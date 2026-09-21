"""Calorie Tracker backend — FastAPI service.

Endpoints:
  GET  /health
  GET  /api/barcode/{code}      OpenFoodFacts lookup, normalized to app schema, SQLite-cached
  POST /api/recipe              {text?, url?, servings?} -> parsed ingredients + totals

Run:  uvicorn app:app --port 8001   (from the backend/ folder)
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from nutrition import NUTRIENTS, analyze_recipe

HERE = Path(__file__).resolve().parent
FOODS_JSON = HERE / "foods.json"
CACHE_DB = HERE / "cache.db"
OFF_FIELDS = ("product_name,brands,quantity,nutriments,"
              "nutriments.energy-kcal_100g,nutriments.proteins_100g,"
              "nutriments.carbohydrates_100g,nutriments.fat_100g,"
              "nutriments.fiber_100g,nutriments.sugars_100g,"
              "nutriments.sodium_100g,nutriments.potassium_100g,"
              "nutriments.calcium_100g,nutriments.iron_100g,"
              "nutriments.vitamin-c_100g,nutriments.vitamin-a_100g")

app = FastAPI(title="Calorie Tracker API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


def load_foods() -> list[dict]:
    if not FOODS_JSON.exists():
        raise RuntimeError("foods.json missing — run: python export_foods.py")
    return json.loads(FOODS_JSON.read_text(encoding="utf-8"))


def _cache_get(code: str) -> dict | None:
    if not CACHE_DB.exists():
        return None
    with sqlite3.connect(CACHE_DB) as c:
        row = c.execute("SELECT payload FROM barcode_cache WHERE code=?", (code,)).fetchone()
    return json.loads(row[0]) if row else None


def _cache_put(code: str, payload: dict) -> None:
    with sqlite3.connect(CACHE_DB) as c:
        c.execute("CREATE TABLE IF NOT EXISTS barcode_cache(code TEXT PRIMARY KEY, payload TEXT)")
        c.execute("INSERT OR REPLACE INTO barcode_cache VALUES (?,?)", (code, json.dumps(payload)))


def _mg(v) -> float:
    return round((v or 0) * 1000, 2)  # OFF vitamins come in grams


def normalize_off(code: str, product: dict) -> dict:
    n = product.get("nutriments", {})
    va = n.get("vitamin-a_100g") or 0
    va_mcg = va * 1e6 if va < 0.1 else 0  # grams -> mcg, ignore absurd values
    food = {"name": product.get("product_name") or f"Product {code}",
            "brand": product.get("brands", ""),
            "quantity": product.get("quantity", ""),
            "cat": "Scanned",
            "kcal": n.get("energy-kcal_100g") or 0,
            "p": n.get("proteins_100g") or 0, "c": n.get("carbohydrates_100g") or 0,
            "f": n.get("fat_100g") or 0, "fib": n.get("fiber_100g") or 0,
            "sug": n.get("sugars_100g") or 0, "na": round((n.get("sodium_100g") or 0) * 1000, 1),
            "k": round((n.get("potassium_100g") or 0) * 1000, 1),
            "ca": round((n.get("calcium_100g") or 0) * 1000, 1),
            "fe": round((n.get("iron_100g") or 0) * 1000, 2),
            "vc": _mg(n.get("vitamin-c_100g")),
            "va": round(min(va_mcg, 10000), 1)}
    for key in ("kcal", "p", "c", "f", "fib", "sug"):
        food[key] = round(food[key] or 0, 2)
    return food


class RecipeIn(BaseModel):
    text: str | None = None
    url: str | None = None
    servings: int | None = None


def _recipe_lines_from_url(url: str) -> tuple[str, int | None]:
    try:
        r = httpx.get(url, timeout=20, follow_redirects=True,
                      headers={"User-Agent": "CalorieTracker/1.0"})
        r.raise_for_status()
    except Exception as e:
        raise HTTPException(400, f"Could not fetch URL: {e}")
    for m in re.finditer(
            r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
            r.text, re.DOTALL | re.IGNORECASE):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        graphs = data if isinstance(data, list) else data.get("@graph", [data])
        for g in graphs:
            types = g.get("@type", "")
            types = [types] if isinstance(types, str) else types
            if "Recipe" in types and g.get("recipeIngredient"):
                yld = None
                ry = g.get("recipeYield")
                if ry:
                    mm = re.search(r"\d+", str(ry[0] if isinstance(ry, list) else ry))
                    yld = int(mm.group()) if mm else None
                return "\n".join(g["recipeIngredient"]), yld
    raise HTTPException(422, "No recipe data (schema.org/Recipe) found — paste the ingredients instead.")


@app.get("/health")
def health():
    return {"ok": True, "foods": len(load_foods())}


@app.get("/api/barcode/{code}")
def barcode(code: str):
    code = re.sub(r"\D", "", code)
    if not (4 <= len(code) <= 14):
        raise HTTPException(400, "Barcode must be 4–14 digits.")
    if (hit := _cache_get(code)) is not None:
        return {**hit, "cached": True}
    try:
        r = httpx.get(f"https://world.openfoodfacts.org/api/v2/product/{code}.json",
                      params={"fields": OFF_FIELDS}, timeout=20,
                      headers={"User-Agent": "CalorieTracker/1.0"})
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        raise HTTPException(502, f"OpenFoodFacts lookup failed: {e}")
    if data.get("status") != 1:
        raise HTTPException(404, "Barcode not found in OpenFoodFacts.")
    food = normalize_off(code, data["product"])
    _cache_put(code, food)
    return {**food, "cached": False}


@app.post("/api/recipe")
def recipe(body: RecipeIn):
    text, servings = body.text or "", body.servings or 1
    if body.url:
        lines, yld = _recipe_lines_from_url(body.url)
        text = lines if not text else text + "\n" + lines
        if body.servings is None and yld:
            servings = yld
    if not text.strip():
        raise HTTPException(400, "Provide 'text' (ingredient lines) or 'url'.")
    return analyze_recipe(text, load_foods(), servings=max(1, servings))

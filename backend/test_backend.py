"""Backend tests: stdlib logic + live API (needs fastapi/httpx installed).

Run:  python test_backend.py          (from the backend/ folder)
"""
import json
import sys
from pathlib import Path

from nutrition import analyze_recipe, match_food, parse_line, to_grams

HERE = Path(__file__).resolve().parent
foods = json.loads((HERE / "foods.json").read_text(encoding="utf-8"))
print(f"DB: {len(foods)} foods")
assert len(foods) > 100, "foods.json incomplete — run export_foods.py first"

# --- parse_line ---
assert parse_line("2 cups rolled oats")["qty"] == 2
assert parse_line("250ml milk")["unit"] == "ml"
assert parse_line("1 1/2 tbsp olive oil")["qty"] == 1.5
assert parse_line("1/2 tsp salt")["qty"] == 0.5
assert parse_line("2x eggs")["unit"] == "x"
assert parse_line("- 3 cloves garlic")["item"] == "garlic"
print("parse_line OK")

# --- to_grams ---
assert to_grams(2, "cups", "rolled oats")[0] == 2 * 240 * 0.38
assert to_grams(1, "kg", "x")[0] == 1000
assert to_grams(2, "x", "eggs")[0] == 100
assert to_grams(1, "can", "chopped tomatoes")[0] == 400
assert to_grams(None, None, "salt")[0] is None
print("to_grams OK")

# --- match_food ---
assert match_food("rolled oats", foods)[0]["name"] == "Oats (dry)"
assert match_food("2 bananas", foods)[0]["name"] == "Banana"
assert match_food("chicken breasts", foods)[0]["name"] == "Chicken breast (grilled)"
assert match_food("xyzzy nonsense", foods)[0] is None
print("match_food OK")

# --- full recipe ---
res = analyze_recipe("2 cups rolled oats\n1 banana\n250 ml whole milk\nServes 2",
                     foods, servings=1)
assert res["servings"] == 2 and not res["unmatched"], res["unmatched"]
assert 800 < res["totals"]["kcal"] < 1100, res["totals"]
assert abs(res["per_serving"]["kcal"] - res["totals"]["kcal"] / 2) < 0.2
print("analyze_recipe OK:", res["totals"]["kcal"], "kcal total /",
      res["per_serving"]["kcal"], "per serving")

# --- live API via TestClient ---
_cache = HERE / "cache.db"
if _cache.exists():
    _cache.unlink()  # start uncached so the cached False/True assertions hold
try:
    from fastapi.testclient import TestClient

    from app import app

    c = TestClient(app)
    assert c.get("/health").json()["foods"] > 100
    r = c.post("/api/recipe", json={"text": "100g oats (dry)\n1 banana"})
    assert r.status_code == 200 and r.json()["totals"]["kcal"] > 400
    b = c.get("/api/barcode/3017620422003")  # Nutella — live OpenFoodFacts
    assert b.status_code == 200, b.text
    nutella = b.json()
    assert 500 < nutella["kcal"] < 600 and nutella["cached"] is False
    assert c.get("/api/barcode/3017620422003").json()["cached"] is True  # cache hit
    assert c.get("/api/barcode/0000").status_code == 404
    print("API OK — Nutella:", nutella["kcal"], "kcal/100g, brand:", nutella["brand"])
except ImportError:
    print("SKIP live API tests (fastapi not installed)", file=sys.stderr)

print("ALL TESTS PASSED")

"""Pure-stdlib nutrition logic: ingredient parsing, unit conversion,
fuzzy food matching and total calculation. No web framework imports,
so this module is unit-testable without FastAPI installed.
"""
from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

NUTRIENTS = ["kcal", "p", "c", "f", "fib", "sug",
             "na", "k", "ca", "fe", "vc", "va"]

FRACTIONS = {"½": 0.5, "¼": 0.25, "¾": 0.75, "⅓": 1 / 3, "⅔": 2 / 3}

MASS_TO_G = {"g": 1, "gram": 1, "grams": 1, "gr": 1,
             "kg": 1000, "mg": 0.001,
             "oz": 28.3495, "ounce": 28.3495, "ounces": 28.3495,
             "lb": 453.592, "lbs": 453.592, "pound": 453.592, "pounds": 453.592}
VOL_TO_ML = {"ml": 1, "milliliter": 1, "milliliters": 1,
             "l": 1000, "liter": 1000, "liters": 1000, "litre": 1000,
             "dl": 100, "cl": 10,
             "tsp": 5, "teaspoon": 5, "teaspoons": 5,
             "tbsp": 15, "tablespoon": 15, "tablespoons": 15, "tbs": 15,
             "cup": 240, "cups": 240, "c": 240,
             "floz": 30, "fl-oz": 30, "fluidounce": 30,
             "pint": 473, "quart": 946}

# g per ml by keyword (fallback 1.0 = water-like)
DENSITY = [("flour", 0.55), ("sugar", 0.85), ("oats", 0.38), ("oatmeal", 0.38),
           ("rice", 0.85), ("oil", 0.92), ("olive", 0.92), ("honey", 1.4),
           ("butter", 0.95), ("milk", 1.03), ("cream", 1.0), ("yogurt", 1.03),
           ("yoghurt", 1.03), ("cocoa", 0.55), ("salt", 1.2)]

# typical grams per countable piece, matched by keyword
PIECE_G = [("egg", 50), ("banana", 118), ("apple", 182), ("orange", 130),
           ("onion", 150), ("garlic", 4), ("lemon", 58), ("lime", 44),
           ("potato", 150), ("tomato", 120), ("carrot", 60), ("avocado", 150),
           ("chicken breast", 170), ("bread", 30), ("toast", 30)]
CAN_G = 400  # standard tin of tomatoes/beans (approx)

COUNT_UNITS = {"piece", "pieces", "pc", "pcs", "x", "clove", "cloves",
               "slice", "slices", "can", "cans", "tin", "tins"}

DESCRIPTORS = {"fresh", "frozen", "chopped", "diced", "sliced", "minced",
               "grated", "crushed", "large", "medium", "small", "ripe",
               "organic", "raw", "cooked", "boiled", "canned", "drained",
               "rinsed", "peeled", "seeded", "boneless", "skinless",
               "softened", "melted", "beaten", "red", "green", "yellow",
               "white", "brown", "black", "whole", "all-purpose"}

SERVES_RE = re.compile(r"serves?\s+(\d+)|servings?\s*[:=]?\s*(\d+)|yield\s*[:=]?\s*(\d+)",
                       re.IGNORECASE)


def _num(tok: str) -> float | None:
    tok = tok.strip()
    if tok in FRACTIONS:
        return FRACTIONS[tok]
    if "/" in tok and tok.count("/") == 1:
        try:
            a, b = tok.split("/")
            return float(a) / float(b)
        except ValueError:
            return None
    try:
        return float(tok)
    except ValueError:
        return None


def parse_line(line: str) -> dict:
    """'2 cups rolled oats' -> {qty, unit, item}. Never raises."""
    # strip one leading bullet / list marker ("-", "•", "1. ", "2) ") — never a quantity
    line = re.sub(r"^\s*(?:[-•*]|\d+[.)])\s+", "", line.strip())
    line = re.sub(r"\(.*?\)", "", line).strip()  # drop '(optional)' notes
    if not line:
        return {"qty": None, "unit": None, "item": ""}
    parts = line.split()
    qty: float | None = None
    rest = parts
    unit = None
    item = " ".join(rest)
    if parts:
        m_x = re.match(r"^(\d+(?:\.\d+)?)x$", parts[0], re.IGNORECASE)
        if m_x:  # '2x eggs'
            return {"qty": float(m_x.group(1)), "unit": "x",
                    "item": " ".join(parts[1:]).strip(" ,")}
    first = _num(parts[0]) if parts else None
    if first is not None:
        qty = first
        rest = parts[1:]
        if len(rest) >= 2:  # mixed number '1 1/2 cups ...'
            second = _num(rest[0])
            if second is not None and second < first * 2 + 2 and qty == int(qty):
                qty += second
                rest = rest[1:]
    # attached unit: '250ml milk', '500g flour'
    if rest:
        m = re.match(r"^([0-9.]+)\s*([a-zA-Z]+)$", parts[0]) if qty is None else None
        if m and _num(m.group(1)) is not None and m.group(2).lower() in (
                set(MASS_TO_G) | set(VOL_TO_ML) | COUNT_UNITS):
            qty = _num(m.group(1))
            unit = m.group(2).lower()
            item = " ".join(parts[1:])
        elif rest and rest[0].lower().rstrip("s,") in (
                set(MASS_TO_G) | set(VOL_TO_ML) | COUNT_UNITS) | {"t", "T"}:
            unit = rest[0].lower()
            if unit == "t":
                unit = "tsp"
            elif unit == "T":
                unit = "tbsp"
            item = " ".join(rest[1:])
        elif rest and rest[0].lower() == "x" and qty is not None:
            unit = "x"
            item = " ".join(rest[1:])
    return {"qty": qty, "unit": unit, "item": item.strip(" ,")}


def _density(item: str) -> float:
    low = item.lower()
    for key, d in DENSITY:
        if key in low:
            return d
    return 1.0


def _piece_g(item: str, unit: str | None) -> float | None:
    low = item.lower()
    if unit in ("can", "cans", "tin", "tins"):
        return CAN_G
    for key, g in PIECE_G:
        if key in low:
            if "clove" in (unit or "") and "garlic" in low:
                return 4
            return g
    return None


def to_grams(qty: float | None, unit: str | None, item: str) -> tuple[float | None, bool]:
    """Returns (grams, approx). None grams = cannot convert."""
    if qty is None:
        return None, True
    u = (unit or "").lower()
    if u in MASS_TO_G:
        return qty * MASS_TO_G[u], False
    if u in VOL_TO_ML:
        return qty * VOL_TO_ML[u] * _density(item), True
    if u in COUNT_UNITS or u is None or u == "":
        g = _piece_g(item, u)
        if g is not None:
            return qty * g, True
        if u in ("", None):
            return qty, True  # bare number -> assume grams
    return None, True


def normalize(text: str) -> str:
    toks = re.sub(r"[^a-z\s]", "", text.lower()).split()
    toks = [t for t in toks if t not in DESCRIPTORS]
    out = []
    for t in toks:  # crude singularization
        if len(t) > 3 and t.endswith("ies"):
            t = t[:-3] + "y"
        elif len(t) > 3 and t.endswith("es") and not t.endswith("ches"):
            t = t[:-1] if t.endswith("ses") else t
        elif len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]
        out.append(t)
    return " ".join(out)


def match_food(item: str, foods: list[dict]) -> tuple[dict | None, float]:
    norm = normalize(item)
    if not norm:
        return None, 0.0
    best, best_s = None, 0.0
    item_toks = set(norm.split())
    for f in foods:
        fn = normalize(f["name"])
        if fn == norm:
            return f, 1.0
        f_toks = set(fn.split())
        if f_toks and (f_toks <= item_toks or item_toks <= f_toks):
            s = 0.9
        else:
            s = SequenceMatcher(None, norm, fn).ratio()
            # token overlap bonus
            if f_toks & item_toks:
                s = max(s, 0.55 + 0.4 * len(f_toks & item_toks) / max(len(f_toks), 1))
        if s > best_s:
            best, best_s = f, s
    return (best, best_s) if best_s >= 0.6 else (None, best_s)


def scale(food: dict, grams: float) -> dict:
    return {n: round(food[n] * grams / 100, 2) for n in NUTRIENTS}


def analyze_recipe(text: str, foods: list[dict], servings: int = 1) -> dict:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    det = SERVES_RE.search(text)
    if det and servings == 1:
        servings = int(next(g for g in det.groups() if g))
    items, unmatched, totals = [], [], {n: 0.0 for n in NUTRIENTS}
    total_g = 0.0
    for ln in lines:
        if SERVES_RE.fullmatch(ln.strip()):
            continue
        p = parse_line(ln)
        food, score = match_food(p["item"], foods)
        grams, approx = to_grams(p["qty"], p["unit"], p["item"])
        if food is None or grams is None:
            unmatched.append({"line": ln, "reason":
                              "no food match" if food is None else "unknown unit/quantity"})
            continue
        nut = scale(food, grams)
        for n in NUTRIENTS:
            totals[n] += nut[n]
        total_g += grams
        items.append({"line": ln, "food": food["name"], "grams": round(grams, 1),
                      "approx": approx or score < 0.85, "nutrients": nut})
    totals = {n: round(v, 1) for n, v in totals.items()}
    per = {n: round(v / servings, 1) for n, v in totals.items()} if servings else totals
    return {"items": items, "unmatched": unmatched,
            "total_grams": round(total_g, 1), "servings": servings,
            "totals": totals, "per_serving": per}

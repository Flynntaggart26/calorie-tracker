"""Export the food database embedded in ../index.html to foods.json.

Single source of truth stays in index.html (FOODS array, per 100 g).
Run:  python export_foods.py   (from the backend/ folder)
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
DST = ROOT / "backend" / "foods.json"

KEYS = ["name", "cat", "kcal", "p", "c", "f", "fib", "sug",
        "na", "k", "ca", "fe", "vc", "va"]

ROW = re.compile(
    r'\["((?:[^"\\]|\\.)*)","((?:[^"\\]|\\.)*)",'
    r'([0-9.\-]+),([0-9.\-]+),([0-9.\-]+),([0-9.\-]+),'
    r'([0-9.\-]+),([0-9.\-]+),([0-9.\-]+),([0-9.\-]+),'
    r'([0-9.\-]+),([0-9.\-]+),([0-9.\-]+),([0-9.\-]+)\]'
)


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    foods = []
    for m in ROW.finditer(text):
        vals = list(m.groups())
        foods.append({
            "name": vals[0], "cat": vals[1],
            **{k: float(v) for k, v in zip(KEYS[2:], vals[2:])},
        })
    if not foods:
        raise SystemExit("No food rows parsed — is FOODS still in index.html?")
    DST.write_text(json.dumps(foods, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Exported {len(foods)} foods -> {DST}")


if __name__ == "__main__":
    main()

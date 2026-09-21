# Calorie Tracker Backend (Python)

Optional [FastAPI](https://fastapi.tiangolo.com/) service that powers two frontend features
in `index.html`: **barcode lookup** and **recipe import**.

| Endpoint | What it does |
|----------|--------------|
| `GET /health` | Status + loaded food count |
| `GET /api/barcode/{code}` | [OpenFoodFacts](https://world.openfoodfacts.org/) lookup, normalized to the app's per-100 g schema, cached in SQLite (`cache.db`) |
| `POST /api/recipe` | `{text?, url?, servings?}` → parses ingredient lines (quantities, fractions, cups/tbsp/tsp/ml/oz, piece weights), fuzzy-matches against the app DB, returns per-ingredient grams + totals + per-serving. URLs are parsed via embedded `schema.org/Recipe` JSON-LD |

## Setup

```bash
cd backend
python export_foods.py      # index.html FOODS array -> foods.json (single source of truth)
pip install -r requirements.txt
uvicorn app:app --port 8001
python test_backend.py      # stdlib logic + live API tests (incl. OpenFoodFacts)
```

Then in the app, set the **Backend API URL** field to `http://localhost:8001`
(stored in `localStorage`; the app degrades gracefully when the backend is offline).

## Files

- `app.py` — FastAPI app (endpoints, OpenFoodFacts client, SQLite cache, recipe-URL fetcher)
- `nutrition.py` — pure-stdlib parsing / unit conversion / fuzzy matching (no framework imports)
- `export_foods.py` — derives `foods.json` from `index.html`
- `test_backend.py` — offline logic tests + live `TestClient` API tests

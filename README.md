# 🔥 Advanced Calorie Tracker

[![Live App](https://img.shields.io/badge/▶_Live_App-Open_Tracker-6C5CFF?style=for-the-badge)](https://flynntaggart26.github.io/calorie-tracker/)
[![Single File](https://img.shields.io/badge/Single_File-index.html-00D9A5?style=flat-square)](#project-structure)
[![No Build](https://img.shields.io/badge/No_Build-Vanilla_JS-FFB800?style=flat-square)](#tech-stack)
[![Offline](https://img.shields.io/badge/Offline-localStorage-4FC3F7?style=flat-square)](#privacy--data)

> An advanced, offline-friendly calorie and nutrient tracker in a **single HTML file**.
> Log meals by weight, hit protein/carb/fat targets derived from your body metrics, and cover
> vitamins, minerals and hydration — with charts, history and CSV export.

### 🚀 Try it now → [flynntaggart26.github.io/calorie-tracker](https://flynntaggart26.github.io/calorie-tracker/)

No install, no account — works out of the box, and your data never leaves your browser. An optional Python backend adds barcode lookup + recipe import.

## Contents

- [Quick start](#quick-start)
- [Features](#features)
- [How targets are calculated](#how-targets-are-calculated)
- [Daily values reference](#daily-values-reference)
- [Screenshots (what you'll see)](#screenshots-what-youll-see)
- [Project structure](#project-structure)
- [Tech stack](#tech-stack)
- [Backend API (Python)](#backend-api-python)
- [Data & methodology](#data--methodology)
- [Privacy & data](#privacy--data)
- [Roadmap](#roadmap)
- [Limitations & disclaimer](#limitations--disclaimer)

## Quick start

| Option | How |
|--------|-----|
| 🌐 **Live app (easiest)** | Open [flynntaggart26.github.io/calorie-tracker](https://flynntaggart26.github.io/calorie-tracker/) — works on desktop and mobile |
| 💻 **Local file** | Download [`index.html`](index.html) and double-click it |
| 🛠️ **Local server** | `python -m http.server` → http://localhost:8000 |

**First 60 seconds:** set age/height/weight/activity/goal → targets auto-calculate → search
"chicken", pick 150 g, add to Dinner → watch macros, micros and remaining kcal update live.

## Features

| Area | Details |
|------|---------|
| 🍎 **Food database (116 items)** | 13 categories — fruits, vegetables, grains, legumes, nuts & seeds, dairy & eggs, meat, fish & seafood, fats & oils, snacks & sweets, fast food, beverages, homemade. Every item carries **12 nutrients per 100 g**: calories, protein, carbs, fat, fiber, sugar, sodium, potassium, calcium, iron, vitamin C, vitamin A |
| 🔍 **Smart logging** | Live search, category filter, sort by name / calories / protein, portion presets (50/100/150/250 g) or exact grams, 4 meals (Breakfast, Lunch, Dinner, Snacks), per-item macro breakdown, one-click delete |
| 🎯 **Personal targets** | BMR via **Mifflin-St Jeor**, TDEE via activity multiplier, goal adjustment (cut → bulk). Auto macro split: protein ~1.7–2.0 g/kg, fat 25 % of kcal, remainder carbs. Water target 35 ml/kg |
| 🧬 **Vital nutrients vs Daily Value** | Fiber 30 g · sugar < 50 g · sodium < 2300 mg · potassium 3500 mg · calcium 1000 mg · iron 18 mg · vitamin C 90 mg · vitamin A 900 mcg — live % bars plus a totals table with ✅ Hit / 🟡 Half / ⚠️ Over status |
| 📊 **Analytics** | Macro donut (energy split), calories-by-meal bar, 7-day calorie history vs target, weight log, hydration progress |
| ➕ **Custom foods** | Add your own dishes (per 100 g) — saved in the browser and loggable like built-ins |
| 💧 **Hydration** | One-tap 250/330/500 ml logging with % of daily target |
| ⚖️ **Weight log** | Track body weight alongside calories to see the trend against your goal |
| 💾 **Persistence & export** | Everything in `localStorage` (daily log, water, profile, weights, history). One-click **CSV export** of the day's log |
| 🌗 **Theme** | Dark / light mode, responsive down to phones |
| 🔌 **Barcode + recipe import** | Optional `backend/` Python service: scan packaged-food barcodes (OpenFoodFacts, cached) and paste ingredient lists or recipe URLs — auto-matched nutrition with one-click dish logging |

## How targets are calculated

- **BMR (Mifflin-St Jeor):** men `10·w + 6.25·h − 5·a + 5`, women `10·w + 6.25·h − 5·a − 161`
  (w = kg, h = cm, a = years)
- **TDEE:** BMR × activity (1.2 sedentary → 1.9 athlete)
- **Target kcal:** TDEE + goal (−500 cut … +500 bulk)
- **Protein:** 2.0 g/kg on a cut, 1.8 g/kg maintain, 1.7 g/kg gain · **Fat:** 25 % of kcal ÷ 9 ·
  **Carbs:** remaining kcal ÷ 4

## Daily values reference

| Nutrient | Daily value | Why it matters |
|----------|-------------|----------------|
| Calories | Target from profile | Fuel for the body — balance intake vs TDEE for goal weight |
| Protein | ~1.7–2.2 g/kg | Muscle, satiety, recovery |
| Carbs | ~45–55 % kcal | Main energy source, brain fuel |
| Fat | ~25 % kcal | Hormones, absorption of vitamins A/D/E/K |
| Fiber | 30 g | Gut health, fullness, blood sugar |
| Sugar (added) | < 50 g | Limit — excess drives fat gain and energy crashes |
| Sodium | < 2300 mg | Limit — excess raises blood pressure |
| Potassium | 3500 mg | Blood pressure, muscle function |
| Calcium | 1000 mg | Bones, teeth, muscle signaling |
| Iron | 18 mg | Oxygen transport — deficiency = fatigue |
| Vitamin C | 90 mg | Immunity, iron absorption, skin |
| Vitamin A | 900 mcg | Vision, immunity |

## Screenshots (what you'll see)

> Text tour — open the [live app](https://flynntaggart26.github.io/calorie-tracker/) to see it in action.

1. **Profile & targets** — BMR, TDEE, target kcal, water goal and macro split in grams/day.
2. **Today dashboard** — eaten vs remaining kcal, progress bar, macro donut, calories-by-meal
   chart, macro bars and 7 micronutrient gauges.
3. **Food database** — searchable, filterable list with full per-100 g nutrition on every row.
4. **Daily log + analytics** — meals grouped with kcal subtotals, hydration tracker, 7-day
   history chart, weight log and a totals table with Hit/Half/Over status per nutrient.

## Project structure

```
calorie-tracker/
├── index.html    # The entire app (markup + styles + 116-food DB + logic)
├── backend/      # Optional Python API: barcode lookup + recipe import
│   ├── app.py            # FastAPI endpoints, OpenFoodFacts client, SQLite cache
│   ├── nutrition.py      # stdlib-only parsing / units / fuzzy matching
│   ├── export_foods.py   # index.html FOODS array -> foods.json
│   ├── foods.json        # generated DB snapshot (regenerate after FOODS edits)
│   ├── test_backend.py   # offline logic + live API tests
│   └── requirements.txt
├── README.md     # This file
└── .gitignore    # OS / editor noise
```

Everything lives in `index.html`: the `FOODS` array is the database, `targets()` computes goals,
`render()` redraws dashboard + charts, and `save()` persists to `localStorage`.
The `backend/` service is strictly optional — the app degrades gracefully when it is offline.

## Tech stack

Vanilla HTML/CSS/JS + Chart.js 4 (CDN) for the app — no framework, no build step, easy to audit,
fork and host anywhere (GitHub Pages serves this repo's `index.html` as the live app).
Optional Python backend: FastAPI + httpx + SQLite (`backend/`, see [Backend API](#backend-api-python)).

## Backend API (Python)

Optional service in [`backend/`](backend/) — the app works fully without it
(the Barcode & recipe panel shows "backend offline" and everything else keeps working).

| Endpoint | What it does |
|----------|--------------|
| `GET /health` | Status + loaded food count |
| `GET /api/barcode/{code}` | OpenFoodFacts lookup normalized to the app's per-100 g schema, cached in SQLite |
| `POST /api/recipe` | `{text?, url?, servings?}` — parses ingredient lines (quantities, fractions, cups/tbsp/tsp/ml/oz, piece weights), fuzzy-matches against the app DB, returns per-ingredient grams + totals + per-serving. URLs are read via embedded `schema.org/Recipe` JSON-LD |

```bash
cd backend
python export_foods.py        # index.html FOODS array -> foods.json (single source of truth)
pip install -r requirements.txt
uvicorn app:app --port 8001
python test_backend.py        # offline logic + live API tests
```

Then set the **Backend API URL** field in the app to `http://localhost:8001` (saved in
`localStorage`). Details in [`backend/README.md`](backend/README.md).

## Data & methodology

Nutrient values are USDA-based approximations per 100 g edible portion, embedded directly in the file —
the app works fully offline (except the Chart.js CDN). Packaged and restaurant items vary by brand and
preparation; mixed/fast-food micronutrients are estimates. For medical-precision needs, check the label.

## Privacy & data

All data (food log, water, profile, custom foods, weights, history) is stored in your browser's
`localStorage` — per device, per browser. Nothing is uploaded anywhere by the app itself.
(The optional barcode/recipe backend only contacts OpenFoodFacts — or a recipe URL you paste —
when you explicitly use those buttons.) Clearing browser site data erases it, so use CSV export for records you want to keep.

## Roadmap

- [ ] Vitamin D, B12, magnesium, zinc tracking
- [x] Barcode / packaged-food label quick entry (via `backend/` + OpenFoodFacts)
- [x] Recipe import — paste ingredients or a recipe URL (via `backend/`)
- [ ] Recipe builder v2 (combine saved dishes, per-ingredient editing in-app)
- [ ] Weekly averages + streaks
- [ ] PWA install + true offline (service worker) so charts work without network
- [ ] Import/export full backup JSON

Ideas and pull requests welcome — open an issue first to discuss.

## Limitations & disclaimer

- Estimates, **not medical advice** — consult a professional for clinical goals, eating disorders,
  pregnancy, or medication-affected nutrition needs
- Vitamin D, B12, magnesium and zinc are not yet tracked per food
- History/weights live in browser `localStorage` (per device, per browser)

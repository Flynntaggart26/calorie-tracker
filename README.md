# 🔥 Advanced Calorie Tracker

> An advanced, offline-friendly calorie and nutrient tracker in a **single HTML file**.
> Log meals by weight, hit protein/carb/fat targets derived from your body metrics, and cover
> vitamins, minerals and hydration — with charts, history and CSV export.

Just open [`calorie-tracker.html`](calorie-tracker.html) in any modern browser. No framework, no build
step, no backend, no account.

## Features

| Area | Details |
|------|---------|
| 🍎 **Food database (120+ items)** | 13 categories — fruits, vegetables, grains, legumes, nuts & seeds, dairy & eggs, meat, fish & seafood, fats & oils, snacks & sweets, fast food, beverages, homemade. Every item carries **12 nutrients per 100 g**: calories, protein, carbs, fat, fiber, sugar, sodium, potassium, calcium, iron, vitamin C, vitamin A |
| 🔍 **Smart logging** | Live search, category filter, sort by name / calories / protein, portion presets (50/100/150/250 g) or exact grams, 4 meals (Breakfast, Lunch, Dinner, Snacks), per-item macro breakdown, one-click delete |
| 🎯 **Personal targets** | BMR via **Mifflin-St Jeor**, TDEE via activity multiplier, goal adjustment (cut → bulk). Auto macro split: protein ~1.7–2.0 g/kg, fat 25 % of kcal, remainder carbs. Water target 35 ml/kg |
| 🧬 **Vital nutrients vs Daily Value** | Fiber 30 g · sugar < 50 g · sodium < 2300 mg · potassium 3500 mg · calcium 1000 mg · iron 18 mg · vitamin C 90 mg · vitamin A 900 mcg — live % bars plus a totals table with ✅ Hit / 🟡 Half / ⚠️ Over status |
| 📊 **Analytics** | Macro donut (energy split), calories-by-meal bar, 7-day calorie history vs target, weight log, hydration progress |
| ➕ **Custom foods** | Add your own dishes (per 100 g) — saved in the browser and loggable like built-ins |
| 💾 **Persistence & export** | Everything in `localStorage` (daily log, water, profile, weights, history). One-click **CSV export** of the day's log |
| 🌗 **Theme** | Dark / light mode |

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

## Data & methodology

Nutrient values are USDA-based approximations per 100 g edible portion, embedded directly in the file —
the app works fully offline (except the Chart.js CDN). Packaged and restaurant items vary by brand and
preparation; mixed/fast-food micronutrients are estimates. For medical-precision needs, check the label.

## Run it

```bash
# Option 1: just double-click calorie-tracker.html
# Option 2: serve the folder
python -m http.server  # → http://localhost:8000/calorie-tracker.html
```

## Tech

Vanilla HTML/CSS/JS + Chart.js 4 via CDN. Single auditable file (~31 KB).

## Limitations

- Estimates, not medical advice — consult a professional for clinical goals
- Vitamin D, B12, magnesium and zinc are not yet tracked per food
- History/weights live in browser `localStorage` (per device, per browser)

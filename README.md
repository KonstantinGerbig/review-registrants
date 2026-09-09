# review-registrants

Scripts to sort, tier, and prepare a review sheet from conference registrant Google Form CSV exports.
Based on experience organizing ERES 2023 and the AI+Science Summer School 2026.

**All sensitive data lives in `data/` (gitignored).** The committed code is the method only.

---

## Repo structure

```
review-registrants/
├── CLAUDE.md
├── sort_registrants.py     ← Deduplicates, tiers, and adds reviewer columns
├── plot_registrants.py     ← Overview charts
├── render_abstracts.py     ← Renders all submissions as formatted markdown
├── defaults/
│   ├── config.py           ← Template — copy to data/config.py
│   └── tier_rules.py       ← Template — copy to data/tier_rules.py
└── data/                   ← GITIGNORED — create this yourself
    ├── raw/                ← Drop Google Form CSV export here
    ├── config.py           ← Copied from defaults/, filled in
    ├── tier_rules.py       ← Copied from defaults/, filled in
    └── outputs/
        └── plots/
```

---

## Setup for a new conference

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create the data layout
```bash
mkdir -p data/raw data/outputs/plots
cp defaults/config.py data/config.py
cp defaults/tier_rules.py data/tier_rules.py
```

### 3. Drop the Google Form CSV
Export from Google Sheets → File → Download → CSV. Place the file in `data/raw/`.
The scripts auto-detect any `.csv` file there.

If a person submitted the form multiple times (e.g. to correct an answer), only their
**last** submission is kept — Google Forms appends rows chronologically, so `keep="last"`
on the email column always retains the most recent entry.

### 4. Edit `data/config.py`
- **`COLUMNS`** — paste the exact header strings from your CSV for `email`, `name`, `institution`, `position`. For long question headers, leave the entry `None` and check that `COLUMN_PARTIAL_MATCH` has a substring that matches.
- **`N_REVIEWERS`** — number of reviewer slots (default 2).
- **`PIE_COLUMNS`** — uncomment or add entries for columns you want as pie charts in the dashboard.
- **`INSTITUTION_GROUPS`** — optionally group institutions into categories for the plot.

### 5. Edit `data/tier_rules.py`
Uncomment and fill in rules for Tiers I, II, and IV. Registrants that match no rule default to Tier III.

Available rule types (documented in the file):
- `email_list` — list of email addresses
- `name_list` — list of full names
- `name_csv` — path to a CSV with `first_name`, `last_name` columns
- `institution_contains` — case-insensitive substring of institution name
- `field_empty` — flags registrants who left a specific field blank (good for Tier IV)

Rules are evaluated in order; first match wins.

### 6. Run
```bash
python sort_registrants.py    # → data/outputs/review_sheet.csv + summary.txt
python plot_registrants.py    # → data/outputs/plots/*.png
python render_abstracts.py    # → data/outputs/abstracts.md  (requires review_sheet first)
```

---

## Output

`sort_registrants.py` produces:
- **`review_sheet.csv`** — all unique registrants sorted by tier (I → IV), with empty
  `Reviewer N Name / Grade / Notes` columns ready to be filled in.
- **`summary.txt`** — counts per tier.

`plot_registrants.py` produces:
- **`overview_dashboard.png`** — position bar chart, entry counts, tier distribution,
  and any pie charts configured in `PIE_COLUMNS`.
- **`institutions_and_fields.png`** — institution and research field breakdowns.

`render_abstracts.py` produces:
- **`abstracts.md`** — all submissions rendered as markdown, grouped by tier. Each entry
  shows name, institution, position, and all form fields. Long free-text answers are
  formatted as blockquotes. Reviewer columns are omitted.

---

## Tier system

| Tier | Label | Meaning |
|------|-------|---------|
| I | Whitelisted | Guaranteed acceptance |
| II | Preferred | Strong candidates, reviewed before III |
| III | Normal | Standard pool (default) |
| IV | Blacklisted / Incomplete | Placed at bottom; flag for rejection or follow-up |

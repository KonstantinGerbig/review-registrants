# review-registrants

Scripts to sort, tier, and prepare a review sheet from conference registrant Google Form CSV exports.
Based on experience organizing ERES 2023 and the AI+Science Summer School 2026.

**All sensitive data lives in `data/` (gitignored).** The committed code is the method only.

---

## Repo structure

```
review-registrants/
├── CLAUDE.md
├── sort_registrants.py     ← Deduplicates, tiers, reconciles columns, builds review sheet
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

- **`COLUMNS`** — paste the exact header string from your CSV for each key (`email`,
  `name`, `institution`, `position`, `timestamp`, etc.). For long question headers leave
  the value as `None` and rely on `COLUMN_PARTIAL_MATCH` instead.
- **`COLUMN_PARTIAL_MATCH`** — case-insensitive substrings used to find columns whose
  exact header isn't set in `COLUMNS`.
- **`N_REVIEWERS`** — number of reviewer slots added to the review sheet (default 2).
- **`COLUMN_RECONCILIATIONS`** — optional list of derived columns. Each entry reads a
  source column and maps its values to canonical labels via `exact_map` (exact string
  match) then `keyword_rules` (case-insensitive substring). Useful for normalising messy
  dropdown answers (e.g. career stage).
- **`OUTPUT_COLUMNS`** — controls the column order in `review_sheet.csv`. Uses special
  tokens (`__decision__`, `__average_score__`, `__applicant_num__`, `__tier__`,
  `__reviewers__`, `__remaining__`) plus any `COLUMNS` key or exact header string.
  Omit entirely to use the default order.
- **`PIE_COLUMNS`** — columns to show as pie charts in the overview dashboard.
- **`INSTITUTION_GROUPS`** — optional grouping of institution names for plots.

### 5. Edit `data/tier_rules.py`
Fill in rules for whichever tiers apply. Registrants that match no rule default to **Tier III**.

Available match types (all documented inside the file):

| Match type | What it checks |
|---|---|
| `email_list` | registrant's email is in a list |
| `name_list` | registrant's full name is in a list (case-insensitive) |
| `name_csv` | registrant's name appears in a CSV with `first_name`, `last_name` columns |
| `institution_contains` | institution name contains a substring (case-insensitive) |
| `field_empty` | a given field is blank — useful for Tier V (incomplete submissions) |
| `field_contains` | a given field's value contains a substring — useful for specific answers (e.g. "No" to poster question) |
| `timestamp_after` | submission timestamp is after a given date (`YYYY-MM-DD`) — useful for Tier IV (late submissions) |

Rules are evaluated in order; first match wins. Put higher-priority tiers (I, II) before
lower-priority ones (IV, V) so that a whitelisted person who submitted late still lands
in Tier I, not Tier IV.

### 6. Run
```bash
python sort_registrants.py    # → data/outputs/review_sheet.csv + summary.txt
python plot_registrants.py    # → data/outputs/plots/*.png
python render_abstracts.py    # → data/outputs/abstracts.md  (requires review_sheet first)
```

---

## Output

`sort_registrants.py` produces:
- **`review_sheet.csv`** — all unique registrants sorted by tier (I → V), with empty
  `Decision`, `Average Score`, and `Reviewer N Name / Grade / Notes` columns ready to
  be filled in. Column order is controlled by `OUTPUT_COLUMNS` in `data/config.py`.
- **`summary.txt`** — registrant counts per tier.

`plot_registrants.py` produces:
- **`overview_dashboard.png`** — career stage bar chart, entry counts, tier distribution,
  and any pie charts configured in `PIE_COLUMNS`. Reads from `review_sheet.csv` if it
  exists (to get reconciled columns), otherwise reads the raw CSV.
- **`institutions_and_fields.png`** — institution and research field breakdowns.

`render_abstracts.py` produces:
- **`abstracts.md`** — all submissions rendered as markdown, grouped by tier. Each entry
  shows name, institution, position, and all form fields. Long free-text answers are
  formatted as blockquotes. Reviewer and decision columns are omitted.

---

## Tier system

| Tier | Label | Default meaning |
|------|-------|-----------------|
| I | Whitelisted | Guaranteed consideration — reviewed first |
| II | Preferred | Strong candidates — reviewed before Tier III |
| III | Normal | Standard pool — default for all unmatched registrants |
| IV | Late Submission | Submitted after the deadline |
| V | No Poster / Incomplete | Did not commit to a poster, or left required fields blank |

Tiers are assigned by rules in `data/tier_rules.py`. The labels and meanings above are
conventions — you can repurpose any tier for your conference's needs by adjusting the
rules and labels in `sort_registrants.py`.

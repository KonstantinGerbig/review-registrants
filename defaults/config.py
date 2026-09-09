"""
defaults/config.py — Template configuration for a new conference.

Copy this file to  data/config.py  and edit it there.
data/ is gitignored, so your column names and settings stay local.
"""

# ── Column mappings ────────────────────────────────────────────────────────────
# Set each value to the exact header string in your Google Form CSV.
# Leave a value as None to use the partial-match fallback below instead.

COLUMNS = {
    "email":        "Email",
    "name":         "Name",
    "institution":  "Institution",
    "position":     "Position",        # e.g. "Position:", "Career Stage"
    "research_area": None,             # set if your form has a research field question
    "why_joining":  None,              # set or rely on partial match below
}

# Substring searched (case-insensitive) in column headers when COLUMNS[key] is None.
COLUMN_PARTIAL_MATCH = {
    "why_joining":  "why",             # adjust to match your form's question wording
    "research_area": "research",
}

# ── Reviewer columns ───────────────────────────────────────────────────────────
# Number of reviewer slots added to the output CSV.
N_REVIEWERS = 2

# ── Pie chart columns for plot_registrants.py ─────────────────────────────────
# List of (field_key, plot_title, kind) tuples.
#   field_key — key from COLUMNS / COLUMN_PARTIAL_MATCH
#   plot_title — label shown on the chart
#   kind — "pie"    : one slice per unique answer value
#           "filled": binary — did the person fill this field in or not
#
# Leave empty to skip the pie row entirely.
PIE_COLUMNS = [
    # ("expertise",    "Level of Expertise",   "pie"),
    # ("poster",       "Present a Poster?",     "pie"),
    # ("why_joining",  "Reason Provided?",      "filled"),
]

# ── Column reconciliations (optional) ─────────────────────────────────────────
# Create new derived columns by mapping/bucketing existing column values.
# Each entry produces one new column in the output CSV and review sheet.
#
# source_key    — key from COLUMNS / COLUMN_PARTIAL_MATCH to read from
# output_name   — name of the new column to add
# exact_map     — dict: raw value (exact, case-sensitive) → output value;
#                 applied first
# keyword_rules — list of (output_value, [keywords]) for values not matched
#                 by exact_map; case-insensitive substring; first match wins
# default       — value when nothing matches (omit to keep the raw value)
COLUMN_RECONCILIATIONS = [
    # {
    #     "source_key":  "position",
    #     "output_name": "Career Stage",
    #     "exact_map": {
    #         "Exact Dropdown Value 1": "Canonical Label A",
    #         "Exact Dropdown Value 2": "Canonical Label B",
    #     },
    #     "keyword_rules": [
    #         ("Canonical Label A", ["keyword1", "keyword2"]),
    #         ("Canonical Label B", ["keyword3"]),
    #     ],
    #     "default": "Other",
    # },
]

# ── Output column order ───────────────────────────────────────────────────────
# Controls the column order in review_sheet.csv.
# Omit this entirely to use the default order.
#
# Special tokens:
#   __decision__      — empty "Decision" column (accept / waitlist / reject)
#   __average_score__ — empty "Average Score" column
#   __applicant_num__ — "Applicant #"
#   __tier__          — "Tier"
#   __reviewers__     — all reviewer columns (N_REVIEWERS × Name / Grade / Notes)
#   __remaining__     — every column not yet placed, in original form order
#
# Any key from COLUMNS / COLUMN_PARTIAL_MATCH, or an exact column header string,
# can also be placed by name (e.g. "name", "funding?").
#
# OUTPUT_COLUMNS = [
#     "__decision__",
#     "__average_score__",
#     "__applicant_num__",
#     "name",
#     "funding?",
#     "__reviewers__",
#     "__remaining__",
# ]

# ── Institution grouping for plots (optional) ──────────────────────────────────
# If defined, institutions are bucketed into these groups for the bar chart.
# Each entry is (group_label, [list of case-insensitive substrings]).
# First match wins; unmatched → "Other".
# Leave as empty list to show raw institution names (top N) instead.
INSTITUTION_GROUPS = [
    # ("Home Institution", ["your university name", "your uni abbrev"]),
    # ("Partner Schools",  ["school a", "school b"]),
    # ("International",    ["keyword1", "keyword2"]),
]

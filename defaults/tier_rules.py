"""
defaults/tier_rules.py — Template tier-assignment rules.

Copy this file to  data/tier_rules.py  and edit it there.
data/ is gitignored, so your lists and rules stay local.

Rules are evaluated in order; the first matching rule wins.
Registrants that match no rule are assigned Tier III (Normal).

── Tier meanings ──────────────────────────────────────────────────────────────

  Tier I   Whitelisted          — reviewed first, guaranteed consideration
  Tier II  Preferred            — strong candidates, reviewed before III
  Tier III Normal               — standard pool (default for unmatched)
  Tier IV  Late Submission      — submitted after the deadline
  Tier V   No Poster/Incomplete — did not commit to a poster or left fields blank

── Available match types ──────────────────────────────────────────────────────

  email_list          emails: [...]
                      Matches if the registrant's email is in the list.

  name_list           names: [...]
                      Matches if the registrant's full name (case-insensitive)
                      is in the list. Format: "First Last".

  name_csv            csv_path: "data/special/fellows.csv"
                      CSV with columns  first_name, last_name.
                      Matches if the registrant's name appears in the file.

  institution_contains  value: "substring"
                      Matches if the registrant's institution (case-insensitive)
                      contains the substring.

  field_empty         field_key: "why_joining"
                      Matches if the field (key from COLUMNS/COLUMN_PARTIAL_MATCH)
                      is blank or missing.

  field_contains      field_key: "poster?"   value: "No"
                      Matches if the field value contains the given substring
                      (case-insensitive). Useful for checking specific answers.

  timestamp_after     timestamp_key: "timestamp"   date: "YYYY-MM-DD"
                      Matches if the submission timestamp is after the given date.
                      Requires "timestamp" (or the given key) in COLUMNS.
"""

TIER_RULES = [

    # ── Tier I: Whitelisted ───────────────────────────────────────────────────
    # {
    #     "tier":  "I",
    #     "match": "name_list",
    #     "names": [
    #         "Jane Doe",
    #     ],
    # },
    # {
    #     "tier":  "I",
    #     "match": "name_csv",
    #     "csv_path": "data/special/vip_list.csv",   # first_name, last_name columns
    # },

    # ── Tier II: Preferred ────────────────────────────────────────────────────
    # {
    #     "tier":  "II",
    #     "match": "institution_contains",
    #     "value": "partner school",
    # },
    # {
    #     "tier":  "II",
    #     "match": "name_list",
    #     "names": ["Jane Doe", "John Smith"],
    # },

    # ── Tier IV: Late submission ──────────────────────────────────────────────
    # {
    #     "tier":          "IV",
    #     "match":         "timestamp_after",
    #     "timestamp_key": "timestamp",
    #     "date":          "2025-08-28",
    # },

    # ── Tier V: No poster / incomplete ───────────────────────────────────────
    # {
    #     "tier":      "V",
    #     "match":     "field_contains",
    #     "field_key": "poster?",
    #     "value":     "No",
    # },
    # {
    #     "tier":      "V",
    #     "match":     "field_empty",
    #     "field_key": "why_joining",
    # },

]

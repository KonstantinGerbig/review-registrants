"""
defaults/tier_rules.py — Template tier-assignment rules.

Copy this file to  data/tier_rules.py  and edit it there.
data/ is gitignored, so your lists and rules stay local.

Rules are evaluated in order; the first matching rule wins.
Registrants that match no rule are assigned Tier III (Normal).

── Recommended ordering ───────────────────────────────────────────────────────

  Put Tier V (incomplete) rules FIRST.  Because first-match wins, this ensures
  submissions with missing required fields are always marked incomplete —
  even if the person would otherwise qualify for Tier I or II.  Add all other
  rules after the completeness checks.

── Tier meanings ──────────────────────────────────────────────────────────────

  Tier I   Whitelisted          — reviewed first, guaranteed consideration
  Tier II  Preferred            — strong candidates, reviewed before III
  Tier III Normal               — standard pool (default for unmatched)
  Tier IV  Late Submission      — submitted after the deadline
  Tier V   Incomplete           — missing required fields or opted out

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

  field_empty         field_key: "abstract"
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

    # ── Tier V: Incomplete — evaluated FIRST ─────────────────────────────────
    # Place all completeness/eligibility checks here so they override any
    # higher-tier rule that would otherwise match the same person.
    #
    # Missing required field (e.g. abstract):
    # {
    #     "tier":      "V",
    #     "match":     "field_empty",
    #     "field_key": "abstract",        # key from COLUMNS / COLUMN_PARTIAL_MATCH
    # },
    #
    # Opted out of required component (e.g. poster):
    # {
    #     "tier":      "V",
    #     "match":     "field_contains",
    #     "field_key": "poster?",
    #     "value":     "No",
    # },

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

]

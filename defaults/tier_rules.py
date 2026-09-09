"""
defaults/tier_rules.py — Template tier-assignment rules.

Copy this file to  data/tier_rules.py  and edit it there.
data/ is gitignored, so your lists and rules stay local.

Rules are evaluated in order; the first matching rule wins.
Registrants that match no rule are assigned Tier III (Normal).

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
                      Matches if the registrant's institution name (case-insensitive)
                      contains the given substring.

  field_empty         field_key: "why_joining"
                      Matches if the given field (key from COLUMNS) is blank.
                      Useful for flagging incomplete submissions as Tier IV.
"""

TIER_RULES = [
    # ── Tier I: Whitelisted ────────────────────────────────────────────────────
    # Guaranteed acceptance. Examples:
    # {
    #     "tier": "I",
    #     "match": "email_list",
    #     "emails": [
    #         "vip@institution.edu",
    #     ],
    # },
    # {
    #     "tier": "I",
    #     "match": "name_csv",
    #     "csv_path": "data/special/vip_list.csv",   # first_name, last_name columns
    # },
    # {
    #     "tier": "I",
    #     "match": "institution_contains",
    #     "value": "home university name",
    # },

    # ── Tier II: Preferred ─────────────────────────────────────────────────────
    # Strong candidates, reviewed before Tier III.
    # {
    #     "tier": "II",
    #     "match": "institution_contains",
    #     "value": "partner school",
    # },
    # {
    #     "tier": "II",
    #     "match": "name_list",
    #     "names": [
    #         "Jane Doe",
    #         "John Smith",
    #     ],
    # },

    # ── Tier IV: Blacklisted / Incomplete ─────────────────────────────────────
    # Placed at the bottom of the review sheet.
    # Flag registrants who left the motivation field blank:
    # {
    #     "tier": "IV",
    #     "match": "field_empty",
    #     "field_key": "why_joining",
    # },
    # {
    #     "tier": "IV",
    #     "match": "email_list",
    #     "emails": [
    #         "known_spammer@domain.com",
    #     ],
    # },
]

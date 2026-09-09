"""
render_abstracts.py — Render all submissions as a formatted markdown document.

Reads:  data/outputs/review_sheet.csv  (produced by sort_registrants.py)
        data/config.py

Writes: data/outputs/abstracts.md

Registrants are grouped by tier. Reviewer columns and internal columns are
omitted — only the original form fields are shown.
"""

import os
import sys
import pandas as pd

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(REPO_DIR, "data")
OUT_DIR   = os.path.join(DATA_DIR, "outputs")

sys.path.insert(0, DATA_DIR)
try:
    import config
except ImportError:
    print("ERROR: data/config.py not found.")
    print("  → cp defaults/config.py data/config.py  then fill it in.")
    sys.exit(1)


# ── Load review sheet ─────────────────────────────────────────────────────────

sheet_path = os.path.join(OUT_DIR, "review_sheet.csv")
if not os.path.exists(sheet_path):
    print("ERROR: data/outputs/review_sheet.csv not found.")
    print("  → Run sort_registrants.py first.")
    sys.exit(1)

df = pd.read_csv(sheet_path)

TIER_ORDER = ["I", "II", "III", "IV", "V"]

# Columns to skip in the rendered output
reviewer_cols = {c for c in df.columns if c.startswith("Reviewer ")}
skip_cols = reviewer_cols | {"Applicant #", "Tier"}


# ── Resolve column names for header fields ────────────────────────────────────

def resolve_column(df, key):
    exact = config.COLUMNS.get(key)
    if exact and exact in df.columns:
        return exact
    pattern = config.COLUMN_PARTIAL_MATCH.get(key, "").lower()
    if pattern:
        matches = [c for c in df.columns if pattern in c.lower()]
        if matches:
            return matches[0]
    return None

name_col      = resolve_column(df, "name")
email_col     = resolve_column(df, "email")
inst_col      = resolve_column(df, "institution")
position_col  = resolve_column(df, "position")

# These four are shown in a compact header line; the rest get bullet-listed below
header_fields = {c for c in [name_col, email_col, inst_col, position_col] if c}


# ── Render ────────────────────────────────────────────────────────────────────

lines = ["# Submissions\n"]

for tier in TIER_ORDER:
    tier_df = df[df["Tier"] == tier]
    if tier_df.empty:
        continue

    lines.append(f"---\n\n## Tier {tier}  ({len(tier_df)} registrants)\n")

    for _, row in tier_df.iterrows():
        app_num  = row.get("Applicant #", "?")
        name     = row.get(name_col, "Unknown") if name_col else "Unknown"
        email    = row.get(email_col, "") if email_col else ""
        inst     = row.get(inst_col, "") if inst_col else ""
        position = row.get(position_col, "") if position_col else ""

        # Compact identity line
        meta_parts = [p for p in [inst, position] if pd.notna(p) and str(p).strip()]
        meta_str   = "  ·  ".join(str(p).strip() for p in meta_parts)
        email_str  = f"  <{str(email).strip()}>" if pd.notna(email) and str(email).strip() else ""

        lines.append(f"### #{app_num}: {name}{email_str}")
        if meta_str:
            lines.append(f"*{meta_str}*\n")
        else:
            lines.append("")

        # All remaining form fields as labelled bullets
        for col in df.columns:
            if col in skip_cols or col in header_fields:
                continue
            val = row[col]
            if pd.isna(val) or str(val).strip() == "":
                continue
            # Use a blockquote for long free-text answers (> 80 chars)
            text = str(val).strip()
            if len(text) > 80:
                indented = "\n> ".join(text.splitlines())
                lines.append(f"**{col}**\n> {indented}\n")
            else:
                lines.append(f"- **{col}:** {text}")

        lines.append("\n")

out_path = os.path.join(OUT_DIR, "abstracts.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Saved: {out_path}  ({len(df)} entries across {df['Tier'].nunique()} tiers)")

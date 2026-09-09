"""
sort_registrants.py — Deduplicate, tier-sort, and prepare review sheet.

Reads:  data/raw/<form>.csv
        data/config.py       (copy from defaults/config.py)
        data/tier_rules.py   (copy from defaults/tier_rules.py)

Writes: data/outputs/review_sheet.csv
        data/outputs/summary.txt
"""

import os
import sys
import pandas as pd

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(REPO_DIR, "data")
RAW_DIR   = os.path.join(DATA_DIR, "raw")
OUT_DIR   = os.path.join(DATA_DIR, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load config & tier rules ──────────────────────────────────────────────────

sys.path.insert(0, DATA_DIR)

try:
    import config
except ImportError:
    print("ERROR: data/config.py not found.")
    print("  → cp defaults/config.py data/config.py  then fill it in.")
    sys.exit(1)

try:
    import tier_rules as tier_rules_mod
except ImportError:
    print("ERROR: data/tier_rules.py not found.")
    print("  → cp defaults/tier_rules.py data/tier_rules.py  then fill it in.")
    sys.exit(1)

RULES = tier_rules_mod.TIER_RULES
N_REVIEWERS = getattr(config, "N_REVIEWERS", 2)


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def preprocess_rules(rules):
    """Expand name_csv rules by loading the CSV once and converting to name_list."""
    processed = []
    for rule in rules:
        if rule.get("match") == "name_csv":
            csv_path = os.path.join(REPO_DIR, rule["csv_path"])
            if os.path.exists(csv_path):
                ref = pd.read_csv(csv_path)
                names = (
                    ref["first_name"].fillna("").str.strip() + " " +
                    ref["last_name"].fillna("").str.strip()
                ).str.lower().tolist()
                processed.append({**rule, "match": "name_list", "names": names})
            else:
                print(f"WARNING: CSV not found for name_csv rule: {csv_path} — skipping rule.")
        else:
            processed.append(rule)
    return processed


RECONCILIATIONS = getattr(config, "COLUMN_RECONCILIATIONS", [])


def apply_reconciliation(val, rec):
    """Map a single raw value using exact_map then keyword_rules."""
    raw = str(val).strip() if pd.notna(val) else ""
    if raw in rec.get("exact_map", {}):
        return rec["exact_map"][raw]
    search = raw.lower()
    if search:
        for output_val, keywords in rec.get("keyword_rules", []):
            if any(kw.lower() in search for kw in keywords):
                return output_val
    return rec.get("default", raw)


def assign_tier(row, rules, col_map):
    """Return tier string for a single row. col_map keys: email, name, institution, field keys."""
    for rule in rules:
        match = rule.get("match")

        if match == "email_list":
            col = col_map.get("email")
            if col and row.get(col, "") in rule.get("emails", []):
                return rule["tier"]

        elif match == "name_list":
            col = col_map.get("name")
            if col:
                name = str(row.get(col, "")).strip().lower()
                if name in [n.strip().lower() for n in rule.get("names", [])]:
                    return rule["tier"]

        elif match == "institution_contains":
            col = col_map.get("institution")
            if col:
                inst = str(row.get(col, "")).lower()
                if rule.get("value", "").lower() in inst:
                    return rule["tier"]

        elif match == "field_empty":
            field_col = col_map.get(rule.get("field_key", ""))
            if field_col:
                val = row.get(field_col)
                if pd.isna(val) or str(val).strip() == "":
                    return rule["tier"]

        elif match == "field_contains":
            field_col = col_map.get(rule.get("field_key", ""))
            if field_col:
                val = str(row.get(field_col, "")).strip().lower()
                if rule.get("value", "").lower() in val:
                    return rule["tier"]

        elif match == "timestamp_after":
            ts = row.get("__timestamp_parsed")
            if pd.notna(ts):
                cutoff = pd.Timestamp(rule.get("date", "2099-01-01"))
                ts_naive = ts.tz_localize(None) if ts.tzinfo else ts
                if ts_naive > cutoff:
                    return rule["tier"]

    return "III"


# ── Load & deduplicate ────────────────────────────────────────────────────────

csv_files = sorted(f for f in os.listdir(RAW_DIR) if f.endswith(".csv"))
if not csv_files:
    print("ERROR: No CSV found in data/raw/. Place your Google Form export there.")
    sys.exit(1)
if len(csv_files) > 1:
    print(f"WARNING: Multiple CSVs in data/raw/ — using '{csv_files[0]}'.")

csv_path  = os.path.join(RAW_DIR, csv_files[0])
df_raw    = pd.read_csv(csv_path)
n_raw     = len(df_raw)

email_col = resolve_column(df_raw, "email")
if not email_col:
    print("ERROR: Could not find email column. Check COLUMNS['email'] in data/config.py.")
    sys.exit(1)

df = df_raw.drop_duplicates(subset=[email_col], keep="last").copy()
n_unique = len(df)
print(f"Loaded {n_raw} entries → {n_unique} unique registrants (deduplicated on '{email_col}')")

# ── Column reconciliations ────────────────────────────────────────────────────

reconciled_cols = []
for rec in RECONCILIATIONS:
    src_col = resolve_column(df, rec["source_key"])
    out_name = rec["output_name"]
    if not src_col:
        print(f"WARNING: source column '{rec['source_key']}' not found — skipping '{out_name}'.")
        continue
    df[out_name] = df[src_col].apply(lambda v: apply_reconciliation(v, rec))
    reconciled_cols.append(out_name)
    counts = df[out_name].value_counts()
    print(f"\n{out_name} (reconciled from '{src_col}'):")
    for label, n in counts.items():
        print(f"  {label}: {n}")
print()


# ── Build column map for tier assignment ──────────────────────────────────────

col_map = {}
for key in config.COLUMNS:
    resolved = resolve_column(df, key)
    if resolved:
        col_map[key] = resolved

# Resolve any field_key references used in tier rules (field_empty, field_contains)
for rule in RULES:
    fk = rule.get("field_key", "")
    if fk and fk not in col_map:
        resolved = resolve_column(df, fk)
        if resolved:
            col_map[fk] = resolved

# Pre-parse timestamp column once for timestamp_after rules
if any(r.get("match") == "timestamp_after" for r in RULES):
    ts_col = col_map.get("timestamp")
    if ts_col:
        # Try the Google Forms default format first (M/D/YYYY H:MM:SS), fall back to flexible parsing
        df["__timestamp_parsed"] = pd.to_datetime(df[ts_col], format="%m/%d/%Y %H:%M:%S", errors="coerce")
        still_null = df["__timestamp_parsed"].isna() & df[ts_col].notna()
        if still_null.any():
            df.loc[still_null, "__timestamp_parsed"] = pd.to_datetime(
                df.loc[still_null, ts_col], errors="coerce"
            )
    else:
        print("WARNING: timestamp_after rule present but 'timestamp' column not found in config.")


# ── Apply tier rules ──────────────────────────────────────────────────────────

processed_rules = preprocess_rules(RULES)
df["Tier"] = df.apply(lambda row: assign_tier(row, processed_rules, col_map), axis=1)

tier_order = ["I", "II", "III", "IV", "V"]
df["Tier"] = pd.Categorical(df["Tier"], categories=tier_order, ordered=True)
df = df.sort_values("Tier").reset_index(drop=True)
df["Applicant #"] = df.index + 1


# ── Add reviewer columns ──────────────────────────────────────────────────────

reviewer_cols = []
for i in range(1, N_REVIEWERS + 1):
    for field in ("Name", "Grade", "Notes"):
        col = f"Reviewer {i} {field}"
        df[col] = ""
        reviewer_cols.append(col)


# ── Print summary ─────────────────────────────────────────────────────────────

tier_counts = df["Tier"].value_counts().reindex(tier_order).fillna(0).astype(int)
tier_labels = {
    "I":   "Whitelisted",
    "II":  "Preferred",
    "III": "Normal",
    "IV":  "Late Submission",
    "V":   "No Poster / Incomplete",
}

lines = []
lines.append(f"Source: {csv_files[0]}")
lines.append(f"Total entries: {n_raw}  |  Unique: {n_unique}")
lines.append("")
lines.append("Tier breakdown:")
lines.append("-" * 40)
for tier in tier_order:
    label = tier_labels[tier]
    lines.append(f"  Tier {tier} ({label}): {tier_counts[tier]}")
lines.append("-" * 40)
lines.append(f"  Total: {tier_counts.sum()}")

summary_text = "\n".join(lines)
print("\n" + summary_text)

summary_path = os.path.join(OUT_DIR, "summary.txt")
with open(summary_path, "w") as f:
    f.write(summary_text + "\n")
print(f"\nSaved: {summary_path}")


# ── Export CSV ────────────────────────────────────────────────────────────────

# Column order: Applicant #, Tier, Name, Email, then rest of form, then reviewer cols
name_col = col_map.get("name", "")
front_cols = ["Applicant #", "Tier"] + reconciled_cols
if name_col:
    front_cols.append(name_col)
if email_col not in front_cols:
    front_cols.append(email_col)

internal_cols = {c for c in df.columns if c.startswith("__")}
remaining = [c for c in df.columns if c not in front_cols and c not in reviewer_cols and c not in internal_cols]
export_cols = front_cols + remaining + reviewer_cols

csv_out = os.path.join(OUT_DIR, "review_sheet.csv")
df[export_cols].to_csv(csv_out, index=False)
print(f"Saved: {csv_out}")

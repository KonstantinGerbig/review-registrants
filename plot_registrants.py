"""
plot_registrants.py — Overview plots for conference registrants.

Reads:  data/raw/<form>.csv
        data/config.py
        data/outputs/review_sheet.csv  (optional — for tier distribution plot)

Writes: data/outputs/plots/overview_dashboard.png
        data/outputs/plots/institutions_and_fields.png
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

REPO_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(REPO_DIR, "data")
RAW_DIR    = os.path.join(DATA_DIR, "raw")
OUT_DIR    = os.path.join(DATA_DIR, "outputs")
PLOTS_DIR  = os.path.join(OUT_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

sys.path.insert(0, DATA_DIR)
try:
    import config
except ImportError:
    print("ERROR: data/config.py not found.")
    print("  → cp defaults/config.py data/config.py  then fill it in.")
    sys.exit(1)


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


def plot_pie(ax, series, title):
    counts = series.fillna("No Entry").value_counts()
    total  = counts.sum()
    ax.pie(
        counts, labels=counts.index,
        autopct=lambda p: f"{int(round(p * total / 100.0))}",
        startangle=90, textprops={"fontsize": 11},
        wedgeprops={"edgecolor": "black"},
    )
    ax.set_title(title, fontsize=13)


def plot_filled_pie(ax, series, title):
    counts = series.notna().map({True: "Filled out", False: "No entry"}).value_counts()
    total  = counts.sum()
    ax.pie(
        counts, labels=counts.index,
        autopct=lambda p: f"{int(round(p * total / 100.0))}",
        startangle=90, textprops={"fontsize": 11},
        wedgeprops={"edgecolor": "black"},
    )
    ax.set_title(title, fontsize=13)


def categorize_institution(name, groups):
    """Group institution name using INSTITUTION_GROUPS list from config."""
    if not isinstance(name, str):
        return "Unknown"
    n = name.lower()
    for label, keywords in groups:
        if any(kw.lower() in n for kw in keywords):
            return label
    return "Other"


# ── Load data ─────────────────────────────────────────────────────────────────
# Prefer the processed review_sheet (has Career Stage + Tier) over raw CSV.

review_sheet_path = os.path.join(OUT_DIR, "review_sheet.csv")
if os.path.exists(review_sheet_path):
    df = pd.read_csv(review_sheet_path)
    # Strip empty reviewer columns from plots — they add no information
    reviewer_cols = [c for c in df.columns if c.startswith("Reviewer ")]
    df = df.drop(columns=reviewer_cols, errors="ignore")
    total_entries = unique_count = len(df)
    print(f"Loaded {total_entries} registrants from review_sheet.csv")
else:
    csv_files = sorted(f for f in os.listdir(RAW_DIR) if f.endswith(".csv"))
    if not csv_files:
        print("ERROR: No CSV found in data/raw/ and review_sheet.csv doesn't exist.")
        print("  → Run sort_registrants.py first, or place raw CSV in data/raw/.")
        sys.exit(1)
    if len(csv_files) > 1:
        print(f"WARNING: Multiple CSVs in data/raw/ — using '{csv_files[0]}'.")
    df_raw        = pd.read_csv(os.path.join(RAW_DIR, csv_files[0]))
    total_entries = len(df_raw)
    email_col     = resolve_column(df_raw, "email") or df_raw.columns[0]
    df            = df_raw.drop_duplicates(subset=[email_col], keep="last").copy()
    unique_count  = len(df)
    print(f"Loaded {total_entries} entries → {unique_count} unique (from raw CSV)")

# Use reconciled Career Stage if available, otherwise fall back to raw position column
career_stage_col = "Career Stage" if "Career Stage" in df.columns else resolve_column(df, "position")
institution_col  = resolve_column(df, "institution")
field_col        = resolve_column(df, "research_area")

pie_specs = getattr(config, "PIE_COLUMNS", [])


# ── Plot 1: Overview dashboard ────────────────────────────────────────────────

n_pies    = len(pie_specs)
has_pies  = n_pies > 0
n_rows    = 2 if has_pies else 1
row_ratios = [1, 1.2] if has_pies else [1]

fig = plt.figure(figsize=(max(20, n_pies * 5), 8 * n_rows))
gs  = gridspec.GridSpec(n_rows, 5, figure=fig, height_ratios=row_ratios)

# Bar: career stage breakdown
ax_bar  = fig.add_subplot(gs[0, :4])
bar_col = career_stage_col
bar_title = "Registrants by Career Stage" if bar_col == "Career Stage" else "Registrants by Position"
if bar_col:
    counts = df[bar_col].fillna("No Entry").value_counts().sort_values(ascending=False)
    counts.plot(kind="bar", ax=ax_bar, color="skyblue", edgecolor="black", rot=45)
    ax_bar.set_xticklabels(ax_bar.get_xticklabels(), ha="right", fontsize=13)
else:
    ax_bar.text(0.5, 0.5, "Position column not found\n(check COLUMNS in data/config.py)",
                ha="center", va="center", fontsize=13)
ax_bar.set_title(bar_title, fontsize=16)
ax_bar.set_ylabel("Count", fontsize=13)
ax_bar.tick_params(axis="y", labelsize=12)

# Text panel: counts
ax_text = fig.add_subplot(gs[0, 4])
ax_text.axis("off")

# Check for tier distribution from review_sheet if it exists
review_sheet = os.path.join(DATA_DIR, "outputs", "review_sheet.csv")
tier_text = ""
if os.path.exists(review_sheet):
    df_rev = pd.read_csv(review_sheet)
    if "Tier" in df_rev.columns:
        tc = df_rev["Tier"].value_counts().reindex(["I","II","III","IV"]).fillna(0).astype(int)
        tier_text = "\n\nTiers:\n" + "\n".join(f"  {t}: {n}" for t, n in tc.items())

ax_text.text(
    0.5, 0.5,
    f"Total\nEntries: {total_entries}\n\nUnique: {unique_count}" + tier_text,
    fontsize=18, ha="center", va="center",
    bbox=dict(boxstyle="round,pad=0.8", facecolor="lightgrey", alpha=0.5),
)

# Pie row
if has_pies:
    for i, (field_key, title, kind) in enumerate(pie_specs[:5]):
        ax = fig.add_subplot(gs[1, i])
        col = resolve_column(df, field_key)
        if col:
            if kind == "filled":
                plot_filled_pie(ax, df[col], title)
            else:
                plot_pie(ax, df[col], title)
        else:
            ax.axis("off")
            ax.text(0.5, 0.5, f"Column not found\n({field_key})",
                    ha="center", va="center", fontsize=10)

plt.tight_layout()
out1 = os.path.join(PLOTS_DIR, "overview_dashboard.png")
plt.savefig(out1, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out1}")


# ── Plot 2: Institutions & research fields ────────────────────────────────────

inst_groups = getattr(config, "INSTITUTION_GROUPS", [])

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Institution panel
if institution_col:
    if inst_groups:
        df["__inst_group"] = df[institution_col].apply(
            lambda n: categorize_institution(n, inst_groups)
        )
        group_order = [label for label, _ in inst_groups] + ["Other", "Unknown"]
        inst_counts = df["__inst_group"].value_counts().reindex(group_order).dropna()
    else:
        inst_counts = df[institution_col].fillna("Unknown").value_counts().head(15)
    inst_counts.plot(kind="bar", ax=axes[0], color="coral", edgecolor="black", rot=45)
    axes[0].set_title("Registrants by Institution" +
                      (" Category" if inst_groups else " (top 15)"), fontsize=14)
else:
    axes[0].text(0.5, 0.5, "Institution column not found", ha="center", va="center")
    axes[0].set_title("Registrants by Institution", fontsize=14)
axes[0].set_ylabel("Count")
axes[0].set_xticklabels(axes[0].get_xticklabels(), ha="right")

# Research field panel
if field_col:
    field_counts = df[field_col].fillna("No Entry").value_counts().head(15)
    field_counts.plot(kind="bar", ax=axes[1], color="mediumpurple", edgecolor="black", rot=45)
    axes[1].set_title("Registrants by Research Field (top 15)", fontsize=14)
else:
    axes[1].text(0.5, 0.5, "Research area column not found", ha="center", va="center")
    axes[1].set_title("Registrants by Research Field", fontsize=14)
axes[1].set_ylabel("Count")
axes[1].set_xticklabels(axes[1].get_xticklabels(), ha="right")

plt.tight_layout()
out2 = os.path.join(PLOTS_DIR, "institutions_and_fields.png")
plt.savefig(out2, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out2}")

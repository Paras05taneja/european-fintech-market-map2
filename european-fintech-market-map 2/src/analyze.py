"""Summarise the market map: counts by segment and country, funding if filled in.
Usage: python src/analyze.py
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..")
df = pd.read_csv(os.path.join(ROOT, "data", "startups.csv"))
out = os.path.join(ROOT, "outputs"); os.makedirs(out, exist_ok=True)

print(f"{len(df)} companies, {df['segment'].nunique()} segments, {df['hq_country'].nunique()} countries\n")

seg = df.groupby("segment").size().sort_values(ascending=False)
ctry = df.groupby("hq_country").size().sort_values(ascending=False)
print("By segment:\n", seg.to_string(), "\n")
print("By country:\n", ctry.to_string(), "\n")

# Segment x country matrix: where is the map thin?
matrix = pd.crosstab(df["segment"], df["hq_country"])
matrix.to_csv(os.path.join(out, "segment_by_country.csv"))
print("Segment x country matrix saved.")

# Italy vs rest of map
it = df[df["hq_country"] == "Italy"]
print(f"\nItalian companies on the map: {len(it)} of {len(df)} "
      f"({len(it)/len(df):.0%}), in segments: {sorted(it['segment'].unique())}")
missing = sorted(set(df["segment"]) - set(it["segment"]))
print("Segments with no Italian company on this map:", missing)

# Funding analysis only if the user has filled the column in
funded = df.dropna(subset=["total_funding_usd_m"])
if len(funded) >= 5:
    by_seg = funded.groupby("segment")["total_funding_usd_m"].agg(["count", "sum", "median"])
    print("\nFunding by segment (filled rows only):\n", by_seg.round(1).to_string())
    by_seg["sum"].sort_values().plot(kind="barh", figsize=(8, 5), title="Total funding by segment ($M)")
    plt.tight_layout(); plt.savefig(os.path.join(out, "funding_by_segment.png"), dpi=150); plt.close()
else:
    print("\nFunding columns not filled yet. Add total_funding_usd_m, latest_round, "
          "key_investors and source_url from Crunchbase/Dealroom/press releases, then re-run.")

seg.sort_values().plot(kind="barh", figsize=(8, 5), title="Companies on the map by segment")
plt.xlabel("Number of companies"); plt.tight_layout()
plt.savefig(os.path.join(out, "companies_by_segment.png"), dpi=150); plt.close()

ctry.sort_values().plot(kind="barh", figsize=(7, 4), title="Companies on the map by HQ country")
plt.xlabel("Number of companies"); plt.tight_layout()
plt.savefig(os.path.join(out, "companies_by_country.png"), dpi=150); plt.close()
print("Charts saved to outputs/")

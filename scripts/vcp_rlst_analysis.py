"""
=============================================================================
VCP vs RLST Statistical Analysis (2016, 2019, 2022, 2025)
=============================================================================
Analyzes the relationship between Vegetation Carbon Proxy (VCP) and
Relative Land Surface Temperature (RLST) across four years.

Outputs per year:
  - Data cleaning summary (NaN removal, valid n)
  - Pearson correlation coefficient (r) and p-value
  - Coefficient of determination (R²)
  - Histogram with fitted normal curve (VCP and RLST)
  - Scatter plot with regression line and confidence band
  - Combined multi-year summary figure

Recommendations included:
  - Outlier detection (IQR method)
  - Normality test (Shapiro-Wilk / Kolmogorov-Smirnov)
  - Linear regression equation
  - Trend summary table
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
from scipy import stats
from scipy.stats import pearsonr, shapiro, kstest, norm
import warnings
warnings.filterwarnings("ignore")

# ── Colour palette ────────────────────────────────────────────────────────────
YEAR_COLORS = {
    2016: "#2196F3",   # blue
    2019: "#4CAF50",   # green
    2022: "#FF9800",   # orange
    2025: "#E91E63",   # pink/red
}

# ── Load data ─────────────────────────────────────────────────────────────────
print("=" * 70)
print("  VCP vs RLST ANALYSIS  |  Years: 2016, 2019, 2022, 2025")
print("=" * 70)

df = pd.read_csv(r"C:\Users\USER\Documents\ArcGIS\Projects\FINAL-PROJECT-V1\PYTHON\SAMPLES.csv")
print(f"\nRaw dataset shape: {df.shape[0]} rows × {df.shape[1]} columns\n")

YEARS = [2016, 2019, 2022, 2025]

def get_cols(year):
    vcp_col  = f"VCP_{year}"
    rlst_col = f"RLST_{year}"
    return vcp_col, rlst_col


def clean_data(df, year):
    """Return cleaned (vcp, rlst) arrays and a stats dict."""
    vcp_col, rlst_col = get_cols(year)
    sub = df[[vcp_col, rlst_col]].copy()
    n_raw = len(sub)
    sub.replace("nan", np.nan, inplace=True)
    sub = sub.apply(pd.to_numeric, errors="coerce")
    sub.dropna(inplace=True)
    n_valid = len(sub)
    n_removed = n_raw - n_valid
    return sub[vcp_col].values, sub[rlst_col].values, n_raw, n_valid, n_removed


def normality_test(data, label, year):
    """Choose Shapiro-Wilk (n≤5000) or K-S test and return result string."""
    if len(data) <= 5000:
        stat, p = shapiro(data)
        test_name = "Shapiro-Wilk"
    else:
        stat, p = kstest(data, "norm", args=(np.mean(data), np.std(data)))
        test_name = "Kolmogorov-Smirnov"
    normal = "✓ Normal" if p > 0.05 else "✗ Non-normal"
    return f"{test_name}: W={stat:.4f}, p={p:.4f}  →  {normal}"


def iqr_outliers(data):
    """Return mask of outliers using 1.5×IQR rule."""
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    return (data < q1 - 1.5 * iqr) | (data > q3 + 1.5 * iqr)


# ── Per-year analysis ─────────────────────────────────────────────────────────
summary_rows = []

for year in YEARS:
    color = YEAR_COLORS[year]
    vcp, rlst, n_raw, n_valid, n_removed = clean_data(df, year)

    # ── Statistics ───────────────────────────────────────────────────────────
    r, p_val  = pearsonr(vcp, rlst)
    r2        = r ** 2
    slope, intercept, _, _, se = stats.linregress(vcp, rlst)

    # Outliers
    out_vcp  = iqr_outliers(vcp)
    out_rlst = iqr_outliers(rlst)
    n_out    = int(np.sum(out_vcp | out_rlst))

    # Normality
    norm_vcp  = normality_test(vcp,  "VCP",  year)
    norm_rlst = normality_test(rlst, "RLST", year)

    # Significance label
    if   p_val < 0.001: sig = "***"
    elif p_val < 0.01:  sig = "**"
    elif p_val < 0.05:  sig = "*"
    else:               sig = "ns"

    summary_rows.append({
        "Year": year, "n_valid": n_valid, "n_removed": n_removed,
        "r": r, "r2": r2, "p_val": p_val, "sig": sig,
        "slope": slope, "intercept": intercept, "n_outliers": n_out,
    })

    # ── Console output ────────────────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print(f"  YEAR {year}")
    print(f"{'─'*70}")
    print(f"  Raw observations       : {n_raw}")
    print(f"  NaN / invalid removed  : {n_removed}")
    print(f"  Valid data points (n)  : {n_valid}")
    print(f"  Outliers detected (IQR): {n_out}  "
          f"({100*n_out/n_valid:.1f}% of valid data)")
    print()
    print(f"  Pearson r              : {r:.4f}")
    print(f"  R²                     : {r2:.4f}  "
          f"({100*r2:.1f}% variance explained)")
    print(f"  p-value                : {p_val:.4e}  {sig}")
    print(f"  Regression equation    : RLST = {slope:.4f}·VCP "
          f"{'+'if intercept>=0 else ''}{intercept:.4f}")
    print(f"  Std error of slope     : {se:.4f}")
    print()
    print(f"  Normality — VCP  : {norm_vcp}")
    print(f"  Normality — RLST : {norm_rlst}")

    # ── Figure: histogram + scatter ───────────────────────────────────────────
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle(
        f"VCP vs RLST Analysis  —  {year}  |  n = {n_valid}",
        fontsize=15, fontweight="bold", y=0.98
    )
    gs = gridspec.GridSpec(2, 3, figure=fig,
                           hspace=0.45, wspace=0.35,
                           left=0.07, right=0.97, top=0.92, bottom=0.08)

    # ── Histogram VCP ─────────────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    counts, bins, _ = ax1.hist(vcp, bins=30, color=color,
                                alpha=0.65, edgecolor="white", density=True)
    xv = np.linspace(vcp.min(), vcp.max(), 200)
    ax1.plot(xv, norm.pdf(xv, vcp.mean(), vcp.std()),
             color="black", lw=2, label="Normal curve")
    ax1.set_title(f"VCP Distribution  ({year})", fontweight="bold")
    ax1.set_xlabel("VCP"); ax1.set_ylabel("Density")
    ax1.legend(fontsize=9)
    ax1.text(0.97, 0.92,
             f"μ={vcp.mean():.3f}\nσ={vcp.std():.3f}",
             transform=ax1.transAxes, ha="right", va="top",
             fontsize=8.5, bbox=dict(boxstyle="round,pad=0.3",
                                     facecolor="white", alpha=0.8))

    # ── Histogram RLST ────────────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.hist(rlst, bins=30, color=color,
             alpha=0.65, edgecolor="white", density=True)
    xr = np.linspace(rlst.min(), rlst.max(), 200)
    ax2.plot(xr, norm.pdf(xr, rlst.mean(), rlst.std()),
             color="black", lw=2, label="Normal curve")
    ax2.set_title(f"RLST Distribution  ({year})", fontweight="bold")
    ax2.set_xlabel("RLST (°C relative)"); ax2.set_ylabel("Density")
    ax2.legend(fontsize=9)
    ax2.text(0.97, 0.92,
             f"μ={rlst.mean():.3f}\nσ={rlst.std():.3f}",
             transform=ax2.transAxes, ha="right", va="top",
             fontsize=8.5, bbox=dict(boxstyle="round,pad=0.3",
                                     facecolor="white", alpha=0.8))

    # ── Stats summary box ─────────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.axis("off")
    stats_text = (
        f"{'Statistical Summary':^32}\n"
        f"{'─'*32}\n"
        f"  n (valid)       : {n_valid}\n"
        f"  NaN removed     : {n_removed}\n"
        f"  Outliers (IQR)  : {n_out}\n\n"
        f"  Pearson r       : {r:+.4f}\n"
        f"  R²              : {r2:.4f}\n"
        f"  p-value         : {p_val:.2e}  {sig}\n\n"
        f"  Regression:\n"
        f"  RLST = {slope:.3f}·VCP\n"
        f"         {'+'if intercept>=0 else ''}{intercept:.3f}\n\n"
        f"  Interpretation:\n"
        f"  {'↑ Higher VCP → Higher RLST' if slope>0 else '↑ Higher VCP → Lower RLST'}\n"
        f"  Correlation: {'Positive' if r>0 else 'Negative'} ({'Strong' if abs(r)>.5 else 'Moderate' if abs(r)>.3 else 'Weak'})"
    )
    ax3.text(0.05, 0.97, stats_text, transform=ax3.transAxes,
             va="top", ha="left", fontsize=9,
             fontfamily="monospace",
             bbox=dict(boxstyle="round,pad=0.5",
                       facecolor="#f5f5f5", edgecolor=color, linewidth=1.5))

    # ── Scatter plot ──────────────────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, :])
    outlier_mask = out_vcp | out_rlst

    # Normal points
    ax4.scatter(vcp[~outlier_mask], rlst[~outlier_mask],
                c=color, alpha=0.35, s=15, linewidths=0, label="Data points")
    # Outliers highlighted
    if outlier_mask.any():
        ax4.scatter(vcp[outlier_mask], rlst[outlier_mask],
                    c="red", alpha=0.55, s=20, marker="x",
                    linewidths=1, label=f"Outliers (n={n_out})")

    # Regression line
    x_line = np.linspace(vcp.min(), vcp.max(), 300)
    y_line = slope * x_line + intercept
    ax4.plot(x_line, y_line, color="black", lw=2.5, label="Regression line")

    # 95 % confidence band (analytical)
    x_mean = vcp.mean()
    n = n_valid
    t_crit = stats.t.ppf(0.975, df=n - 2)
    se_band = se * np.sqrt(1/n + (x_line - x_mean)**2 / np.sum((vcp - x_mean)**2))
    ax4.fill_between(x_line, y_line - t_crit * se_band,
                                y_line + t_crit * se_band,
                     alpha=0.18, color=color, label="95% CI band")

    ax4.set_title(
        f"VCP vs RLST Scatter  ({year})   "
        f"r = {r:+.4f}  |  R² = {r2:.4f}  |  p = {p_val:.2e} {sig}",
        fontweight="bold"
    )
    ax4.set_xlabel("VCP  (Vegetation Carbon Proxy)", fontsize=11)
    ax4.set_ylabel("RLST  (Relative Land Surface Temperature, °C)", fontsize=11)
    ax4.legend(fontsize=9, loc="upper right")
    ax4.grid(True, alpha=0.25, linestyle="--")

    fig.savefig("analysis_{year}.png",
                dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  → Figure saved: analysis_{year}.png")


# ── Multi-year summary figure ─────────────────────────────────────────────────
print(f"\n{'─'*70}")
print("  MULTI-YEAR COMPARISON")
print(f"{'─'*70}")

fig2, axes = plt.subplots(2, 2, figsize=(14, 10))
fig2.suptitle("VCP vs RLST — Multi-Year Scatter Comparison",
              fontsize=14, fontweight="bold", y=0.98)

for ax, year in zip(axes.flatten(), YEARS):
    color = YEAR_COLORS[year]
    row = next(r for r in summary_rows if r["Year"] == year)
    vcp, rlst, _, n_valid, _ = clean_data(df, year)

    out_mask = iqr_outliers(vcp) | iqr_outliers(rlst)
    ax.scatter(vcp[~out_mask], rlst[~out_mask],
               c=color, alpha=0.3, s=10, linewidths=0)
    x_line = np.linspace(vcp.min(), vcp.max(), 200)
    ax.plot(x_line, row["slope"] * x_line + row["intercept"],
            color="black", lw=2)
    ax.set_title(
        f"{year}   n={n_valid}   r={row['r']:+.3f}   R²={row['r2']:.3f}   "
        f"p={row['p_val']:.1e} {row['sig']}",
        fontsize=9.5, fontweight="bold"
    )
    ax.set_xlabel("VCP", fontsize=9)
    ax.set_ylabel("RLST", fontsize=9)
    ax.grid(True, alpha=0.25, linestyle="--")

plt.tight_layout(rect=[0, 0, 1, 0.96])
fig2.savefig("analysis_multi_year.png",
             dpi=150, bbox_inches="tight")
plt.close(fig2)
print("  → Figure saved: analysis_multi_year.png")


# ── Summary table ─────────────────────────────────────────────────────────────
print(f"\n{'─'*70}")
print("  SUMMARY TABLE")
print(f"{'─'*70}")
print(f"\n  {'Year':>6} | {'n':>6} | {'NaN':>5} | {'r':>8} | "
      f"{'R²':>7} | {'p-value':>12} | {'Sig':>4} | {'Slope':>8} | {'Intercept':>10}")
print("  " + "-" * 78)
for row in summary_rows:
    print(f"  {row['Year']:>6} | {row['n_valid']:>6} | {row['n_removed']:>5} | "
          f"{row['r']:>+8.4f} | {row['r2']:>7.4f} | {row['p_val']:>12.4e} | "
          f"{row['sig']:>4} | {row['slope']:>+8.4f} | {row['intercept']:>+10.4f}")

print(f"\n  Significance codes: *** p<0.001   ** p<0.01   * p<0.05   ns p≥0.05")

# ── Trend bar chart ───────────────────────────────────────────────────────────
fig3, (ax_r, ax_r2) = plt.subplots(1, 2, figsize=(12, 5))
fig3.suptitle("VCP–RLST Correlation Summary Across Years",
              fontsize=13, fontweight="bold")

years_list = [r["Year"] for r in summary_rows]
r_vals     = [r["r"]    for r in summary_rows]
r2_vals    = [r["r2"]   for r in summary_rows]
colors_bar = [YEAR_COLORS[y] for y in years_list]

bars1 = ax_r.bar(years_list, r_vals, color=colors_bar, width=1.8, edgecolor="white")
ax_r.axhline(0, color="black", lw=0.8, linestyle="--")
ax_r.set_title("Pearson r  (correlation coefficient)", fontweight="bold")
ax_r.set_ylabel("r value"); ax_r.set_ylim(-1, 1)
ax_r.set_xticks(years_list)
for bar, val in zip(bars1, r_vals):
    ax_r.text(bar.get_x() + bar.get_width() / 2,
              val + 0.02 * np.sign(val),
              f"{val:+.4f}", ha="center", va="bottom" if val >= 0 else "top",
              fontsize=9, fontweight="bold")

bars2 = ax_r2.bar(years_list, r2_vals, color=colors_bar, width=1.8, edgecolor="white")
ax_r2.set_title("R²  (coefficient of determination)", fontweight="bold")
ax_r2.set_ylabel("R² value"); ax_r2.set_ylim(0, max(r2_vals) * 1.25)
ax_r2.set_xticks(years_list)
for bar, val in zip(bars2, r2_vals):
    ax_r2.text(bar.get_x() + bar.get_width() / 2,
               val + 0.001,
               f"{val:.4f}\n({100*val:.1f}%)",
               ha="center", va="bottom", fontsize=9, fontweight="bold")

plt.tight_layout()
fig3.savefig("analysis_summary_bars.png",
             dpi=150, bbox_inches="tight")
plt.close(fig3)
print("\n  → Figure saved: analysis_summary_bars.png")

# ── Recommendations ───────────────────────────────────────────────────────────
print(f"\n{'─'*70}")
print("  RECOMMENDATIONS")
print(f"{'─'*70}")
recs = [
    "1. NORMALITY  — Both VCP and RLST should be tested for normality before "
    "reporting Pearson r. If either is non-normal, consider Spearman ρ or "
    "Kendall τ as a complementary non-parametric measure.",
    "2. OUTLIERS   — Outliers are flagged (IQR ×1.5) but NOT removed. "
    "Investigate whether they represent real land-cover extremes or sensor "
    "artefacts before exclusion.",
    "3. SPATIAL    — Samples may be spatially autocorrelated. Apply Moran's I "
    "or use spatially-lagged regression (SAR/CAR) to avoid inflated r.",
    "4. SEASONALITY — If data span different phenological periods across years, "
    "consider normalising VCP and RLST to same-season acquisitions.",
    "5. NON-LINEAR — If residual plots show curvature, test quadratic or "
    "logarithmic models (ln(VCP) vs RLST) for a better fit.",
    "6. CHANGE     — Compute Δr and ΔR² across years to quantify the "
    "strengthening or weakening of the VCP–RLST relationship over time.",
    "7. PARTIAL r  — Control for confounders (elevation, impervious surface "
    "fraction) via partial correlation or multiple regression.",
]
for rec in recs:
    print(f"\n  {rec}")

print(f"\n{'='*70}")
print("  Analysis completed. All figures saved to current directory.")
print(f"{'='*70}\n")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import StrMethodFormatter

# --- Parameters ---
avg_power_price_per_mwh = 65.0
om_cost_ratio = 0.10
mgmt_fee_ratio = 0.02
discount_rate = 0.08
analysis_start_year = 2025
analysis_end_year = 2049
portfolio_gwh_2024 = 5484
target_capacity_factor = 0.31
market_cap_gbp_m = 2280  # £2.28b as of 15/09/2025

turbine_life_years = 25
annual_degradation = 0.005

# --- Synthetic portfolio ---
np.random.seed(7)
total_capacity_mw = 1980
n_assets = 120
asset_mw = np.random.triangular(5, 15, 40, size=n_assets)
asset_mw *= total_capacity_mw / asset_mw.sum()
current_year = 2024
bucket_probs = [0.14, 0.51, 0.35]
bucket_choices = np.random.choice([0,1,2], size=n_assets, p=bucket_probs)
ages = np.zeros(n_assets)
for i, b in enumerate(bucket_choices):
    if b == 0:
        age = np.random.randint(0,5)
    elif b == 1:
        age = np.random.randint(5,11)
    else:
        age = np.random.randint(10,21)
    ages[i] = age
commission_year = current_year - ages.astype(int)
portfolio = pd.DataFrame({"asset": [f"A{i:03d}" for i in range(n_assets)],
                          "mw": asset_mw,
                          "commission_year": commission_year.astype(int)})
portfolio.to_csv("/mnt/data/ukw_age_template.csv", index=False)

# --- Generation calculation ---
years = np.arange(analysis_start_year, analysis_end_year+1)
def mw_to_gwh(mw, capacity_factor):
    return mw * 8760 * capacity_factor / 1000.0
mw_total = portfolio["mw"].sum()
gwh_2024_model = mw_to_gwh(mw_total, target_capacity_factor)
scale_to_report = portfolio_gwh_2024 / gwh_2024_model
gen_table = pd.DataFrame(index=years, columns=portfolio["asset"], dtype=float)
for idx, row in portfolio.iterrows():
    mw = row["mw"]
    y0 = int(row["commission_year"])
    for y in years:
        age = y - y0
        if 0 <= age < turbine_life_years:
            base = mw_to_gwh(mw, target_capacity_factor) * scale_to_report
            perf = base * ((1 - annual_degradation) ** age)
        else:
            perf = 0.0
        gen_table.at[y, row["asset"]] = perf
annual_generation_gwh = gen_table.sum(axis=1)

# --- Revenue, NPV ---
gross_rev_m = annual_generation_gwh * avg_power_price_per_mwh / 1000.0
net_rev_m = gross_rev_m * (1 - om_cost_ratio - mgmt_fee_ratio)
years_from_start = years - analysis_start_year
disc_factors = 1.0 / (1.0 + discount_rate) ** years_from_start
npv_m = (net_rev_m * disc_factors).sum()
cum_disc_cf_m = (net_rev_m * disc_factors).cumsum()

# --- Plot ---
plt.figure(figsize=(12,7))
plt.bar(years, net_rev_m, color="#1a9850", edgecolor="#0b3d2e")
plt.plot(years, cum_disc_cf_m, linestyle="-", marker="o", color="#283593", 
         label="Cumulative discounted cash flow (NPV)")
plt.axhline(y=market_cap_gbp_m, color="#d73027", linestyle="--", 
            label=f"Market cap £{market_cap_gbp_m:,.0f}m")

plt.title("UKW: Projected Net Revenue from Existing Assets vs. Market Capitalisation", fontsize=14, weight="bold")
plt.xlabel("Year")
plt.ylabel("£ million")
plt.xticks(years, rotation=45)
plt.gca().yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

# Key figures box (bottom right, above assumptions)
text = (
    f"Key figures:\n"
    f"• NPV of net cash flows (2025–{analysis_end_year}): £{npv_m:,.0f}m\n"
    f"• Total undiscounted net revenue: £{net_rev_m.sum():,.0f}m\n"
    f"• Market cap (as of 15/09/2025): £{market_cap_gbp_m:,.0f}m\n"
    f"• Implied NPV / Market cap: {npv_m/market_cap_gbp_m:,.2f}x"
)
plt.gcf().text(0.65, 0.55, text, fontsize=10, bbox=dict(facecolor="white", alpha=0.8))

# Assumptions box (slightly moved left)
assumptions = (
    "Assumptions:\n"
    f"• Avg price £{avg_power_price_per_mwh:.0f}/MWh; O&M {om_cost_ratio*100:.0f}%, Mgmt {mgmt_fee_ratio*100:.0f}%\n"
    f"• Target CF {target_capacity_factor*100:.0f}% (scaled to {portfolio_gwh_2024:,} GWh in 2024)\n"
    f"• Turbine life {turbine_life_years}y; degradation {annual_degradation*100:.1f}%/y\n"
    f"• Age distribution approx: <5y 14%, 5–10y 51%, 10–20y 35%\n"
    f"• Discount rate {discount_rate*100:.0f}%"
)
plt.gcf().text(0.58, 0.30, assumptions, fontsize=10, bbox=dict(facecolor="white", alpha=0.8))

# Legend stays top left
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("/mnt/data/ukw_future_revenue_vs_marketcap_v9.png", dpi=200)
plt.close()

("/mnt/data/ukw_future_revenue_vs_marketcap_v9.png")

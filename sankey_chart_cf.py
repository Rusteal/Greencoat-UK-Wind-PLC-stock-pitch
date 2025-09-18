import pandas as pd
import plotly.graph_objects as go
import os

def make_cashflow_sankey(csv_file, title, out_html, out_png):
    # Load
    df = pd.read_csv(csv_file)
    df.columns = [c.strip() for c in df.columns]  # clean headers
    value_col = [c for c in df.columns if "Value" in c][0]
    df["Value"] = df[value_col].astype(str).str.replace(",", "").astype(float)

    # Rename for clarity
    df["Metric"] = df["Metric"].replace({
        "Debt interest": "Debt Interest Payments"
    })

    # Extract operating inflow
    operating = float(df.loc[df["Metric"].str.contains("Operating activities", case=False), "Value"].iloc[0])

    # Split categories
    investing_rows = df[df["Metric"].str.contains("Acquisition|Disposal|Repayment of shareholder loan", case=False)]
    financing_rows = df[df["Metric"].str.contains("buyback|Amounts drawn|Debt Interest|Dividends", case=False)]
    net_rows = df[df["Metric"].str.contains("Net increase|Net change", case=False)]

    sources, targets, values = [], [], []

    # Operating inflow
    sources.append("Operating Cash Flow")
    targets.append("Cash Available")
    values.append(abs(operating))

    # Investing as inflow too
    if not investing_rows.empty:
        invest_total = investing_rows["Value"].sum()
        if invest_total != 0:
            sources.append("Investing")
            targets.append("Cash Available")
            values.append(abs(invest_total))
            for _, row in investing_rows.iterrows():
                v = abs(row["Value"])
                if v > 0:
                    sources.append("Investing")
                    targets.append(row["Metric"])
                    values.append(v)

    # Financing branch (outflow from Cash Available)
    if not financing_rows.empty:
        finance_total = financing_rows["Value"].sum()
        if finance_total != 0:
            sources.append("Cash Available")
            targets.append("Financing")
            values.append(abs(finance_total))
            for _, row in financing_rows.iterrows():
                v = abs(row["Value"])
                if v > 0:
                    sources.append("Financing")
                    targets.append(row["Metric"])
                    values.append(v)

    # Net change branch
    for _, row in net_rows.iterrows():
        v = abs(row["Value"])
        if v > 0:
            sources.append("Cash Available")
            targets.append(row["Metric"])
            values.append(v)

    # Build Sankey
    labels = list(set(sources + targets))
    label_to_idx = {l: i for i, l in enumerate(labels)}
    src_idx = [label_to_idx[s] for s in sources]
    tgt_idx = [label_to_idx[t] for t in targets]

    fig = go.Figure(go.Sankey(
        node=dict(
            label=labels,
            pad=20,
            thickness=20,
            line=dict(color="black", width=0.5),
        ),
        link=dict(
            source=src_idx,
            target=tgt_idx,
            value=values,
        )
    ))

    fig.update_layout(title_text=title, font_size=12, width=1200, height=700)

    os.makedirs(os.path.dirname(out_html) or ".", exist_ok=True)
    fig.write_html(out_html)
    try:
        fig.write_image(out_png)
    except Exception as e:
        print("⚠️ Error saving PNG:", e)

    print(f"Saved {title}: {out_html}, {out_png}")


if __name__ == "__main__":
    make_cashflow_sankey(
        "cash_flow_2024.csv",
        "Cash Flow 2024 (Greencoat UK Wind)",
        "cash_flow_2024.html",
        "cash_flow_2024.png"
    )
    make_cashflow_sankey(
        "cash_flow_h1_2025.csv",
        "Cash Flow H1 2025 (Greencoat UK Wind)",
        "cash_flow_h1_2025.html",
        "cash_flow_h1_2025.png"
    )

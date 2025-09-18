import pandas as pd
import plotly.graph_objects as go
import os

def make_balance_sheet_sankey(csv_file, title, out_html, out_png):
    # Load data
    df = pd.read_csv(csv_file)
    df["Value"] = df["Value"].astype(str).str.replace(",", "").astype(float)

    # Extract numbers
    equity = float(df.loc[df["Metric"].str.contains("Equity", case=False), "Value"].iloc[0])
    loans = float(df.loc[df["Metric"].str.contains("Loans", case=False), "Value"].iloc[0])
    payables = float(df.loc[df["Metric"].str.contains("Payables", case=False), "Value"].iloc[0])
    inv = float(df.loc[df["Metric"].str.contains("Investments at fair value", case=False), "Value"].iloc[0])
    swaps = float(df.loc[df["Metric"].str.contains("Interest rate swaps", case=False), "Value"].iloc[0])
    receivables = float(df.loc[df["Metric"].str.contains("Receivables", case=False), "Value"].iloc[0])
    cash = float(df.loc[df["Metric"].str.contains("Cash & cash equivalents", case=False), "Value"].iloc[0])

    # Nodes
    labels = [
        "Net Assets / Equity", 
        "Loans & Borrowings (non-current)", 
        "Payables (current liabilities)",
        "Balance Sheet",
        "Investments at fair value",
        "Interest rate swaps (non-current)",
        "Receivables (Current Assets)",
        "Cash & cash equivalents"
    ]

    # Links
    sources = [
        0, 1, 2,  # Left -> Balance Sheet
        3, 3, 3, 3 # Balance Sheet -> Right
    ]
    targets = [
        3, 3, 3,
        4, 5, 6, 7
    ]
    values = [
        equity, loans, payables,
        inv, swaps, receivables, cash
    ]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color="green"
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values
        )
    )])

    fig.update_layout(title_text=title, font_size=12, width=1200, height=650)

    # Ensure output directory
    os.makedirs(os.path.dirname(out_html) or ".", exist_ok=True)

    # Save both HTML and PNG
    fig.write_html(out_html)
    try:
        fig.write_image(out_png)
    except Exception as e:
        print("⚠️ Error saving PNG:", e)
        print("➡️ Try installing kaleido with: pip install kaleido")

    print(f"Saved {title} → {out_html}, {out_png}")


if __name__ == "__main__":
    make_balance_sheet_sankey(
        "balance_sheet_2024.csv",
        "Balance Sheet 2024 (Greencoat UK Wind)",
        "balance_sheet_2024.html",
        "balance_sheet_2024.png"
    )
    make_balance_sheet_sankey(
        "balance_sheet_h1_2025.csv",
        "Balance Sheet H1 2025 (Greencoat UK Wind)",
        "balance_sheet_h1_2025.html",
        "balance_sheet_h1_2025.png"
    )

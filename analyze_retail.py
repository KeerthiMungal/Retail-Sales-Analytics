"""
End-to-end Retail Sales Analytics
Dataset is synthetic and created for portfolio/learning purposes.
Run from the project root: python src/analyze_retail.py
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "retail_sales_raw.csv"
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"
OUT.mkdir(exist_ok=True)
CHARTS.mkdir(parents=True, exist_ok=True)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    for col in ["Quantity", "Unit_Price", "Discount", "Unit_Cost", "Revenue", "Profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # Normalise text and replace blank strings with missing values
    for col in ["Region", "Sales_Channel", "Customer_Segment", "Category", "Product"]:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)
    # Remove rows with invalid dates or impossible price/quantity/discount values
    df = df.dropna(subset=["Order_ID", "Order_Date", "Category", "Product"])
    df = df[(df["Quantity"] > 0) & (df["Unit_Price"] > 0) &
            (df["Unit_Cost"] >= 0) & (df["Discount"].between(0, 0.8))]
    # Fill missing dimensions with explicit unknown category rather than dropping sales
    for col in ["Region", "Sales_Channel", "Customer_Segment"]:
        df[col] = df[col].fillna("Unknown")
    # Recalculate revenue and profit so metrics are internally consistent
    df["Revenue"] = (df["Quantity"] * df["Unit_Price"] * (1 - df["Discount"])).round(2)
    df["Profit"] = (df["Quantity"] * (df["Unit_Price"] - df["Unit_Cost"]) -
                    df["Quantity"] * df["Unit_Price"] * df["Discount"]).round(2)
    df["Profit_Margin"] = (df["Profit"] / df["Revenue"].replace(0, pd.NA)).fillna(0)
    df["Order_Month"] = df["Order_Date"].dt.to_period("M").astype(str)
    return df.sort_values("Order_Date")

def save_bar(series, title, xlabel, ylabel, path, horizontal=False):
    fig, ax = plt.subplots(figsize=(9, 5))
    if horizontal:
        series.sort_values().plot(kind="barh", ax=ax)
    else:
        series.plot(kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)

def main():
    raw = pd.read_csv(DATA)
    cleaned = clean_data(raw)
    cleaned.to_csv(OUT / "retail_sales_clean.csv", index=False)

    monthly = cleaned.groupby("Order_Month", as_index=False).agg(
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum"),
        Orders=("Order_ID", "nunique"), Units_Sold=("Quantity", "sum"))
    monthly.to_csv(OUT / "monthly_kpis.csv", index=False)

    category = cleaned.groupby("Category", as_index=False).agg(
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum"),
        Units_Sold=("Quantity", "sum"), Order_Lines=("Order_ID", "count"))
    category["Profit_Margin"] = category["Profit"] / category["Revenue"].replace(0, pd.NA)
    category.to_csv(OUT / "category_performance.csv", index=False)

    channel = cleaned.groupby("Sales_Channel", as_index=False).agg(
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum"),
        Orders=("Order_ID", "nunique"), Units_Sold=("Quantity", "sum"))
    channel.to_csv(OUT / "channel_performance.csv", index=False)

    region = cleaned.groupby("Region", as_index=False).agg(
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum"),
        Orders=("Order_ID", "nunique"))
    region.to_csv(OUT / "regional_performance.csv", index=False)

    discount = cleaned.groupby("Discount", as_index=False).agg(
        Avg_Revenue=("Revenue", "mean"), Avg_Profit=("Profit", "mean"),
        Order_Lines=("Order_ID", "count"))
    discount.to_csv(OUT / "discount_analysis.csv", index=False)

    # Charts
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(monthly["Order_Month"], monthly["Revenue"], marker="o", linewidth=1.5)
    ax.set_title("Monthly Revenue Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (currency units)")
    ax.tick_params(axis="x", rotation=70)
    fig.tight_layout()
    fig.savefig(CHARTS / "monthly_revenue_trend.png", dpi=160)
    plt.close(fig)

    save_bar(category.set_index("Category")["Revenue"], "Revenue by Product Category",
             "Category", "Revenue (currency units)", CHARTS / "revenue_by_category.png")
    save_bar(channel.set_index("Sales_Channel")["Profit"], "Profit by Sales Channel",
             "Sales channel", "Profit (currency units)", CHARTS / "profit_by_channel.png")
    save_bar(region.set_index("Region")["Revenue"], "Revenue by Region",
             "Region", "Revenue (currency units)", CHARTS / "revenue_by_region.png", horizontal=True)

    total_revenue = cleaned["Revenue"].sum()
    total_profit = cleaned["Profit"].sum()
    total_orders = cleaned["Order_ID"].nunique()
    avg_order = total_revenue / total_orders if total_orders else 0
    margin = total_profit / total_revenue if total_revenue else 0
    top_category = category.sort_values("Revenue", ascending=False).iloc[0]
    top_channel = channel.sort_values("Revenue", ascending=False).iloc[0]
    report = f"""# Retail Sales Analytics — Automated Summary

> **Data note:** This analysis uses synthetic data generated for this portfolio project. Values are illustrative and do not represent a real retailer.

## Dataset and quality
- Raw rows: {len(raw):,}
- Cleaned rows: {len(cleaned):,}
- Rows excluded by validation rules: {len(raw)-len(cleaned):,}
- Date range: {cleaned['Order_Date'].min().date()} to {cleaned['Order_Date'].max().date()}

## KPI snapshot
- Total revenue: {total_revenue:,.2f} currency units
- Total profit: {total_profit:,.2f} currency units
- Unique orders: {total_orders:,}
- Average revenue per order: {avg_order:,.2f} currency units
- Overall profit margin: {margin:.1%}
- Highest-revenue category: {top_category['Category']} ({top_category['Revenue']:,.2f})
- Highest-revenue channel: {top_channel['Sales_Channel']} ({top_channel['Revenue']:,.2f})

## Questions explored
1. How does revenue change month by month?
2. Which categories contribute the most revenue and profit?
3. How do sales channels compare?
4. How does performance vary by region?
5. How do observed order-level metrics vary by discount level?

## Interpretation notes
- The dataset is synthetic; all figures and patterns are demonstration-only.
- The discount analysis is descriptive and does not establish causation.
- Revenue and profit are recalculated from quantity, unit price, unit cost and discount during cleaning.
- In a real project, validate business definitions, tax/shipping treatment, returns, currency and the meaning of an order before drawing business conclusions.
"""
    (OUT / "analysis_summary.md").write_text(report, encoding="utf-8")
    print("Analysis complete.")
    print(f"Raw rows: {len(raw):,}; cleaned rows: {len(cleaned):,}")
    print(f"Revenue: {total_revenue:,.2f}; Profit: {total_profit:,.2f}; Orders: {total_orders:,}")
    print(f"Outputs saved to: {OUT}")

if __name__ == "__main__":
    main()

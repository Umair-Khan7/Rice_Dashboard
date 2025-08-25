
import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
df = pd.read_csv("Rice_sales_CSV.csv")

st.set_page_config(page_title="Basmati Rice Sales Dashboard", layout="wide")

# Title
st.title("📊 Basmati Rice Sales Analysis Dashboard")
st.markdown("### Interactive Performance Tracker")

# Sidebar filters
months = df["month"].unique()
selected_month = st.sidebar.selectbox("Select Month", months)

weeks = ["All Weeks"] + sorted(df[df["month"] == selected_month]["week_in_month"].unique().tolist())
selected_week = st.sidebar.selectbox("Select Week", weeks)

supervisors = ["All Supervisors"] + df["supervisor"].unique().tolist()
selected_supervisor = st.sidebar.selectbox("Select Supervisor", supervisors)

# Apply filters
filtered_df = df[df["month"] == selected_month]
if selected_week != "All Weeks":
    filtered_df = filtered_df[filtered_df["week_in_month"] == selected_week]
if selected_supervisor != "All Supervisors":
    filtered_df = filtered_df[filtered_df["supervisor"] == selected_supervisor]

# Aggregate for KPIs
agg = filtered_df.agg({
    "total_bags_sold":"sum",
    "billed_customers":"sum",
    "rice_customers":"sum",
    "month_repeat_rate_pct":"mean",
    "sampling_reach_pct":"mean",
    "funnel_lapsers":"sum"
}).to_dict()

conversion_rate = (agg["billed_customers"] / agg["rice_customers"] * 100) if agg["rice_customers"] > 0 else 0

# KPI Cards
st.subheader("📌 Overall Performance Snapshot")
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Bags Sold", f"{agg['total_bags_sold']}")
col2.metric("Billed Customers", f"{agg['billed_customers']}")
col3.metric("Conversion Rate", f"{conversion_rate:.1f}%")
col4.metric("Repeat Rate", f"{agg['month_repeat_rate_pct']:.1f}%")
col5.metric("Sampling Reach", f"{agg['sampling_reach_pct']:.1f}%")
col6.metric("Lapsers", f"{agg['funnel_lapsers']}")

# Charts
st.subheader("📈 Key Performance Trends")

# Conversion trend per week
conv_data = df[df["month"] == selected_month].groupby("week_in_month").agg(
    billed=("billed_customers","sum"), rice=("rice_customers","sum")
).reset_index()
conv_data["conversion_rate"] = conv_data["billed"] / conv_data["rice"] * 100
fig1 = px.line(conv_data, x="week_in_month", y="conversion_rate", markers=True, title="Weekly Conversion Rate (%)")
st.plotly_chart(fig1, use_container_width=True)

# Sampling reach by supervisor
fig2 = px.bar(filtered_df, x="supervisor", y="sampling_reach_pct", color="supervisor",
             title="Sampling Reach by Supervisor", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# Sales by supervisor
fig3 = px.bar(filtered_df, x="supervisor", y="total_bags_sold", color="supervisor",
             title="Bags Sold per Supervisor", text_auto=True)
st.plotly_chart(fig3, use_container_width=True)

# Lapsers trend
lapsers_data = df[df["month"] == selected_month].groupby("week_in_month")["funnel_lapsers"].sum().reset_index()
fig4 = px.line(lapsers_data, x="week_in_month", y="funnel_lapsers", markers=True, title="Lapsers Trend")
st.plotly_chart(fig4, use_container_width=True)

# Product Portfolio Breakdown
portfolio_cols = ["samples_premium","samples_select","samples_everyday","samples_sella","samples_sonamasoori"]
portfolio = filtered_df[portfolio_cols].sum().reset_index()
portfolio.columns = ["Product","Samples"]
fig5 = px.pie(portfolio, names="Product", values="Samples", title="Product Portfolio Sampling")
st.plotly_chart(fig5, use_container_width=True)

# Alerts Section
st.subheader("⚠️ Critical Performance Concerns")
if agg['month_repeat_rate_pct'] < 75:
    st.error(f"Repeat rate dropped to {agg['month_repeat_rate_pct']:.1f}% - Customer retention risk!")
if (filtered_df.groupby("supervisor")["sampling_reach_pct"].mean().min()) < 65:
    underperf = filtered_df.loc[filtered_df["sampling_reach_pct"].idxmin()]["supervisor"]
    st.warning(f"{underperf} sampling reach is below team average and requires intervention.")

# Executive Summary (basic)
st.subheader("📝 Executive Summary")
summary_text = f'''
For **{selected_month}**, the team sold **{agg['total_bags_sold']} bags** with a conversion rate of **{conversion_rate:.1f}%**.  
Repeat rate averaged **{agg['month_repeat_rate_pct']:.1f}%** and sampling reach was **{agg['sampling_reach_pct']:.1f}%**.  
Total lapsers recorded were **{agg['funnel_lapsers']}**.
'''
st.markdown(summary_text)

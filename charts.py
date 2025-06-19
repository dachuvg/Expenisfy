import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px


def select_year(df):
    df_copy = df.copy()
    df_copy['Date'] = pd.to_datetime(df_copy['Date'], dayfirst=True, errors='coerce')
    df_copy['Total Spend'] = df_copy['Total Spend'].astype(float)
    years = sorted(df_copy['Date'].dt.year.dropna().unique())
    selected_year = st.selectbox("Select Year", years)
    df_copy = df_copy[df_copy['Date'].dt.year == selected_year]
    
    return selected_year,df_copy


def category_pie(df):
    if df.empty:
        st.info("No data available to plot category pie chart.")
        return

    df['Total Spend'] = df['Total Spend'].astype(float)
    category_grouped = df.groupby('Category')['Total Spend'].sum().reset_index()

    fig = px.pie(
        category_grouped,
        values='Total Spend',
        names='Category',
        hole=0.4  
    )

    st.subheader("Spending by Category")
    st.plotly_chart(fig, use_container_width=True)

def filter_by_year_range(df):
    st.subheader("Yearly Expenses")

    years = df['Date'].dt.year.dropna().unique()
    min_year = int(years.min())
    max_year = int(years.max())

    year_range = st.slider("Select year range", min_year, max_year, (min_year, max_year+1))

    df_filtered = df[(df['Date'].dt.year >= year_range[0]) & (df['Date'].dt.year <= year_range[1])]
    return df_filtered


def monthly(df):
    if df.empty:
        st.info("No data available for monthly chart.")
        return

    df_copy = df.copy()
    df_copy['Date'] = pd.to_datetime(df_copy['Date'], dayfirst=True, errors='coerce')
    df_copy['Total Spend'] = df_copy['Total Spend'].astype(float)
    
    # years = sorted(df_copy['Date'].dt.year.dropna().unique())
    # selected_year = st.selectbox("Select Year", years)
    # df_copy = df_copy[df_copy['Date'].dt.year == selected_year]
    
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    grouped = (
        df_copy.groupby(df_copy['Date'].dt.month)['Total Spend']
          .sum()
          .reindex(range(1, 13), fill_value=0)
    )

    df_grouped = pd.DataFrame({
        'Month': [month_names[i - 1] for i in grouped.index],
        'Total Spend': grouped.values
    })

    df_grouped['Month'] = pd.Categorical(df_grouped['Month'], categories=month_names, ordered=True)

    st.subheader("📆 Monthly Expenses")
    st.bar_chart(df_grouped.set_index("Month"))
    
    

def yearly(df):
    if df.empty:
        st.info("No data available for yearly chart.")
        return

    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Total Spend'] = df['Total Spend'].astype(float)

    years = np.arange(df['Date'].dt.year.min(), df['Date'].dt.year.max() + 1)
    grouped_df = (
        df.groupby(df['Date'].dt.year)['Total Spend']
          .sum()
          .reindex(years, fill_value=0)
    )
    
    st.bar_chart(grouped_df)

import calendar
def daily(selected_year,df):
    st.subheader(f"Daily Expenses")
    if df.empty:
        st.info("No data available.")
        return

    df_year = df.copy()


    # years = sorted(df_copy['Date'].dt.year.dropna().unique())
    # selected_year = st.selectbox("Select Year", years)

    # df_year = df_copy[df_copy['Date'].dt.year == selected_year]

    months = sorted(df_year['Date'].dt.month.unique())
    month_map = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    month_names = [month_map[m] for m in months]
    selected_month_name = st.selectbox("Select Month", month_names)
    selected_month = {v: k for k, v in month_map.items()}[selected_month_name]

    df_month = df_year[df_year['Date'].dt.month == selected_month]

    _, num_days = calendar.monthrange(selected_year, selected_month)

    daily_totals = (
        df_month.groupby(df_month['Date'].dt.day)['Total Spend']
        .sum()
        .reindex(range(1, num_days + 1), fill_value=0)
    )
    
    daily_totals.index.name = 'Day'
    daily_totals = daily_totals.reset_index()

    
    st.bar_chart(daily_totals.set_index("Day"))
    avg_spend = daily_totals["Total Spend"].mean()
    st.markdown(f"**📈 Avg Spend for {selected_month_name}:** `{avg_spend:.2f}`")


def calc_avg(df):
    df_copy = df.copy()
    df_copy['Date'] = pd.to_datetime(df_copy['Date'], dayfirst=True, errors='coerce')
    df_copy['Total Spend'] = df_copy['Total Spend'].astype(float)


    daily_totals_all = df_copy.groupby(df_copy['Date'].dt.date)['Total Spend'].sum()

    overall_avg = daily_totals_all.mean()
    
    return overall_avg



import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np

# Page Config

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Header

st.title("Bike Sharing Dashboard")
st.markdown("Analisis data peminjaman sepeda per jam — **Capital Bikeshare System**")
st.divider()

# Load Data
def load_data():
    df = pd.read_csv("hour.csv")
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

df = load_data()
df["bulan"] = df["dteday"].dt.to_period("M")

# Mapping 
season_map    = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
weather_map   = {1: "Clear", 2: "Mist/Cloudy", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}
weekday_map   = {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"}
year_map      = {0: "2011", 1: "2012"}
month_map     = {1: "Januari", 2: "Februari", 3:"Maret", 4:"April", 5:"Mei", 6:"Juni", 7:"Juli", 8:"Agustus", 9:"September", 10:"Oktober", 11:"November", 12:"Desember"}
workingday_map = {1: "Yes", 0: "No"}
holiday_map = {1: "Yes", 0: "No"}

# Sidebar Filter
st.sidebar.header("🎛️ Filter Data")

selected_year = st.sidebar.multiselect(
    "Tahun",
    options=sorted(df["yr"].unique()),
    default=sorted(df["yr"].unique()),
    format_func=lambda x: year_map[x],
)

selected_season = st.sidebar.multiselect(
    "Musim",
    options=sorted(df["season"].unique()),
    default=sorted(df["season"].unique()),
    format_func=lambda x: season_map[x],
)

selected_weather = st.sidebar.multiselect(
    "Cuaca",
    options=sorted(df["weathersit"].unique()),
    default=sorted(df["weathersit"].unique()),
    format_func=lambda x: weather_map.get(x, str(x)),
)

# Filter dataframe
df_filtered = df[
    (df["yr"].isin(selected_year)) &
    (df["season"].isin(selected_season)) &
    (df["weathersit"].isin(selected_weather))
]

# Metrik
k1, k2, k3, k4 = st.columns(4)

with k1:
    with st.container(border=True):
        st.metric("Total Peminjaman", f"{df_filtered['cnt'].sum():,}")

with k2:
    with st.container(border=True):
        st.metric("Rata-rata per Jam", f"{df_filtered['cnt'].mean():.1f}")

with k3:
    with st.container(border=True):
        st.metric("Total Pengguna Kasual", f"{df_filtered['casual'].sum():,}")

with k4:
    with st.container(border=True):
        st.metric("Total Pengguna Terdaftar", f"{df_filtered['registered'].sum():,}")

st.divider()

# ROW 1: TREN BULANAN
st.subheader("📈 Tren Peminjaman Bulanan")
monthly = df_filtered.groupby("bulan")["cnt"].sum().reset_index()
monthly["bulan"] = monthly["bulan"].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(12, 4))
ax.fill_between(monthly["bulan"], monthly["cnt"], alpha=0.25, color="#1a73e8")
ax.plot(monthly["bulan"], monthly["cnt"], color="#1a73e8", linewidth=1.5, marker="o", markersize=4)
ax.set_xlabel("Bulan", fontsize=8)
ax.set_ylabel("Total Peminjaman", fontsize=8)
ax.tick_params(axis="both", labelsize=7)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x/1000):,}K"))
ax.grid(axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
st.pyplot(fig)

col1, col2 = st.columns([6, 5])

with col1:
    st.subheader("🕐 Heatmap: Jam vs Hari dalam Seminggu")
    pivot = df_filtered.pivot_table(values="cnt", index="weekday", columns="hr", aggfunc="mean")
    pivot.index = [weekday_map[i] for i in pivot.index]
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    sns.heatmap(pivot, cmap="YlOrRd", ax=ax3, linewidths=0.3,
                cbar_kws={"label": "Avg Peminjaman"}, fmt=".0f", annot=False)
    ax3.set_xlabel("Jam")
    ax3.set_ylabel("Hari")
    fig3.tight_layout()
    fig3.set_size_inches(14, 5)
    st.pyplot(fig3, use_container_width=True)

with col2:
    st.subheader("🌤️ Peminjaman per Musim")
    season_data = df_filtered.groupby("season")["cnt"].sum().reset_index()
    season_data["label"] = season_data["season"].map(season_map)
    colors = ["#FF6B9D", "#FFD93D", "#6BCB77", "#4D96FF"]
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    bars = ax2.barh(season_data["label"], season_data["cnt"], color=colors[:len(season_data)])
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax2.set_xlabel("Total Peminjaman")
    for bar in bars:
        ax2.text(bar.get_width() + 500, bar.get_y() + bar.get_height()/2,
                 f"{int(bar.get_width()):,}", va="center", fontsize=9)
    ax2.grid(axis="x", linestyle="--", alpha=0.4)
    fig2.tight_layout()
    fig2.set_size_inches(14, 5)
    st.pyplot(fig2, use_container_width=True)
    # st.pyplot(fig2)

# ROW 3: PENGARUH SUHU & RATA-RATA PER JAM
col5, col6 = st.columns(2)

with col5:
    st.subheader("🌡️ Pengaruh Suhu terhadap Peminjaman")
    sample = df_filtered.sample(min(2000, len(df_filtered)), random_state=42)
    fig5, ax5 = plt.subplots(figsize=(6, 4))
    scatter = ax5.scatter(
        sample["temp"] * 41,   # denormalize ke °C (temp_actual = temp * 41)
        sample["cnt"],
        c=sample["cnt"], cmap="coolwarm",
        alpha=0.4, s=15, edgecolors="none"
    )
    plt.colorbar(scatter, ax=ax5, label="Jumlah Peminjaman")
    ax5.set_xlabel("Suhu Aktual (°C)")
    ax5.set_ylabel("Jumlah Peminjaman")
    ax5.grid(linestyle="--", alpha=0.4)
    fig5.tight_layout()
    st.pyplot(fig5)

with col6:
    st.subheader("⏰ Rata-rata Peminjaman per Jam")
    hourly = df_filtered.groupby("hr")["cnt"].mean().reset_index()
    fig6, ax6 = plt.subplots(figsize=(6, 4))
    ax6.bar(hourly["hr"], hourly["cnt"],
            color=["#1a73e8" if (h in [7,8,9,17,18,19]) else "#b3cde3" for h in hourly["hr"]])
    ax6.set_xlabel("Jam")
    ax6.set_ylabel("Rata-rata Peminjaman")
    ax6.set_xticks(range(0, 24))
    ax6.grid(axis="y", linestyle="--", alpha=0.4)
    ax6.annotate("Jam sibuk", xy=(8, hourly[hourly["hr"]==8]["cnt"].values[0]),
                 xytext=(10, hourly["cnt"].max() * 0.9),
                 arrowprops=dict(arrowstyle="->", color="gray"), fontsize=9, color="gray")
    fig6.tight_layout()
    st.pyplot(fig6)

# ROW 4: TABEL DATA MENTAH (OPSIONAL)
with st.expander("📋 Lihat Data Mentah"):
    df_display = df_filtered.copy()
    df_display = df_display.drop('bulan', axis=1)
    
    # Mapping nilai
    df_display["season"]     = df_display["season"].map(season_map)
    df_display["weathersit"] = df_display["weathersit"].map(weather_map)
    df_display["weekday"]    = df_display["weekday"].map(weekday_map)
    df_display["yr"]         = df_display["yr"].map(year_map)
    df_display["mnth"]       = df_display["mnth"].map(month_map)
    df_display["workingday"] = df_display["workingday"].map(workingday_map)
    df_display["holiday"]    = df_display["holiday"].map(holiday_map)

    # Rename kolom
    st.dataframe(
        df_display.rename(columns={
            "dteday": "Tanggal", "hr": "Jam", "season": "Musim",
            "weathersit": "Cuaca", "temp": "Temp (norm)", "yr": "Tahun",
            "weekday": "Hari", "hum": "Humidity", "windspeed": "Windspeed",
            "casual": "Kasual", "registered": "Terdaftar", "cnt": "Total"
        }),
        use_container_width=True,
        height=300,
    )
    st.caption(f"Menampilkan {len(df_display):,} baris data.")

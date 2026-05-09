import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Bird Biodiversity Dashboard",
    page_icon="🦜",
    layout="wide"
)

# ----------------------------
# 🎨 UI STYLE (CARDS + BUTTONS)
# ----------------------------
st.markdown("""
<style>
.card-blue, .card-green, .card-purple, .card-orange {
    padding: 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    font-weight: 500;
    transition: all 0.3s ease-in-out;
    cursor: pointer;
}

/* KPI Colors */
.card-blue { background: linear-gradient(135deg, #3b82f6, #1e3a8a); }
.card-green { background: linear-gradient(135deg, #22c55e, #166534); }
.card-purple { background: linear-gradient(135deg, #a855f7, #581c87); }
.card-orange { background: linear-gradient(135deg, #f97316, #7c2d12); }

/* Hover Effect */
.card-blue:hover,
.card-green:hover,
.card-purple:hover,
.card-orange:hover {
    transform: translateY(-8px) scale(1.03);
    box-shadow: 0 15px 30px rgba(0,0,0,0.4);
}

/* NAV BUTTON STYLE */
.nav-btn {
    padding: 12px 18px;
    border-radius: 12px;
    background: linear-gradient(135deg, #1f2937, #111827);
    color: white;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease-in-out;
    font-weight: 500;
    border: 1px solid #374151;
}

.nav-btn:hover {
    transform: translateY(-4px);
    background: linear-gradient(135deg, #3b82f6, #1e3a8a);
    box-shadow: 0 10px 20px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# LOAD DATA
# ----------------------------
@st.cache_data
def load_data():
    files = {
        "Forest": "Bird_Monitoring_Data_FOREST.XLSX",
        "Grassland": "Bird_Monitoring_Data_GRASSLAND.XLSX"
    }

    data = []
    for habitat, file in files.items():
        xls = pd.ExcelFile(file)
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            df["Habitat"] = habitat
            df["Park"] = sheet
            data.append(df)

    df = pd.concat(data)
    df.columns = df.columns.str.strip().str.replace(" ", "_")
    return df

df = load_data()

# ----------------------------
# CLEANING
# ----------------------------
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Month'] = df['Date'].dt.month
df['Year'] = df['Date'].dt.year

def season(m):
    if pd.isnull(m):
        return None
    return ["Winter","Winter","Summer","Summer","Summer","Monsoon","Monsoon","Monsoon","Autumn","Autumn","Autumn","Winter"][int(m)-1]

df['Season'] = df['Month'].apply(season)
df = df.dropna(subset=['Common_Name'])

# ----------------------------
# FILTERS
# ----------------------------
st.sidebar.title("🔍 Filters")

habitat = st.sidebar.multiselect("Habitat", df['Habitat'].unique(), default=df['Habitat'].unique())
park = st.sidebar.multiselect("Park", df['Park'].unique(), default=df['Park'].unique())
year = st.sidebar.multiselect("Year", df['Year'].dropna().unique(), default=df['Year'].dropna().unique())

df_filtered = df[
    (df['Habitat'].isin(habitat)) &
    (df['Park'].isin(park)) &
    (df['Year'].isin(year))
].copy()

# ----------------------------
# HEADER
# ----------------------------
st.title("🦅 Bird Biodiversity Intelligence Dashboard: Forest & Grassland Insights")

st.markdown(
    "<p style='text-align: center; font-size:18px; color:#9CA3AF;'>"
    "Turning Bird Observation Data into Actionable Insights for Conservation and Ecosystem Management"
    "</p>",
    unsafe_allow_html=True
)

# ----------------------------
# KPI CARDS
# ----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.markdown(f"<div class='card-blue'>Observations<br><h2>{len(df_filtered)}</h2></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card-green'>Species<br><h2>{df_filtered['Common_Name'].nunique()}</h2></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card-purple'>Parks<br><h2>{df_filtered['Park'].nunique()}</h2></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card-orange'>Habitats<br><h2>{df_filtered['Habitat'].nunique()}</h2></div>", unsafe_allow_html=True)


# 🔥 SPACE BETWEEN KPI & NAV
st.markdown("<br><br>", unsafe_allow_html=True)


# ----------------------------
# NAVIGATION BUTTONS (ACTIVE STATE FIXED)
# ----------------------------
if "tab" not in st.session_state:
    st.session_state.tab = "Temporal"

cols = st.columns(6)

def styled_button(col, label, key):

    is_active = st.session_state.tab == key

    # 🎨 Dynamic style
    bg = "linear-gradient(135deg,#3b82f6,#1e3a8a)" if is_active else "linear-gradient(135deg,#1f2937,#111827)"
    shadow = "0 10px 20px rgba(0,0,0,0.3)" if is_active else "none"
    weight = "600" if is_active else "500"

    # Button with custom CSS
    if col.markdown(
        f"""
        <style>
        div[data-testid="stButton"] button[key="{key}"] {{
            background: {bg};
            color: white;
            border-radius: 12px;
            padding: 10px;
            font-weight: {weight};
            border: 1px solid #374151;
            box-shadow: {shadow};
        }}
        </style>
        """,
        unsafe_allow_html=True
    ):
        pass

    if col.button(label, key=key):
        st.session_state.tab = key


# 🔥 Create buttons
styled_button(cols[0], "📊 Temporal", "Temporal")
styled_button(cols[1], "🌍 Spatial", "Spatial")
styled_button(cols[2], "🐦 Species", "Species")
styled_button(cols[3], "🌦 Environment", "Environment")
styled_button(cols[4], "📍 Map", "Map")
styled_button(cols[5], "🧾 SQL", "SQL")

# ----------------------------
# 📊 TEMPORAL (FINAL PROFESSIONAL VERSION)
# ----------------------------
if st.session_state.tab == "Temporal":

    # Ensure clean datetime
    df_temp = df_filtered.copy()
    df_temp['Date'] = pd.to_datetime(df_temp['Date'], errors='coerce')
    df_temp = df_temp.dropna(subset=['Date'])

    df_temp['Year'] = df_temp['Date'].dt.year
    df_temp['Month'] = df_temp['Date'].dt.month
    df_temp['Month_Name'] = df_temp['Date'].dt.strftime('%b')

    # =========================================================
    # 📅 MONTHLY TREND (MOST IMPORTANT CHART)
    # =========================================================
    st.subheader("📅 Monthly Bird Activity Trend")

    month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    monthly = df_temp.groupby('Month_Name').size().reindex(month_order).reset_index(name='Count')
    monthly = monthly.dropna()

    if not monthly.empty:
        st.plotly_chart(
            px.line(
                monthly,
                x='Month_Name',
                y='Count',
                markers=True,
                title="Monthly Bird Observation Pattern"
            ),
            width="stretch"
        )
    else:
        st.warning("No monthly data available")

    # =========================================================
    # 🌦 SEASONAL DISTRIBUTION
    # =========================================================
    st.subheader("🌦 Seasonal Distribution")

    season_df = df_temp.groupby("Season").size().reset_index(name="Count")

    if not season_df.empty:
        st.plotly_chart(
            px.bar(
                season_df,
                x="Season",
                y="Count",
                color="Season",
                title="Bird Observations Across Seasons"
            ),
            width="stretch"
        )

    # =========================================================
    # 📈 YEARLY TREND (WITH SMOOTHING)
    # =========================================================
    st.subheader("📈 Yearly Trend (Smoothed)")

    year_data = df_temp.groupby('Year').size().reset_index(name='Count')

    if not year_data.empty:
        year_data['Rolling'] = year_data['Count'].rolling(2).mean()

        fig = px.line(
            year_data,
            x='Year',
            y='Count',
            markers=True,
            title="Yearly Bird Observations"
        )

        fig.add_scatter(
            x=year_data['Year'],
            y=year_data['Rolling'],
            mode='lines',
            name='Trend (Smoothed)'
        )

        st.plotly_chart(fig, width="stretch")

    # =========================================================
    # 🔥 PEAK ACTIVITY MONTH (INSIGHT CHART)
    # =========================================================
    st.subheader("🔥 Peak Activity Month")

    peak_month = df_temp['Month_Name'].value_counts().reset_index()
    peak_month.columns = ['Month', 'Count']

    if not peak_month.empty:
        st.plotly_chart(
            px.bar(
                peak_month,
                x='Month',
                y='Count',
                color='Count',
                title="Peak Bird Activity by Month"
            ),
            width="stretch"
        )

    # =========================================================
    # 📊 YEAR vs MONTH HEATMAP (FIXED)
    # =========================================================
    st.subheader("📊 Activity Heatmap (Year vs Month)")

    heat = df_temp.groupby(['Year','Month']).size().reset_index(name='Count')

    if not heat.empty:
        st.plotly_chart(
            px.density_heatmap(
                heat,
                x='Month',
                y='Year',
                z='Count',
                color_continuous_scale="Viridis",
                title="Bird Activity Intensity"
            ),
            width="stretch"
        )

# ----------------------------
# 🌍 SPATIAL (PROFESSIONAL + COLORED)
# ----------------------------
elif st.session_state.tab == "Spatial":

    st.subheader("🌍 Spatial Biodiversity Insights")

    # =========================================================
    # 📍 Location Type Distribution
    # =========================================================
    if 'Location_Type' in df_filtered.columns:

        loc = df_filtered.groupby("Location_Type").size().reset_index(name="Count")

        st.plotly_chart(
            px.bar(
                loc,
                x="Location_Type",
                y="Count",
                color="Location_Type",
                color_discrete_sequence=px.colors.qualitative.Set2,
                title="Observation Distribution by Location Type"
            ),
            width="stretch"
        )

        # % Contribution Pie
        loc['Percentage'] = (loc['Count'] / loc['Count'].sum()) * 100

        st.plotly_chart(
            px.pie(
                loc,
                names='Location_Type',
                values='Percentage',
                color_discrete_sequence=px.colors.qualitative.Pastel,
                title="Contribution of Each Location Type (%)"
            ),
            width="stretch"
        )

    # =========================================================
    # 🌿 BIODIVERSITY HOTSPOTS
    # =========================================================
    if 'Location_Type' in df_filtered.columns and 'Common_Name' in df_filtered.columns:

        hotspot = df_filtered.groupby('Location_Type')['Common_Name'].nunique().reset_index()
        hotspot.columns = ['Location_Type', 'Species_Count']

        st.subheader("🔥 Biodiversity Hotspots (Species Richness)")

        st.plotly_chart(
            px.bar(
                hotspot,
                x='Location_Type',
                y='Species_Count',
                color='Location_Type',
                color_discrete_sequence=px.colors.qualitative.Bold,
                title="Unique Species Count per Location"
            ),
            width="stretch"
        )

    # =========================================================
    # 🏞 TOP OBSERVATION PLOTS
    # =========================================================
    if 'Plot_Name' in df_filtered.columns:

        plot = df_filtered['Plot_Name'].value_counts().head(10).reset_index()
        plot.columns = ['Plot', 'Count']

        st.subheader("🏞 Top Observation Plots")

        st.plotly_chart(
            px.bar(
                plot,
                x='Plot',
                y='Count',
                color='Plot',
                color_discrete_sequence=px.colors.qualitative.Dark24,
                title="Top 10 Observation Plots"
            ),
            width="stretch"
        )

    # =========================================================
    # 🌳 HABITAT vs LOCATION
    # =========================================================
    if 'Habitat' in df_filtered.columns and 'Location_Type' in df_filtered.columns:

        st.subheader("🌳 Habitat vs Location Type")

        cross = df_filtered.groupby(['Habitat','Location_Type']).size().reset_index(name='Count')

        st.plotly_chart(
            px.bar(
                cross,
                x='Location_Type',
                y='Count',
                color='Habitat',
                barmode='group',
                color_discrete_sequence=px.colors.qualitative.Safe,
                title="Habitat Comparison Across Locations"
            ),
            width="stretch"
        )

    # =========================================================
    # 📊 PARK-LEVEL ACTIVITY
    # =========================================================
    st.subheader("🏞 Park-Level Activity")

    park_data = df_filtered['Park'].value_counts().reset_index()
    park_data.columns = ['Park', 'Count']

    st.plotly_chart(
        px.bar(
            park_data,
            x='Park',
            y='Count',
            color='Park',
            color_discrete_sequence=px.colors.qualitative.Vivid,
            title="Observation Count per Park"
        ),
        width="stretch"
    )

    
# ----------------------------
# 🐦 SPECIES (PROFESSIONAL VERSION)
# ----------------------------
elif st.session_state.tab == "Species":

    st.subheader("🐦 Species Analysis & Biodiversity Insights")

    # =========================================================
    # 🥇 TOP SPECIES DISTRIBUTION
    # =========================================================
    st.markdown("### 🥇 Top 10 Most Observed Bird Species")

    top = df_filtered['Common_Name'].value_counts().head(10).reset_index()
    top.columns = ['Species','Count']

    st.plotly_chart(
        px.bar(
            top,
            x='Species',
            y='Count',
            color='Count',
            color_continuous_scale="Viridis",
            title="Top 10 Species by Observation Count"
        ),
        width="stretch"
    )

    # =========================================================
    # 🌿 SPECIES DIVERSITY METRICS (KPI CARDS - PROFESSIONAL)
    # =========================================================
    st.markdown("### 🌿 Biodiversity Metrics")

    # 🎨 KPI CARD STYLE
    st.markdown("""
    <style>
        .kpi-card {
            padding: 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .kpi-blue {
            background: linear-gradient(135deg, #3b82f6, #1e3a8a);
        }
        .kpi-green {
            background: linear-gradient(135deg, #22c55e, #166534);
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Common Species KPI
    col1.markdown(f"""
    <div class="kpi-card kpi-blue">
        <div style="font-size:16px;">🌿 Common Species</div>
        <div style="font-size:32px;">{df_filtered['Common_Name'].nunique()}</div>
    </div>
    """, unsafe_allow_html=True)

    # Scientific Species KPI
    if 'Scientific_Name' in df_filtered.columns:
        col2.markdown(f"""
        <div class="kpi-card kpi-green">
            <div style="font-size:16px;">🧬 Scientific Species</div>
            <div style="font-size:32px;">{df_filtered['Scientific_Name'].nunique()}</div>
        </div>
        """, unsafe_allow_html=True)



    # =========================================================
    # 📊 SPECIES SHARE (IMPORTANT INSIGHT)
    # =========================================================
    st.markdown("### 📊 Species Contribution (%)")

    top['Percentage'] = (top['Count'] / top['Count'].sum()) * 100

    st.plotly_chart(
        px.pie(
            top,
            names='Species',
            values='Percentage',
            title="Contribution of Top Species",
            color_discrete_sequence=px.colors.qualitative.Set3
        ),
        width="stretch"
    )

    # =========================================================
    # ⚧ SEX RATIO ANALYSIS
    # =========================================================
    if 'Sex' in df_filtered.columns:

        st.markdown("### ⚧ Sex Distribution of Observed Birds")

        sex = df_filtered['Sex'].value_counts().reset_index()
        sex.columns = ['Sex','Count']

        st.plotly_chart(
            px.pie(
                sex,
                names='Sex',
                values='Count',
                title="Male vs Female Distribution",
                color_discrete_sequence=["#60a5fa", "#f472b6", "#94a3b8"]
            ),
            width="stretch"
        )

    # =========================================================
    # 🌍 SPECIES DISTRIBUTION BY HABITAT (VERY IMPORTANT 🔥)
    # =========================================================
    if 'Habitat' in df_filtered.columns:

        st.markdown("### 🌍 Species Distribution Across Habitats")

        habitat_species = df_filtered.groupby(['Habitat'])['Common_Name'].nunique().reset_index()
        habitat_species.columns = ['Habitat','Species_Count']

        st.plotly_chart(
            px.bar(
                habitat_species,
                x='Habitat',
                y='Species_Count',
                color='Species_Count',
                color_continuous_scale="Turbo",
                title="Unique Species Count per Habitat"
            ),
            width="stretch"
        )

    # =========================================================
    # 🎯 IDENTIFICATION METHOD ANALYSIS (ACTIVITY)
    # =========================================================
    if 'ID_Method' in df_filtered.columns:

        st.markdown("### 🎯 Bird Activity Identification Methods")

        method = df_filtered['ID_Method'].value_counts().head(10).reset_index()
        method.columns = ['Method','Count']

        st.plotly_chart(
            px.bar(
                method,
                x='Method',
                y='Count',
                color='Count',
                color_continuous_scale="Plasma",
                title="Top Identification Methods (e.g., Singing, Visual)"
            ),
            width="stretch"
        )

# ----------------------------
# 🌦 ENVIRONMENT + BEHAVIOR + OBSERVER + CONSERVATION
# ----------------------------
elif st.session_state.tab == "Environment":

    st.subheader("🌦 Environmental & Behavioral Intelligence")

    # ---------------- Weather & Environment ----------------
    for col in ['Temperature','Humidity','Wind','Sky','Disturbance']:
        if col in df_filtered.columns:

            data = df_filtered[col].value_counts().head(10).reset_index()
            data.columns = [col, 'Count']

            st.markdown(f"### 🌍 Impact of {col} on Bird Observations")

            st.plotly_chart(
                px.bar(
                    data,
                    x=col,
                    y='Count',
                    color='Count',
                    color_continuous_scale="Viridis",
                    title=f"{col} Distribution Across Observations"
                ),
                width="stretch"
            )

    # ---------------- Correlation (PRO LEVEL 🔥) ----------------
    if 'Temperature' in df_filtered.columns and 'Humidity' in df_filtered.columns:

        st.markdown("### 🔥 Environmental Correlation (Temperature vs Humidity)")

        corr_df = df_filtered[['Temperature','Humidity']].dropna()

        if not corr_df.empty:
            st.plotly_chart(
                px.scatter(
                    corr_df,
                    x='Temperature',
                    y='Humidity',
                    trendline="ols",
                    title="Temperature vs Humidity Relationship"
                ),
                width="stretch"
            )

    # ---------------- Distance Analysis ----------------
    if 'Distance' in df_filtered.columns:
        st.markdown("### 📏 Distance-Based Observation Analysis")

        st.plotly_chart(
            px.histogram(
                df_filtered,
                x='Distance',
                nbins=30,
                color_discrete_sequence=['#3b82f6'],
                title="Distribution of Observation Distance"
            ),
            width="stretch"
        )

    # ---------------- Flyover Behavior ----------------
    if 'Flyover_Observed' in df_filtered.columns:
        fly = df_filtered['Flyover_Observed'].value_counts().reset_index()
        fly.columns = ['Flyover', 'Count']

        st.markdown("### 🕊 Flyover Behavior Patterns")

        st.plotly_chart(
            px.bar(
                fly,
                x='Flyover',
                y='Count',
                color='Count',
                color_continuous_scale="Plasma",
                title="Flyover Observation Frequency"
            ),
            width="stretch"
        )

    # ---------------- Observer Analysis ----------------
    if 'Observer' in df_filtered.columns:
        obs = df_filtered['Observer'].value_counts().head(10).reset_index()
        obs.columns = ['Observer', 'Count']

        st.markdown("### 👤 Observer Contribution Analysis")

        st.plotly_chart(
            px.bar(
                obs,
                x='Observer',
                y='Count',
                color='Count',
                color_continuous_scale="Turbo",
                title="Top Observers by Number of Observations"
            ),
            width="stretch"
        )

    # ---------------- Visit Patterns ----------------
    if 'Visit' in df_filtered.columns:
        visit = df_filtered['Visit'].value_counts().reset_index()
        visit.columns = ['Visit', 'Count']

        st.markdown("### 🔁 Visit Frequency Analysis")

        st.plotly_chart(
            px.bar(
                visit,
                x='Visit',
                y='Count',
                color='Count',
                color_continuous_scale="Cividis",
                title="Distribution of Visit Counts"
            ),
            width="stretch"
        )

    # ---------------- Watchlist (Conservation Risk) ----------------
    if 'PIF_Watchlist_Status' in df_filtered.columns:
        watch = df_filtered['PIF_Watchlist_Status'].value_counts().reset_index()
        watch.columns = ['Status', 'Count']

        st.markdown("### ⚠ Conservation Watchlist Status")

        st.plotly_chart(
            px.bar(
                watch,
                x='Status',
                y='Count',
                color='Count',
                color_continuous_scale="Reds",
                title="At-Risk Species Distribution"
            ),
            width="stretch"
        )

    # ---------------- Conservation Status ----------------
    if 'Regional_Stewardship_Status' in df_filtered.columns:
        reg = df_filtered['Regional_Stewardship_Status'].value_counts().reset_index()
        reg.columns = ['Status', 'Count']

        st.markdown("### 🌿 Regional Conservation Priority")

        st.plotly_chart(
            px.bar(
                reg,
                x='Status',
                y='Count',
                color='Count',
                color_continuous_scale="Greens",
                title="Species Conservation Priority Levels"
            ),
            width="stretch"
        )

        
# ----------------------------
# 📍 MAP (PROFESSIONAL ADVANCED VERSION)
# ----------------------------
elif st.session_state.tab == "Map":

    st.subheader("🗺 Geographic Bird Observation Insights")

    # =========================================================
    # 📌 PARK COORDINATES MAPPING
    # =========================================================
    park_coords = {
        "ANTI":[39.46,-77.73],"CATO":[39.65,-77.45],"CHOH":[39.3,-77.8],
        "GWMP":[38.9,-77.1],"HAFE":[39.32,-77.73],"MANA":[38.82,-77.52],
        "MONO":[39.35,-77.43],"NACE":[38.89,-76.99],"PRWI":[38.61,-77.4],
        "ROCR":[38.94,-77.05],"WOTR":[38.92,-77.27]
    }

    df_map = df_filtered.copy()

    df_map['lat'] = df_map['Park'].map(lambda x: park_coords.get(x,[None,None])[0])
    df_map['lon'] = df_map['Park'].map(lambda x: park_coords.get(x,[None,None])[1])

    df_map = df_map.dropna(subset=['lat','lon'])

    # =========================================================
    # 🧭 MAIN INTERACTIVE MAP (UPDATED API)
    # =========================================================
    st.markdown("### 📍 Bird Observation Locations")

    fig_map = px.scatter_map(
        df_map,
        lat="lat",
        lon="lon",
        color="Habitat",
        hover_name="Park",
        size_max=12,
        zoom=5,
        height=500
    )

    fig_map.update_layout(
        mapbox_style="carto-darkmatter",
        margin=dict(l=0, r=0, t=30, b=0)
    )

    st.plotly_chart(fig_map, width="stretch")

    # =========================================================
    # 🔥 DENSITY HEATMAP (ADVANCED INSIGHT)
    # =========================================================
    st.markdown("### 🔥 Observation Density Map")

    density = df_map.groupby(['lat','lon']).size().reset_index(name='Count')

    fig_density = px.density_map(
        density,
        lat="lat",
        lon="lon",
        z="Count",
        radius=20,
        center=dict(lat=38.9, lon=-77.2),
        zoom=5,
        height=500,
        color_continuous_scale="Turbo"
    )

    fig_density.update_layout(mapbox_style="carto-darkmatter")

    st.plotly_chart(fig_density, width="stretch")

    # =========================================================
    # 📊 TOP PARK ANALYSIS (MAP SUPPORT CHART)
    # =========================================================
    st.markdown("### 🏞 Top Parks by Bird Activity")

    park_data = df_map['Park'].value_counts().reset_index()
    park_data.columns = ['Park', 'Observations']

    st.plotly_chart(
        px.bar(
            park_data,
            x='Park',
            y='Observations',
            color='Observations',
            color_continuous_scale="Viridis",
            title="Observation Count per Park"
        ),
        width="stretch"
    )

    # =========================================================
    # 🌿 HABITAT DISTRIBUTION ON MAP
    # =========================================================
    st.markdown("### 🌿 Habitat Distribution (%)")

    habitat_dist = df_map['Habitat'].value_counts().reset_index()
    habitat_dist.columns = ['Habitat','Count']

    st.plotly_chart(
        px.pie(
            habitat_dist,
            names='Habitat',
            values='Count',
            color_discrete_sequence=px.colors.qualitative.Set3,
            title="Habitat Share Across Observations"
        ),
        width="stretch"
    )

    # =========================================================
    # 🧠 QUICK GEO INSIGHTS (PRO TOUCH)
    # =========================================================
    st.markdown("### 🧠 Geographic Insights")

    if not df_map.empty:
        st.success(f"""
        • Most Active Park: {df_map['Park'].mode()[0]}  
        • Dominant Habitat: {df_map['Habitat'].mode()[0]}  
        • Total Geo Points: {len(df_map)}  
        """)


# ----------------------------
# 🧾 SQL (PROFESSIONAL VERSION)
# ----------------------------
elif st.session_state.tab == "SQL":

    st.subheader("🧾 Interactive SQL Data Explorer")

    # =========================================================
    # 🔌 DATABASE CONNECTION
    # =========================================================
    conn = sqlite3.connect(":memory:")
    df_filtered.to_sql("data", conn, index=False, if_exists='replace')

    # =========================================================
    # 💡 SAMPLE QUERIES (PRO FEATURE)
    # =========================================================
    st.markdown("### 💡 Sample Queries")

    sample_queries = {
        "Habitat Distribution":
            "SELECT Habitat, COUNT(*) as Count FROM data GROUP BY Habitat",

        "Top 10 Species":
            "SELECT Common_Name, COUNT(*) as Count FROM data GROUP BY Common_Name ORDER BY Count DESC LIMIT 10",

        "Yearly Observations":
            "SELECT Year, COUNT(*) as Count FROM data GROUP BY Year ORDER BY Year",

        "Observer Activity":
            "SELECT Observer, COUNT(*) as Count FROM data GROUP BY Observer ORDER BY Count DESC LIMIT 10"
    }

    selected_query = st.selectbox("Choose a sample query", list(sample_queries.keys()))

    # =========================================================
    # 📝 QUERY INPUT
    # =========================================================
    query = st.text_area(
        "Write SQL Query",
        value=sample_queries[selected_query],
        height=120
    )

    # =========================================================
    # ▶ RUN QUERY
    # =========================================================
    if st.button("🚀 Run Query"):

        try:
            result = pd.read_sql(query, conn)

            # =========================================================
            # 📊 RESULT KPIs
            # =========================================================
            col1, col2 = st.columns(2)

            col1.metric("Rows Returned", len(result))
            col2.metric("Columns", len(result.columns))

            # =========================================================
            # 📋 TABLE OUTPUT
            # =========================================================
            st.markdown("### 📋 Query Result")
            st.dataframe(result, use_container_width=True)

            # =========================================================
            # 📊 AUTO VISUALIZATION (SMART)
            # =========================================================
            st.markdown("### 📊 Auto Visualization")

            if len(result.columns) >= 2:

                x_col = result.columns[0]
                y_col = result.columns[1]

                # Bar Chart
                st.plotly_chart(
                    px.bar(
                        result,
                        x=x_col,
                        y=y_col,
                        color=y_col,
                        title="Bar Chart Representation"
                    ),
                    width="stretch"
                )

                # Pie Chart (if categorical)
                if result[y_col].dtype != "object":
                    st.plotly_chart(
                        px.pie(
                            result,
                            names=x_col,
                            values=y_col,
                            title="Distribution Breakdown"
                        ),
                        width="stretch"
                    )

            else:
                st.info("Not enough columns for visualization")

            # =========================================================
            # ⬇ DOWNLOAD RESULT
            # =========================================================
            st.download_button(
                "⬇ Download Result",
                result.to_csv(index=False),
                file_name="query_result.csv"
            )

        except Exception as e:
            st.error(f"❌ SQL Error: {e}")

            
# ----------------------------
# INSIGHTS
# ----------------------------
st.subheader("🧠 Smart Insights")

if not df_filtered.empty:
    st.success(f"""
    • Peak Season: {df_filtered['Season'].mode()[0]}  
    • Top Park: {df_filtered['Park'].mode()[0]}  
    • Top Species: {df_filtered['Common_Name'].mode()[0]}  
    """)

# ----------------------------
# DOWNLOAD
# ----------------------------
st.download_button("⬇ Download Data", df_filtered.to_csv(index=False))
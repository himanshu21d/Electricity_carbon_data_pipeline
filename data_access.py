import dlt
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Load the data from DuckDB for a specific zone
def load_electricity(zone):
    pipeline = dlt.pipeline(
        pipeline_name="rest_api_electricity",
        destination="duckdb",
        dataset_name="electricity_data"
    )

    # Used the sql_client to query data from DuckDB
    with pipeline.sql_client() as client:
        carbon_table_name = f"carbon_intensity_history_{zone.lower()}"
        power_table_name = f"power_breakdown_history_{zone.lower()}"
        
        # Query the data from the respective tables
        with client.execute_query(f"SELECT * FROM {carbon_table_name}") as table:
            df_carbon = table.df()  # Convert to Pandas DataFrame
        
        with client.execute_query(f"SELECT * FROM {power_table_name}") as table:
            df_power = table.df()  # Convert to Pandas DataFrame

    return df_carbon, df_power

def get_country_name(zone):
    zone_to_country = {
        "de": "Germany",
        "fr": "France",
        "dk_dk1": "Denmark"
    }
    return zone_to_country.get(zone, zone)

# Streamlit Application
st.title("Electricity Carbon Intensity and Power Breakdown Dashboard")

# List of available zones based on your database tables
zones = ["de", "fr", "dk_dk1"]  # Germany (DE), France (FR), Denmark (DK-DK1)

# Add a selectbox to filter by region/zone
selected_zone = st.selectbox("Select Zone", zones, format_func=get_country_name)

# Load data for the selected zone
df_carbon, df_power = load_electricity(selected_zone)

# Merge the dataframes on datetime to create df_combined
df_combined = pd.merge(
    df_carbon[['datetime', 'carbon_intensity']], 
    df_power[['datetime', 'power_production_total']], 
    on='datetime', 
    how='inner'
)

# Display raw data for the selected zone
st.subheader(f"Raw Data for {get_country_name(selected_zone)}")
st.write(df_carbon.head())  
st.write(df_power.head())  

# **Line Chart**: Carbon Intensity Over Time
st.subheader(f"Carbon Intensity Over Time for {get_country_name(selected_zone)}")
carbon_fig_line = px.line(df_carbon, x="datetime", y="carbon_intensity", 
                          title=f"Carbon Intensity Over Time ({get_country_name(selected_zone)})")
st.plotly_chart(carbon_fig_line)

# Ensure datetime is in a readable format
df_combined['datetime'] = pd.to_datetime(df_combined['datetime']).dt.strftime('%Y-%m-%d %H:%M')

# Create Power Breakdown bar chart
power_fig = go.Figure(go.Bar(
    x=df_combined['datetime'],
    y=df_combined['power_production_total'],
    name='Power Breakdown',
    marker_color='#FFA500'  
))

power_fig.update_layout(
    title=f"Power Breakdown ({get_country_name(selected_zone)})",
    xaxis_title="Datetime",
    yaxis_title="Power Breakdown (MW)",
    xaxis=dict(
        tickangle=-45,
        type='category'
    ),
    height=600,  # Adjust the height as needed
    margin=dict(l=50, r=50, t=100, b=100)
)

# Show the Power Breakdown bar chart in Streamlit
st.plotly_chart(power_fig)

# **Bar Chart for Carbon Intensity**
st.subheader(f"Carbon Intensity for {get_country_name(selected_zone)}")

# Create Carbon Intensity bar chart
carbon_fig = go.Figure(go.Bar(
    x=df_combined['datetime'],
    y=df_combined['carbon_intensity'],
    name='Carbon Intensity',
    marker_color='#1E90FF'  # Blue color
))

carbon_fig.update_layout(
    title=f"Carbon Intensity ({get_country_name(selected_zone)})",
    xaxis_title="Datetime",
    yaxis_title="Carbon Intensity (gCO2eq/kWh)",
    xaxis=dict(
        tickangle=-45,
        type='category'
    ),
    height=600,  # Adjust the height as needed
    margin=dict(l=50, r=50, t=100, b=100)
)

# Show the Carbon Intensity bar chart in Streamlit
st.plotly_chart(carbon_fig)

# Pie Chart: Latest Power Breakdown by Source
st.subheader(f"Latest Power Breakdown by Source for {get_country_name(selected_zone)}")

power_sources = ['power_production_breakdown__coal', 'power_production_breakdown__solar',
                 'power_production_breakdown__wind', 'power_production_breakdown__hydro',
                 'power_production_breakdown__gas', 'power_production_breakdown__oil']

# available power sources
available_power_sources = [col for col in power_sources if col in df_power.columns]

# Handling missing data by using .fillna(0)
latest_power_data = df_power[df_power['datetime'] == df_power['datetime'].max()][available_power_sources].fillna(0).melt()

custom_colors = ['#16325B', '#227B94', '#78B7D0', '#FFDC7F', '#B99470', '#A02334']

# Create the pie chart
pie_fig = px.pie(latest_power_data, values='value', names='variable', 
                 title=f'Power Breakdown by Source ({get_country_name(selected_zone)})',
                 color_discrete_sequence=custom_colors)  # Apply your custom color palette

# Display the pie chart
st.plotly_chart(pie_fig)

# **Map**: Carbon Intensity for all three countries
st.subheader("Carbon Intensity Map for Germany, France, and Denmark")

# data for all zones
all_data = {}
for zone in zones:
    df_carbon, _ = load_electricity(zone)
    all_data[zone] = df_carbon['carbon_intensity'].mean()

# DataFrame for the map
map_data = pd.DataFrame({
    'country': [get_country_name(zone) for zone in zones],
    'iso_alpha': ['DEU', 'FRA', 'DNK'],
    'carbon_intensity': [all_data[zone] for zone in zones]
})

# the choropleth map
fig = px.choropleth(map_data, 
                    locations="iso_alpha", 
                    color="carbon_intensity",
                    hover_name="country", 
                    scope="europe",
                    color_continuous_scale=px.colors.sequential.Reds)

# layout for a dark theme
fig.update_layout(
    geo=dict(
        showland=True,
        landcolor="rgb(40, 40, 40)",
        showocean=True,
        oceancolor="rgb(60, 60, 60)",
        showcoastlines=True,
        coastlinecolor="rgb(80, 80, 80)",
        showcountries=True,
        countrycolor="rgb(120, 120, 120)",
        projection_type="equirectangular"
    ),
    paper_bgcolor="rgb(30, 30, 30)",
    plot_bgcolor="rgb(30, 30, 30)",
    geo_scope="europe", 
)

# Show the map
st.plotly_chart(fig)

# renewable and non-renewable columns
renewable_sources = ['power_production_breakdown__solar', 'power_production_breakdown__wind',
                     'power_production_breakdown__hydro', 'power_production_breakdown__biomass',
                     'power_production_breakdown__geothermal']

non_renewable_sources = ['power_production_breakdown__coal', 'power_production_breakdown__oil',
                         'power_production_breakdown__gas', 'power_production_breakdown__nuclear']

# Filtering out columns that are not present in df_power
available_renewable_sources = [col for col in renewable_sources if col in df_power.columns]
available_non_renewable_sources = [col for col in non_renewable_sources if col in df_power.columns]

# missing values with fillna(0)
df_power[available_renewable_sources] = df_power[available_renewable_sources].fillna(0)
df_power[available_non_renewable_sources] = df_power[available_non_renewable_sources].fillna(0)

# Group renewable and non-renewable energy totals
df_power['renewable_total'] = df_power[available_renewable_sources].sum(axis=1)
df_power['non_renewable_total'] = df_power[available_non_renewable_sources].sum(axis=1)

df_power['datetime'] = pd.to_datetime(df_power['datetime']).dt.strftime('%Y-%m-%d %H:%M')

# Stacked Bar Chart: Renewable vs Non-Renewable over time
st.subheader(f"Renewable vs Non-Renewable Energy for {get_country_name(selected_zone)}")

fig = go.Figure()

# Add bars for Renewable Energy
fig.add_trace(go.Bar(
    x=df_power['datetime'],
    y=df_power['renewable_total'],
    name='Renewable Energy',
    marker_color='#131842'))

# Add bars for Non-Renewable Energy
fig.add_trace(go.Bar(
    x=df_power['datetime'],
    y=df_power['non_renewable_total'],
    name='Non-Renewable Energy',
    marker_color='#E68369'  # Red for Non-Renewable
))

fig.update_layout(
    title=f"Renewable vs Non-Renewable Energy ({get_country_name(selected_zone)})",
    xaxis_title="Datetime",
    yaxis_title="Energy Production (MW)",
    barmode='stack',  
    xaxis=dict(
        tickangle=-45,
        type='category'
    ),
    height=600,
    margin=dict(l=50, r=50, t=100, b=100)
)

st.plotly_chart(fig)

# Pie Chart: Latest Renewable vs Non-Renewable Energy Distribution
st.subheader(f"Latest Renewable vs Non-Renewable Distribution for {get_country_name(selected_zone)}")

latest_data = df_power[df_power['datetime'] == df_power['datetime'].max()]

pie_data = pd.DataFrame({
    'type': ['Renewable', 'Non-Renewable'],
    'value': [latest_data['renewable_total'].values[0], latest_data['non_renewable_total'].values[0]]
})

pie_fig = px.pie(pie_data, values='value', names='type', 
                 title=f'Renewable vs Non-Renewable Energy Distribution ({get_country_name(selected_zone)})',
                 color_discrete_sequence=['#557C56', '#FF9874'])  
st.plotly_chart(pie_fig)
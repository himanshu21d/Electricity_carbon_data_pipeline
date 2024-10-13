# ⚡️ Electricity Carbon Intensity and Power Breakdown Dashboard

### Overview
This project provides an **interactive dashboard** to visualize **carbon intensity** and the **breakdown of power by energy source** across different regions. The data is pulled from the **Electricity Maps API**, processed using **DLT (Data Loading Tool)**, and stored in **DuckDB** for visualization in a Streamlit-powered dashboard.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Pipeline Setup](#pipeline-setup)
- [Dashboard Visualizations](#dashboard-visualizations)
- [Customization](#customization)
- [Contributing](#contributing)
- [License](#license)

## Features
1. **Real-Time Data**: Fetches and displays real-time data on carbon intensity and power breakdown by source.
2. **Region Selection**: Users can select between **Germany**, **France**, and **Denmark** to visualize the energy metrics.
3. **Multiple Visualizations**:
   - **Line Chart** for carbon intensity trends.
   - **Pie Chart** for power breakdown by source.
   - **Stacked Bar Chart** comparing **renewable** and **non-renewable** energy sources.
   - **Choropleth Map** visualizing carbon intensity across Europe.
4. **ETL Pipeline**: Built using **DLT**, the pipeline extracts data from the Electricity Maps API and loads it into **DuckDB**.

## Tech Stack
- **Python**
- **Streamlit** for building the dashboard.
- **Plotly** for creating interactive visualizations.
- **DuckDB** for data storage.
- **DLT (Data Loading Tool)** for building the ETL pipeline.
- **Electricity Maps API** for data.

## Installation
### Prerequisites
- Python 3.7 or higher
- Virtual environment setup (optional but recommended)

### Steps to Install
1. **Clone the repository**:
    ```bash
    git clone <your-repository-url>
    cd <your-repository-folder>
    ```

2. **Set up a virtual environment** (recommended):
    ```bash
    python3 -m venv env
    source env/bin/activate  # For Windows, use `env\Scripts\activate`
    ```

3. **Install required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up your API key**:
    - Add your Electricity Maps API token in the `dlt.secrets` file to access the API.

5. **Run the ETL pipeline** to load data into DuckDB:
    ```bash
    python pipeline.py
    ```

6. **Run the dashboard**:
    ```bash
    streamlit run dashboard.py
    ```

## Usage

Once the setup is complete, navigate to the Streamlit dashboard (`http://localhost:8501` by default) in your browser.

- **Select Region**: Use the dropdown menu to select **Germany**, **France**, or **Denmark**.
- **Explore Visualizations**: Visualizations update dynamically based on the selected region, allowing you to explore:
   - **Carbon Intensity Trends**
   - **Power Breakdown by Energy Source**
   - **Renewable vs Non-Renewable Comparison**
   - **Carbon Intensity Map of Europe**

## Pipeline Setup

The ETL pipeline, implemented using **DLT (Data Loading Tool)**, fetches data from the Electricity Maps API and stores it in **DuckDB** for efficient querying.

### Pipeline Code

```python
from typing import Any
import dlt
import pandas as pd
import duckdb
from rest_api import RESTAPIConfig, rest_api_resources

ZONES = ["DE", "FR", "DK-DK1"]  # Germany, France, Denmark

@dlt.source
def electricity_source(api_token=dlt.secrets.value):
    resources = []
    for zone in ZONES:
        resources.append({
            "name": f"carbon-intensity-history-{zone}",
            "endpoint": {"path": "carbon-intensity/history", "params": {"zone": zone}},
        })
        resources.append({
            "name": f"power-breakdown-history-{zone}",
            "endpoint": {"path": "power-breakdown/history", "params": {"zone": zone}},
        })

    config: RESTAPIConfig = {
        "client": {"base_url": "https://api.electricitymap.org/v3/", "auth": {"token": api_token}},
        "resource_defaults": {"primary_key": ["zone", "datetime"], "write_disposition": "replace"},
        "resources": resources,
    }

    yield from rest_api_resources(config)

def load_electricity() -> pd.DataFrame:
    pipeline = dlt.pipeline(
        pipeline_name="rest_api_electricity",
        destination="duckdb", 
        dataset_name="electricity_data",
    )
    load_info = pipeline.run(electricity_source())
    print(load_info)
    return pipeline
```

The pipeline dynamically generates requests for carbon intensity and power breakdown data based on the zones defined and stores it in **DuckDB**.

### Running the Pipeline:
```bash
python pipeline.py
```

## Dashboard Visualizations

Once data is loaded into DuckDB, the dashboard fetches it and creates interactive visualizations using **Streamlit** and **Plotly**.

### Example Visualizations:
1. **Line Chart**: Displays carbon intensity over time.
2. **Pie Chart**: Shows the breakdown of power sources (e.g., solar, wind, coal).
3. **Stacked Bar Chart**: Compares renewable vs non-renewable energy sources.
4. **Choropleth Map**: Displays carbon intensity across Europe.

### Example Code for Dashboard:

```python
def load_electricity(zone):
    pipeline = dlt.pipeline(pipeline_name="rest_api_electricity", destination="duckdb", dataset_name="electricity_data")
    with pipeline.sql_client() as client:
        carbon_table_name = f"carbon_intensity_history_{zone.lower()}"
        power_table_name = f"power_breakdown_history_{zone.lower()}"
        df_carbon = client.execute_query(f"SELECT * FROM {carbon_table_name}").to_df()
        df_power = client.execute_query(f"SELECT * FROM {power_table_name}").to_df()
    return df_carbon, df_power

# Example: Generate a pie chart using Plotly Express
custom_colors = ['#16325B', '#227B94', '#78B7D0', '#FFDC7F', '#B99470', '#A02334']
pie_fig = px.pie(latest_power_data, values='value', names='variable', 
                 title=f'Power Breakdown by Source ({get_country_name(selected_zone)})',
                 color_discrete_sequence=custom_colors)
st.plotly_chart(pie_fig)
```

## Customization

1. **Color Palette**: You can customize the color palette for visualizations like the pie chart by modifying the `custom_colors` list.
2. **Zones**: You can add or remove zones in the `ZONES` list in the `pipeline.py` file.
3. **Deployment**: The dashboard can be deployed on any cloud platform that supports Python (e.g., **Heroku**, **AWS**, **Google Cloud**).

## Known Issues

- **Missing Data**: Some zones may not have complete data for all power sources. This has been handled by checking for missing columns and using `.fillna(0)` to avoid errors.
- **Performance**: Loading large datasets into the dashboard may take time depending on the volume of data pulled from the API.

## Contributing

Contributions are welcome! To contribute:
1. Fork this repository.
2. Create a new branch (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a pull request.


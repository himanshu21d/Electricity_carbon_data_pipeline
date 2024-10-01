from typing import Any
import dlt
import pandas as pd
import duckdb
from rest_api import RESTAPIConfig, rest_api_resources

ZONES = ["DE", "FR", "DK-DK1"]  # Germany, France, New York, Denmark

@dlt.source
def electricity_source(api_token=dlt.secrets.value):
    resources = []
    
    for zone in ZONES:
        resources.append({
            "name": f"carbon-intensity-history-{zone}",
            "endpoint": {
                "path": "carbon-intensity/history",
                "params": {
                    "zone": zone,
                },
            },
        })
        resources.append({
            "name": f"power-breakdown-history-{zone}",
            "endpoint": {
                "path": "power-breakdown/history",
                "params": {
                    "zone": zone
                },
            },
        })
    
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.electricitymap.org/v3/",
            "auth": {
                "token":  api_token,
            },
        },
        "resource_defaults": {
            "primary_key": ["zone","datetime"],
            "write_disposition": "replace",
        },
        "resources": resources,  # Use the dynamically created list of resources
    }

    yield from rest_api_resources(config)


def load_electricity() -> pd.DataFrame:
    pipeline = dlt.pipeline(
        pipeline_name="rest_api_electricity",
        destination="duckdb",  # Database destination
        dataset_name="electricity_data",
    )

    load_info = pipeline.run(electricity_source())
    print(load_info)  # Display load info
    return pipeline


if __name__ == "__main__":
    load_electricity()

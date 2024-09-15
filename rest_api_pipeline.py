from typing import Any

import dlt
from rest_api import (
    RESTAPIConfig,
    check_connection,
    rest_api_source,
    rest_api_resources,
)


@dlt.source
def electricity_source(api_token=dlt.secrets.value):
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
        "resources": [
            {
                "name": "carbon-intensity-history",
                "endpoint": {
                    "path": "carbon-intensity/history",
                    "params": {
                        "zone": "DE",
                    },
                },
            },
            {
                "name": "power-breakdown-history",
                "endpoint": {
                    "path": "power-breakdown/history",
                    "params": {
                        "zone": "DE"
                    },
                },
            },
        ],
    }

    yield from rest_api_resources(config)

def load_electricity() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="rest_api_electricity",
        destination="duckdb",
        dataset_name="electricity_data",
    )

    load_info = pipeline.run(electricity_source())
    print(load_info)

if __name__ == "__main__":
    load_electricity()


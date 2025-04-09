import os
from typing import Any
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Get Domo credentials from environment variables
DOMO_HOST = os.getenv("DOMO_HOST")
DOMO_DEVELOPER_TOKEN = os.getenv("DOMO_DEVELOPER_TOKEN")

# Initialize FastMCP server
mcp = FastMCP("Domo")

# Constants
DOMO_API_BASE = f"https://{DOMO_HOST}/api"

async def make_domo_request(url: str, method: str, data: dict = None) -> dict[str, Any] | None:
    """Make a request to the Domo API with proper error handling."""

    headers = {
        "X-DOMO-Developer-Token": DOMO_DEVELOPER_TOKEN,
        "Accept": "application/json"
    }

    full_url = f"{DOMO_API_BASE}{url}"

    if method.upper() == "GET":
        response = requests.get(full_url, headers=headers)
    elif method.upper() == "POST":
        response = requests.post(full_url, headers=headers, json=data)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    response.raise_for_status()
    return response.json()

@mcp.tool()
async def get_dataset_metadata(dataset_id: str) -> str:
    """Get metadata for a Domo dataset.
    Args:
        dataset_id: Domo dataset ID
    """
    try:
        url = f"/data/v3/datasources/{dataset_id}?part=core"
        data = await make_domo_request(url, "GET")

        if not data:
            return "Unable to fetch dataset metadata."

        return data
    except Exception as e:
        return f"Error fetching dataset metadata: {str(e)}"

@mcp.tool()
async def get_dataset_schema(dataset_id: str) -> str:
    """Get the schema of a Domo dataset.
    Args:
        dataset_id: Domo dataset ID
    """
    try:
        url = f"/data/v2/datasources/{dataset_id}/schemas/latest"
        data = await make_domo_request(url, "GET")

        if not data:
            return "Unable to fetch dataset schema."

        return data
    except Exception as e:
        return f"Error fetching dataset schema: {str(e)}"

@mcp.tool()
async def query_dataset(dataset_id: str, sql: str) -> str:
    """Query a Domo dataset using SQL.
    Args:
        dataset_id: Domo dataset ID
        sql: SQL query to execute
    """
    try:
        url = f"/query/v1/execute/{dataset_id}"
        data = await make_domo_request(url, "POST", data={"sql": sql})

        if not data:
            return "Unable to execute query on the dataset."

        return data
    except Exception as e:
        return f"Error executing query on dataset: {str(e)}"

@mcp.tool()
async def search_datasets(query: str) -> str:
    """Search for datasets in a Domo instance by name.
    Args:
        query: Search query string
        count: Number of results to return
        offset: Offset for pagination
    """
    try:
        url = "/data/ui/v3/datasources/search"
        payload = {
            "entities": ["DATASET"],
            "filters": [{
                "field": "name_sort",
                "filterType": "wildcard",
                "query": f"*{query}*",
            }],
            "combineResults": True,
            "query": "*",
            "count": 1,
            "offset": 0,
            "sort": {
                "isRelevance": False,
                "fieldSorts": [{"field": "create_date", "sortOrder": "DESC"}]
            }
        }
        data = await make_domo_request(url, "POST", data=payload)

        if not data:
            return "Unable to search datasets."
        
        # Extract dataset IDs and names from the response
        datasets = [{"id": ds["id"], "name": ds["name"]} for ds in data.get("dataSources", [])]
        return datasets
    except Exception as e:
        return f"Error searching datasets: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
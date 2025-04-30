import logging
import os
from typing import Any
import requests
from dotenv import load_dotenv
from mcp.server import Server

# Load environment variables
load_dotenv()

# Get Domo credentials from environment variables
DOMO_HOST = os.getenv("DOMO_HOST")
DOMO_DEVELOPER_TOKEN = os.getenv("DOMO_DEVELOPER_TOKEN")
# Constants
DOMO_API_BASE = f"https://{DOMO_HOST}/api"

app = Server("domo-mcp-server")

class DomoClient:
    def __init__(self, logger: logging.Logger):
        """Initialize the DomoClient with environment variables and constants."""
        self.DOMO_HOST = os.getenv("DOMO_HOST")
        self.DOMO_DEVELOPER_TOKEN = os.getenv("DOMO_DEVELOPER_TOKEN")
        self.DOMO_API_BASE = f"https://{self.DOMO_HOST}/api"
        self.logger = logger

    async def make_request(self, url: str, method: str, data: dict = None) -> dict[str, Any] | None:
        """Make a request to the Domo API with proper error handling."""
        headers = {
            "X-DOMO-Developer-Token": self.DOMO_DEVELOPER_TOKEN,
            "Accept": "application/json"
        }

        full_url = f"{self.DOMO_API_BASE}{url}"

        try:
            if method.upper() == "GET":
                response = requests.get(full_url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(full_url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP request failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None

    async def get_dataset_metadata(self, dataset_id: str) -> str:
        """Get metadata for a Domo dataset."""
        try:
            url = f"/data/v3/datasources/{dataset_id}?part=core"
            data = await self.make_request(url, "GET")

            if not data:
                self.logger.warning("No data returned for dataset metadata.")
                return "Unable to fetch dataset metadata."

            return data
        except Exception as e:
            self.logger.error(f"Error fetching dataset metadata: {str(e)}")
            return f"Error fetching dataset metadata: {str(e)}"

    async def get_dataset_schema(self, dataset_id: str) -> str:
        """Get the schema of a Domo dataset."""
        try:
            url = f"/data/v2/datasources/{dataset_id}/schemas/latest"
            data = await self.make_request(url, "GET")

            if not data:
                self.logger.warning("No data returned for dataset schema.")
                return "Unable to fetch dataset schema."

            return data
        except Exception as e:
            self.logger.error(f"Error fetching dataset schema: {str(e)}")
            return f"Error fetching dataset schema: {str(e)}"

    async def query_dataset(self, dataset_id: str, sql: str) -> str:
        """Query a Domo dataset using SQL."""
        try:
            url = f"/query/v1/execute/{dataset_id}"
            data = await self.make_request(url, "POST", data={"sql": sql})

            if not data:
                self.logger.warning("No data returned for dataset query.")
                return "Unable to execute query on the dataset."

            return data
        except Exception as e:
            self.logger.error(f"Error executing query on dataset: {str(e)}")
            return f"Error executing query on dataset: {str(e)}"

    async def search_datasets(self, query: str) -> str:
        """Search for datasets in a Domo instance by name."""
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
            data = await self.make_request(url, "POST", data=payload)

            if not data:
                self.logger.warning("No data returned for dataset search.")
                return "Unable to search datasets."

            datasets = [{"id": ds["id"], "name": ds["name"]} for ds in data.get("dataSources", [])]
            return datasets
        except Exception as e:
            self.logger.error(f"Error searching datasets: {str(e)}")
            return f"Error searching datasets: {str(e)}"
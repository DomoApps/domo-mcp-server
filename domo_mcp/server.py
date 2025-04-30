import json
import logging
import sys
from typing import Optional
from .domo import DomoClient
import mcp
from mcp.server import NotificationOptions, Server
import mcp.types as types
from pydantic import BaseModel, Field


def setup_logger():
    class Logger:
        def info(self, message):
            print(f"[INFO] {message}", file=sys.stderr)

        def warning(self, message):
            print(f"[WARNING] {message}", file=sys.stderr)

        def error(self, message):
            print(f"[ERROR] {message}", file=sys.stderr)

    return Logger()

logger = setup_logger()
domo_client = DomoClient(logger)
server = Server("domo-mcp")

# options =
class ToolModel(BaseModel):
    @classmethod
    def as_tool(cls):
        return types.Tool(
            name="Domo" + cls.__name__,
            description=cls.__doc__,
            inputSchema=cls.model_json_schema()
        )

class GetDatasetSchema(ToolModel):
    """Get a Domo dataset schema."""
    dataset_id: str = Field(description="The ID of the dataset to get the schema for.")


@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    return []

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    return []

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    logger.info("Listing available tools")
    # await server.request_context.session.send_notification("are you recieving this notification?")
    tools = [
        GetDatasetSchema.as_tool(),
    ]
    logger.info(f"Available tools: {[tool.name for tool in tools]}")
    return tools

@server.call_tool()
async def handle_call_tool(
        name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    assert name[:4] == "Domo", f"Unknown tool: {name}"
    try:
        match name[4:]:
            case "GetDatasetSchema":
                logger.info(f"Performing search with arguments: {arguments}")
                search_results = await domo_client.get_dataset_schema(
                    dataset_id=arguments["dataset_id"]
                )
                logger.info("Schema fetched successfully.")
                return [types.TextContent(
                    type="text",
                    text=json.dumps(search_results, indent=2)
                )]
            case _:
                error_msg = f"Unknown tool: {name}"
                logger.error(error_msg)
                return [types.TextContent(
                    type="text",
                    text=error_msg
                )]
    except Exception as e:
        error_msg = f"Unexpected error occurred: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]

async def main():
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error occurred: {str(e)}")
        raise
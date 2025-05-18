import asyncio
import os
import logging

from mcp.server.fastmcp import FastMCP
# Context might be needed if tools require access to server context, but not for now.
# from mcp.server.fastmcp import Context 

# Import tool handlers and their definitions (for names and descriptions)
from tools.ohlcv_tools import TOOL_HANDLERS, ALL_TOOL_DEFS

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# This FastMCP instance will be discovered by 'mcp dev main.py'
# Standard names are 'mcp', 'server', or 'app'.
mcp = FastMCP(
    "PolygonMCPServer",
    dependencies=["httpx"]  # httpx is used by our tools
)
logger.info(f"MCP Server '{mcp.name}' initialized.") # Assuming .name attribute from docs

# Register all tools
# The @mcp.tool() decorator registers the function with the mcp instance.
# We are applying it programmatically to the imported handler functions.
registered_tool_count = 0
for tool_def_info in ALL_TOOL_DEFS:
    tool_name = tool_def_info.get("tool_name")
    handler_func = TOOL_HANDLERS.get(tool_name)

    if not tool_name:
        logger.warning("Found a tool definition without a 'tool_name'. Skipping.")
        continue
    if not handler_func:
        logger.warning(f"No handler function found for tool '{tool_name}'. Skipping.")
        continue

    try:
        # Get the description from the tool definition dictionary.
        # The schema (parameters, return type) will be inferred from the
        # handler_func's type hints and docstring by FastMCP.
        description = tool_def_info.get("description", handler_func.__doc__ or "")

        # Apply the decorator to the handler function.
        # This registers the tool with the mcp instance.
        # The decorated function itself isn't typically stored in a new variable here,
        # as the act of decoration modifies the mcp instance.
        mcp.tool(
            name=tool_name,      # Explicitly set the tool name
            description=description  # Provide the description
        )(handler_func)          # This applies the configured decorator to the handler

        logger.info(f"Tool '{tool_name}' registered successfully.")
        registered_tool_count +=1
    except Exception as e:
        logger.error(f"Failed to register tool '{tool_name}': {e}", exc_info=True)

if registered_tool_count == 0:
    logger.warning("No tools were successfully registered.")
else:
    logger.info(f"Successfully registered {registered_tool_count} tool(s).")

# Check for POLYGON_API_KEY. This is relevant for the tools' operation.
if not os.environ.get("POLYGON_API_KEY"):
    logger.critical("POLYGON_API_KEY environment variable is not set.")
    logger.critical("The Polygon API tools will likely fail during execution.")
else:
    logger.info("POLYGON_API_KEY environment variable found.")

# This block allows running the server directly using 'python main.py'
if __name__ == "__main__":
    logger.info("Starting Polygon MCP Server application via direct execution (`python main.py`)...")
    # The `mcp dev main.py` command will likely discover and run `mcp`
    # without executing this __main__ block's mcp.run().
    try:
        mcp.run() # This is a blocking call that starts the server.
    except KeyboardInterrupt:
        logger.info("Server stopped by user (KeyboardInterrupt).")
    except Exception as e:
        logger.error(f"Server exited with an error: {e}", exc_info=True)
    finally:
        logger.info("Server has shut down.")

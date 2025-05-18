import asyncio
import os
import logging

# Import from the MCP SDK
from mcp import MCPServer, ToolDefinition, ToolParameter # Assuming these are common MCP SDK classes

# Import our tool definitions and handlers
from tools.ohlcv_tools import ALL_TOOL_DEFS, TOOL_HANDLERS # Corrected import path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Main Application Logic ---
async def main_server_logic():
    # Ensure POLYGON_API_KEY is available, as tools depend on it.
    api_key = os.environ.get("POLYGON_API_KEY")
    if not api_key:
        logger.critical("POLYGON_API_KEY environment variable is not set.")
        logger.critical("The Polygon API tools will fail. Please set this variable before running.")
        # Consider whether to exit or proceed with non-functional tools
        # For now, proceeding but tools will likely error out.
    else:
        logger.info("POLYGON_API_KEY found. Tools should be able to connect to Polygon API.")

    # Initialize the MCP server
    # Assuming MCPServer takes host and port.
    # The MCP SDK might handle server identity (name, version, etc.) differently,
    # possibly via configuration files or other parameters.
    # For now, a simple initialization.
    server = MCPServer(
        host="0.0.0.0",
        port=7777,
        server_name="PolygonMCPServer",
        server_version="0.1.0",
        description="An MCP server providing tools to interact with the Polygon.io API."
    )
    logger.info(f"MCP Server '{server.server_name}' v{server.server_version} initialized to run on {server.host}:{server.port}")

    # Register all tools defined in ohlcv_tools.py
    registered_tool_count = 0
    for tool_def_dict in ALL_TOOL_DEFS:
        tool_name = tool_def_dict.get("tool_name")
        if not tool_name:
            logger.warning("Found a tool definition without a 'tool_name' in ALL_TOOL_DEFS. Skipping.")
            continue

        handler = TOOL_HANDLERS.get(tool_name)
        if not handler:
            logger.warning(f"No handler found for tool '{tool_name}' in TOOL_HANDLERS. Tool will not be operational.")
            continue

        try:
            # Assuming the MCP SDK's ToolDefinition can be created from a dictionary
            # or that MCPServer.add_tool can take the dictionary directly.
            # Let's assume ToolDefinition can parse the schema parts.
            # The actual SDK might have a more structured way to define parameters.
            
            # Create ToolParameter objects if the SDK requires it
            # This is a guess based on typical SDK design.
            input_params = []
            if "properties" in tool_def_dict.get("input_schema", {}):
                for name, schema in tool_def_dict["input_schema"]["properties"].items():
                    input_params.append(ToolParameter(
                        name=name,
                        description=schema.get("description", ""),
                        param_type=schema.get("type"), # SDK might have specific types
                        is_required=name in tool_def_dict["input_schema"].get("required", [])
                    ))
            
            # For simplicity, we might just pass the schema dicts if the SDK supports it.
            # Let's try creating ToolDefinition directly from the dict,
            # assuming it's smart enough or MCPServer.add_tool is.
            # If not, the above ToolParameter creation would be needed.

            tool_definition = ToolDefinition(
                tool_name=tool_name,
                description=tool_def_dict.get("description", ""),
                input_schema=tool_def_dict.get("input_schema", {}), # Or pass input_params if created
                output_schema=tool_def_dict.get("output_schema", {}),
                handler_function=handler
                # Permissions might be handled here if the SDK supports it
            )
            server.add_tool(tool_definition) # Or server.register_tool(tool_definition)
            logger.info(f"Tool '{tool_name}' registered with MCP Server.")
            logger.info(f"  Description: {tool_definition.description}")
            registered_tool_count += 1
        except Exception as e:
            logger.error(f"Failed to register tool '{tool_name}': {e}", exc_info=True)


    if registered_tool_count == 0:
        logger.warning("No tools were successfully registered with the MCP server.")
    else:
        logger.info(f"Successfully registered {registered_tool_count} tool(s).")

    # Start the server
    try:
        logger.info(f"Starting MCP Server on {server.host}:{server.port}...")
        await server.start() # Assuming an async start method
        # The MCP server's start() method should handle the main event loop
        # and keep the server running until stopped.
    except KeyboardInterrupt:
        logger.info("MCP Server stopped by user (KeyboardInterrupt).")
    except Exception as e:
        logger.critical(f"MCP Server failed to start or encountered a critical error: {e}", exc_info=True)
    finally:
        logger.info("MCP Server shutting down...")
        # Perform any cleanup here if necessary (e.g., server.stop() if available)
        # await server.stop() # If an explicit stop is needed
        logger.info("MCP Server has concluded its run.")

if __name__ == "__main__":
    logger.info("Starting Polygon MCP Server application...")

    # Standard Python asyncio setup
    # The WindowsSelectorEventLoopPolicy is generally not needed for Python 3.8+
    # as ProactorEventLoop is default on Windows and usually works well.
    # If issues arise on Windows, it can be reinstated.
    # if os.name == 'nt':
    #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main_server_logic())

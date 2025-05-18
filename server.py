import os
import logging
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP
# Context might be needed if tools require access to server context, but not for now.
# from mcp.server.fastmcp import Context 

# Import tool registration functions
from tools.ohlcv_tools import register_tools as register_ohlcv_tools
from tools.technical_indicator_tools import register_tools as register_technical_indicator_tools

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# This FastMCP instance will be discovered by 'mcp dev main.py'
# Standard names are 'mcp', 'server', or 'app'.
mcp = FastMCP(
    "PolygonMCPServer",
    dependencies=["httpx"]  # httpx is used by our tools
)
logger.info(f"MCP Server '{mcp.name}' initialized.") # Assuming .name attribute from docs

# Register OHLCV tools
try:
    register_ohlcv_tools(mcp)
    logger.info("OHLCV tools registration process initiated via register_ohlcv_tools.")
except Exception as e:
    logger.error(f"Failed to register OHLCV tools via register_ohlcv_tools: {e}", exc_info=True)

# Register technical indicator tools
try:
    register_technical_indicator_tools(mcp)
    logger.info("Technical indicator tools registration process initiated via technical_indicator_tools.register_tools.")
except Exception as e:
    logger.error(f"Failed to register technical indicator tools: {e}", exc_info=True)


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

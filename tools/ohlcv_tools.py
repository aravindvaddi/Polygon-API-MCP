import os
from typing_extensions import List
import httpx  # Using httpx for async requests, similar to 'requests' but good for async frameworks
from typing import Dict, Any, Optional

# It's good practice to get API keys from environment variables
POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"

async def get_previous_day_bar(ticker: str, adjusted: Optional[bool] = True) -> Dict[str, Any]:
    """
    Retrieves the previous trading day's open, high, low, and close (OHLC) data
    for a specified stock ticker from the Polygon API.

    :param ticker: The stock ticker symbol (e.g., "AAPL").
    :param adjusted: Whether or not the results are adjusted for splits.
                     Defaults to True.
    :return: A dictionary containing the OHLC data or an error message.
    """
    if not POLYGON_API_KEY:
        # This is a server-side configuration error, so we might raise an exception
        # or return a specific error structure that the MCP server can interpret.
        return {"error": "Polygon API key is not configured."}

    url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/prev"
    params = {
        "adjusted": str(adjusted).lower(), # Polygon API expects 'true' or 'false' as strings
        "apiKey": POLYGON_API_KEY
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
            data = response.json()

            # According to Polygon docs, results are in a list.
            # Even for a single previous day, it might be a list with one item.
            # {"ticker":"AAPL","queryCount":1,"resultsCount":1,"adjusted":true,"results":[{"T":"AAPL","v":12345,"vw":150.00,"o":150.00,"c":150.00,"h":150.00,"l":150.00,"t":1678886400000,"n":1}],"status":"OK","request_id":"someid"}
            # We should probably return the content of "results" or the first item if present.
            if data.get("status") == "OK" and "results" in data and data["resultsCount"] > 0:
                return data["results"][0] # Return the first bar data
            elif data.get("status") == "OK" and data["resultsCount"] == 0:
                return {"message": f"No previous day bar data found for {ticker}."}
            else:
                # Handle cases like {"status":"ERROR", "error":"Unknown ticker symbol: AAPLX"}
                # or other non-OK statuses
                return {"error": data.get("error") or data.get("message", "Failed to fetch data from Polygon API"), "details": data}

        except httpx.HTTPStatusError as e:
            # Error from Polygon API (e.g., 404 Not Found, 401 Unauthorized if API key is bad)
            return {"error": f"Polygon API error: {e.response.status_code}", "message": str(e.response.text)}
        except httpx.RequestError as e:
            # Network error or other issue with the request
            return {"error": "Failed to connect to Polygon API", "message": str(e)}
        except Exception as e:
            # Catch-all for other unexpected errors
            # Log this error for debugging
            print(f"Unexpected error in get_previous_day_bar: {e}")
            return {"error": "An unexpected error occurred."}

# This is how we might define the tool for an MCP server.
# The exact structure will depend on the Python MCP SDK we use.
# For now, let's assume it's a dictionary structure.
# This would typically be collected by the main server module.

PREVIOUS_DAY_BAR_TOOL_DEF: Dict[str, Any] = {
    "tool_name": "get_previous_day_bar",
    "description": "Retrieves the previous trading day's OHLC data for a stock ticker.",
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": {"type": "string", "description": "The stock ticker symbol (e.g., 'AAPL')."},
            "adjusted": {"type": "boolean", "description": "Whether results are adjusted for splits. Defaults to true.", "default": True}
        },
        "required": ["ticker"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            # Define expected fields based on Polygon's response
            # Example fields:
            "T": {"type": "string", "description": "Ticker symbol."},
            "v": {"type": "number", "description": "Trading volume."},
            "vw": {"type": "number", "description": "Volume weighted average price."},
            "o": {"type": "number", "description": "Open price."},
            "c": {"type": "number", "description": "Close price."},
            "h": {"type": "number", "description": "High price."},
            "l": {"type": "number", "description": "Low price."},
            "t": {"type": "integer", "description": "Unix Msec timestamp."},
            "n": {"type": "integer", "description": "Number of transactions."},
            "error": {"type": "string", "description": "Error message if the call failed."},
            "message": {"type": "string", "description": "Additional message, e.g. if no data found."}
            # We might want to make this more robust, perhaps using a oneOf if there's an error vs success
        }
        # A more advanced schema might use "oneOf" to distinguish between success and error shapes
    },
    # "permissions": [] # Explicitly empty or omitted for no permissions, as discussed
}

# We can add other tool functions and definitions here later.
# For example:
# async def get_custom_bars(...): ...
# CUSTOM_BARS_TOOL_DEF = { ... }

# A list to easily export all tool definitions from this module
ALL_TOOL_DEFS: List[Dict[str, Any]] = [
    PREVIOUS_DAY_BAR_TOOL_DEF
]

# A dictionary to map tool names to their handler functions
TOOL_HANDLERS = {
    "get_previous_day_bar": get_previous_day_bar,
}

if __name__ == '__main__':
    # Example of how to run this function directly for testing
    # You would need to set the POLYGON_API_KEY environment variable
    # e.g., export POLYGON_API_KEY='YOUR_API_KEY'
    import asyncio

    async def main_test():
        if not POLYGON_API_KEY:
            print("POLYGON_API_KEY environment variable not set. Please set it to test.")
            return

        print("Testing get_previous_day_bar for AAPL...")
        result_aapl = await get_previous_day_bar(ticker="AAPL")
        print(f"AAPL Result: {result_aapl}\n")

        print("Testing get_previous_day_bar for a non-existent ticker (e.g., INVALIDTICKER)...")
        result_invalid = await get_previous_day_bar(ticker="INVALIDTICKERXYZ")
        print(f"INVALIDTICKERXYZ Result: {result_invalid}\n")

        print("Testing get_previous_day_bar for MSFT (not adjusted)...")
        result_msft_not_adjusted = await get_previous_day_bar(ticker="MSFT", adjusted=False)
        print(f"MSFT (not adjusted) Result: {result_msft_not_adjusted}\n")

    if os.name == 'nt': # Fix for "RuntimeError: Event loop is closed" on Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main_test())

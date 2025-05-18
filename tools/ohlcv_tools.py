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

async def get_custom_bars(
    ticker: str,
    multiplier: int,
    timespan: str,
    from_date: str,
    to_date: str,
    adjusted: Optional[bool] = True,
    sort: Optional[str] = "asc",
    limit: Optional[int] = 5000
) -> Dict[str, Any]:
    """
    Retrieves custom aggregate bars for a stock ticker over a given date range.

    :param ticker: The stock ticker symbol (e.g., "AAPL").
    :param multiplier: The size of the timespan multiplier.
    :param timespan: The size of the time window (e.g., "minute", "hour", "day").
    :param from_date: The start of the aggregate time window (YYYY-MM-DD).
    :param to_date: The end of the aggregate time window (YYYY-MM-DD).
    :param adjusted: Whether results are adjusted for splits. Defaults to True.
    :param sort: Sort the results by timestamp. "asc" or "desc". Defaults to "asc".
    :param limit: Limits the number of base aggregates queried. Max 50000.
    :return: A dictionary containing the aggregate bar data or an error message.
    """
    if not POLYGON_API_KEY:
        return {"error": "Polygon API key is not configured."}

    url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
    params = {
        "adjusted": str(adjusted).lower(),
        "sort": sort,
        "limit": str(limit),
        "apiKey": POLYGON_API_KEY
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Custom bars response structure:
            # {"ticker":"AAPL","queryCount":2,"resultsCount":2,"adjusted":true,"results":[{"v":123,"vw":150,"o":150,"c":150,"h":150,"l":150,"t":1678886400000,"n":1}, ...],"status":"OK","request_id":"someid"}
            if data.get("status") == "OK": # "results" might be empty if no data for range
                return data # Return the full response including the list of bars
            else:
                return {"error": data.get("error") or data.get("message", "Failed to fetch data from Polygon API"), "details": data}

        except httpx.HTTPStatusError as e:
            return {"error": f"Polygon API error: {e.response.status_code}", "message": str(e.response.text)}
        except httpx.RequestError as e:
            return {"error": "Failed to connect to Polygon API", "message": str(e)}
        except Exception as e:
            print(f"Unexpected error in get_custom_bars: {e}")
            return {"error": "An unexpected error occurred."}

CUSTOM_BARS_TOOL_DEF: Dict[str, Any] = {
    "tool_name": "get_custom_bars",
    "description": "Retrieves custom aggregate bars for a stock ticker over a given date range.",
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": {"type": "string", "description": "The stock ticker symbol (e.g., 'AAPL')."},
            "multiplier": {"type": "integer", "description": "The size of the timespan multiplier."},
            "timespan": {"type": "string", "description": "The size of the time window (e.g., 'minute', 'hour', 'day')."},
            "from_date": {"type": "string", "description": "The start of the aggregate time window (YYYY-MM-DD)."},
            "to_date": {"type": "string", "description": "The end of the aggregate time window (YYYY-MM-DD)."},
            "adjusted": {"type": "boolean", "description": "Whether results are adjusted for splits. Defaults to true.", "default": True},
            "sort": {"type": "string", "description": "Sort order ('asc' or 'desc'). Defaults to 'asc'.", "default": "asc", "enum": ["asc", "desc"]},
            "limit": {"type": "integer", "description": "Limit the number of results. Max 50000. Defaults to 5000.", "default": 5000}
        },
        "required": ["ticker", "multiplier", "timespan", "from_date", "to_date"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "ticker": {"type": "string"},
            "queryCount": {"type": "integer"},
            "resultsCount": {"type": "integer"},
            "adjusted": {"type": "boolean"},
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "v": {"type": "number", "description": "Trading volume."},
                        "vw": {"type": "number", "description": "Volume weighted average price."},
                        "o": {"type": "number", "description": "Open price."},
                        "c": {"type": "number", "description": "Close price."},
                        "h": {"type": "number", "description": "High price."},
                        "l": {"type": "number", "description": "Low price."},
                        "t": {"type": "integer", "description": "Unix Msec timestamp."},
                        "n": {"type": "integer", "description": "Number of transactions."}
                    }
                }
            },
            "status": {"type": "string"},
            "request_id": {"type": "string"},
            "error": {"type": "string", "description": "Error message if the call failed."},
            "message": {"type": "string", "description": "Additional message from API."}
        }
    }
}

async def get_daily_market_summary(
    date: str,
    adjusted: Optional[bool] = True,
    include_otc: Optional[bool] = False
) -> Dict[str, Any]:
    """
    Retrieves the daily open, high, low, and close (OHLC) summary for all tickers
    for a given date from the Polygon API.

    :param date: The date for the market summary (YYYY-MM-DD).
    :param adjusted: Whether results are adjusted for splits. Defaults to True.
    :param include_otc: Whether to include OTC securities. Defaults to False.
    :return: A dictionary containing the market summary data or an error message.
    """
    if not POLYGON_API_KEY:
        return {"error": "Polygon API key is not configured."}

    # Note: The API docs specify /v2/aggs/grouped/locale/us/market/stocks/{date}
    # This implies it's for US stocks.
    url = f"{BASE_URL}/v2/aggs/grouped/locale/us/market/stocks/{date}"
    params = {
        "adjusted": str(adjusted).lower(),
        "includeOTC": str(include_otc).lower(), # API expects 'true' or 'false'
        "apiKey": POLYGON_API_KEY
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            # Example Response:
            # {"queryCount":100,"resultsCount":100,"adjusted":true,"results":[...],"status":"OK","request_id":"..."}
            if data.get("status") == "OK":
                return data # Return the full response
            else:
                return {"error": data.get("error") or data.get("message", "Failed to fetch data from Polygon API"), "details": data}

        except httpx.HTTPStatusError as e:
            return {"error": f"Polygon API error: {e.response.status_code}", "message": str(e.response.text)}
        except httpx.RequestError as e:
            return {"error": "Failed to connect to Polygon API", "message": str(e)}
        except Exception as e:
            print(f"Unexpected error in get_daily_market_summary: {e}")
            return {"error": "An unexpected error occurred."}

DAILY_MARKET_SUMMARY_TOOL_DEF: Dict[str, Any] = {
    "tool_name": "get_daily_market_summary",
    "description": "Retrieves the daily OHLC summary for all US stock tickers for a given date.",
    "input_schema": {
        "type": "object",
        "properties": {
            "date": {"type": "string", "description": "The date for the market summary (YYYY-MM-DD)."},
            "adjusted": {"type": "boolean", "description": "Whether results are adjusted for splits. Defaults to true.", "default": True},
            "include_otc": {"type": "boolean", "description": "Whether to include OTC securities. Defaults to false.", "default": False}
        },
        "required": ["date"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "queryCount": {"type": "integer"},
            "resultsCount": {"type": "integer"},
            "adjusted": {"type": "boolean"},
            "results": {
                "type": "array",
                "items": { # Same structure as individual bar items
                    "type": "object",
                    "properties": {
                        "T": {"type": "string", "description": "Ticker symbol."},
                        "v": {"type": "number", "description": "Trading volume."},
                        "vw": {"type": "number", "description": "Volume weighted average price."},
                        "o": {"type": "number", "description": "Open price."},
                        "c": {"type": "number", "description": "Close price."},
                        "h": {"type": "number", "description": "High price."},
                        "l": {"type": "number", "description": "Low price."},
                        "t": {"type": "integer", "description": "Unix Msec timestamp."},
                        "n": {"type": "integer", "description": "Number of transactions."}
                    }
                }
            },
            "status": {"type": "string"},
            "request_id": {"type": "string"},
            "error": {"type": "string", "description": "Error message if the call failed."},
            "message": {"type": "string", "description": "Additional message from API."}
        }
    }
}

async def get_daily_ticker_summary(
    ticker: str,
    date: str,
    adjusted: Optional[bool] = True
) -> Dict[str, Any]:
    """
    Retrieves the daily open, high, low, close (OHLC) and other summary data
    for a specific stock ticker on a given date from the Polygon API (v1).

    :param ticker: The stock ticker symbol (e.g., "AAPL").
    :param date: The date for the ticker summary (YYYY-MM-DD).
    :param adjusted: Whether results are adjusted for splits. Defaults to True.
    :return: A dictionary containing the ticker summary data or an error message.
    """
    if not POLYGON_API_KEY:
        return {"error": "Polygon API key is not configured."}

    # This uses the v1 daily open/close endpoint
    url = f"{BASE_URL}/v1/open-close/{ticker}/{date}"
    params = {
        "adjusted": str(adjusted).lower(),
        "apiKey": POLYGON_API_KEY
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            data = response.json()
            response.raise_for_status() # Check for 4xx/5xx HTTP errors first

            # V1 API specific error handling (can return 200 OK with error in body)
            if data.get("status") == "OK":
                return data
            elif data.get("status") == "ERROR" or "message" in data : # Check for API-level errors
                 return {"error": data.get("message", "Failed to fetch data from Polygon API"), "details": data}
            else: # Fallback for unexpected response structure
                return {"error": "Failed to fetch data from Polygon API or unexpected response format", "details": data}

        except httpx.HTTPStatusError as e:
            try: # Try to parse JSON error from response body
                error_data = e.response.json()
                return {"error": f"Polygon API error: {e.response.status_code}", "message": error_data.get("message", str(e.response.text)), "details": error_data}
            except: # If response body isn't JSON or other parsing error
                return {"error": f"Polygon API error: {e.response.status_code}", "message": str(e.response.text)}
        except httpx.RequestError as e:
            return {"error": "Failed to connect to Polygon API", "message": str(e)}
        except Exception as e:
            print(f"Unexpected error in get_daily_ticker_summary: {e}")
            return {"error": "An unexpected error occurred."}

DAILY_TICKER_SUMMARY_TOOL_DEF: Dict[str, Any] = {
    "tool_name": "get_daily_ticker_summary",
    "description": "Retrieves the daily OHLC, volume, and after-hours/pre-market data for a specific ticker on a given date (Polygon v1 API).",
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": {"type": "string", "description": "The stock ticker symbol (e.g., 'AAPL')."},
            "date": {"type": "string", "description": "The date for the summary (YYYY-MM-DD)."},
            "adjusted": {"type": "boolean", "description": "Whether results are adjusted for splits. Defaults to true.", "default": True}
        },
        "required": ["ticker", "date"]
    },
    "output_schema": { # Based on Polygon v1 /open-close/{stocksTicker}/{date}
        "type": "object",
        "properties": {
            "status": {"type": "string"},
            "from": {"type": "string", "description": "The date of the data."},
            "symbol": {"type": "string", "description": "The ticker symbol."},
            "open": {"type": "number"},
            "high": {"type": "number"},
            "low": {"type": "number"},
            "close": {"type": "number"},
            "volume": {"type": "number"},
            "afterHours": {"type": "number", "description": "After hours price."},
            "preMarket": {"type": "number", "description": "Pre-market price."},
            "error": {"type": "string", "description": "Error message if the call failed."},
            "message": {"type": "string", "description": "Additional message from API (often for errors)."},
            "details": {"type": "object", "description": "Full error details if available."}
        }
    }
}

# A list to easily export all tool definitions from this module
ALL_TOOL_DEFS: List[Dict[str, Any]] = [
    PREVIOUS_DAY_BAR_TOOL_DEF,
    CUSTOM_BARS_TOOL_DEF,
    DAILY_MARKET_SUMMARY_TOOL_DEF,
    DAILY_TICKER_SUMMARY_TOOL_DEF
]

# A dictionary to map tool names to their handler functions
TOOL_HANDLERS = {
    "get_previous_day_bar": get_previous_day_bar,
    "get_custom_bars": get_custom_bars,
    "get_daily_market_summary": get_daily_market_summary,
    "get_daily_ticker_summary": get_daily_ticker_summary,
}

# For FastMCP integration
from mcp.server.fastmcp import FastMCP # Ensure FastMCP is imported if not already
import logging # For logging within the registration function

logger = logging.getLogger(__name__)

def register_tools(mcp_instance: FastMCP):
    """Registers all OHLCV tools with the provided FastMCP instance."""
    registered_count = 0
    for tool_def_info in ALL_TOOL_DEFS:
        tool_name = tool_def_info.get("tool_name")
        handler_func = TOOL_HANDLERS.get(tool_name)

        if not tool_name:
            logger.warning("Found an OHLCV tool definition without a 'tool_name' in ohlcv_tools. Skipping.")
            continue
        if not handler_func:
            logger.warning(f"No handler function found for OHLCV tool '{tool_name}' in ohlcv_tools. Skipping.")
            continue

        try:
            description = tool_def_info.get("description", handler_func.__doc__ or "")
            # FastMCP infers input_schema and output_schema from type hints and docstrings.
            # The explicit schemas in TOOL_DEF are for documentation/alternative registration.
            mcp_instance.tool(
                name=tool_name,
                description=description
            )(handler_func)
            logger.info(f"OHLCV Tool '{tool_name}' registered successfully via ohlcv_tools.register_tools.")
            registered_count += 1
        except Exception as e:
            logger.error(f"Failed to register OHLCV tool '{tool_name}' via ohlcv_tools.register_tools: {e}", exc_info=True)
    
    if registered_count == 0:
        logger.warning("No OHLCV tools were successfully registered by ohlcv_tools.register_tools.")
    else:
        logger.info(f"Successfully registered {registered_count} OHLCV tool(s) via ohlcv_tools.register_tools.")


if __name__ == '__main__':
    # Example of how to run this function directly for testing
    # You would need to set the POLYGON_API_KEY environment variable
    # e.g., export POLYGON_API_KEY='YOUR_API_KEY'
    import asyncio

    async def main_test():
        if not POLYGON_API_KEY:
            print("POLYGON_API_KEY environment variable not set. Please set it to test.")
            return

        print("--- Testing get_previous_day_bar ---")
        print("Testing get_previous_day_bar for AAPL...")
        result_aapl_prev = await get_previous_day_bar(ticker="AAPL")
        print(f"AAPL Prev Day Result: {result_aapl_prev}\n")

        print("Testing get_previous_day_bar for a non-existent ticker (e.g., INVALIDTICKER)...")
        result_invalid_prev = await get_previous_day_bar(ticker="INVALIDTICKERXYZ")
        print(f"INVALIDTICKERXYZ Prev Day Result: {result_invalid_prev}\n")

        print("\n--- Testing get_custom_bars ---")
        print("Testing get_custom_bars for AAPL (1 day bar, 2023-01-05 to 2023-01-05)...")
        # Note: Polygon free tier might have delays or limitations for recent data.
        # Using a historical date for better test reliability.
        result_aapl_custom = await get_custom_bars(
            ticker="AAPL",
            multiplier=1,
            timespan="day",
            from_date="2023-01-05",
            to_date="2023-01-05"
        )
        print(f"AAPL Custom Bars (2023-01-05) Result: {result_aapl_custom}\n")

        # print("Testing get_custom_bars for MSFT (1 hour bars, 2023-01-05)...")
        # result_msft_custom_hour = await get_custom_bars(
        #     ticker="MSFT",
        #     multiplier=1,
        #     timespan="hour",
        #     from_date="2023-01-05",
        #     to_date="2023-01-05",
        #     limit=5 # Limit for brevity
        # )
        # print(f"MSFT Custom Hourly Bars (2023-01-05) Result: {result_msft_custom_hour}\n")

        print("\n--- Testing get_daily_market_summary ---")
        print("Testing get_daily_market_summary for 2023-01-09 (US Market)...")
        # Using a historical date for better test reliability.
        result_market_summary = await get_daily_market_summary(date="2023-01-09")
        if result_market_summary and "results" in result_market_summary:
            print(f"Daily Market Summary (2023-01-09) Result: Found {result_market_summary.get('resultsCount')} items. (Not printing all items for brevity)\n")
        else:
            print(f"Daily Market Summary (2023-01-09) Result: {result_market_summary}\n")

        print("\n--- Testing get_daily_ticker_summary ---")
        print("Testing get_daily_ticker_summary for AAPL on 2023-01-09...")
        result_aapl_daily_summary = await get_daily_ticker_summary(ticker="AAPL", date="2023-01-09")
        print(f"AAPL Daily Ticker Summary (2023-01-09) Result: {result_aapl_daily_summary}\n")

        print("Testing get_daily_ticker_summary for an invalid ticker (INVALIDTICKERXYZ) on 2023-01-09...")
        result_invalid_daily_summary = await get_daily_ticker_summary(ticker="INVALIDTICKERXYZ", date="2023-01-09")
        print(f"INVALIDTICKERXYZ Daily Ticker Summary (2023-01-09) Result: {result_invalid_daily_summary}\n")


    if os.name == 'nt': # Fix for "RuntimeError: Event loop is closed" on Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main_test())

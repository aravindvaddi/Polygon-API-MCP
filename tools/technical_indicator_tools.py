import httpx
import os
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP, Context

# This assumes 'mcp' is an instance of FastMCP defined in your main server.py
# and that this file will be imported and tools registered there.
# If running this file standalone for testing, you'd initialize mcp here:
# mcp = FastMCP("PolygonTechnicalIndicators")

POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"

async def _fetch_indicator_data(indicator_path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to fetch data for a technical indicator."""
    if not POLYGON_API_KEY:
        return {"error": "POLYGON_API_KEY not set"}

    headers = {"Authorization": f"Bearer {POLYGON_API_KEY}"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}{indicator_path}", params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"API request failed with status {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

# Tools will be added below, to be registered on an mcp instance in server.py
# For example, in server.py:
# from .tools import technical_indicator_tools
# technical_indicator_tools.register_tools(mcp) # You'd need a register_tools function here or register one by one

# --- Tool Definitions ---

SMA_TOOL_DEF: Dict[str, Any] = {
    "tool_name": "get_sma",
    "description": "Get Simple Moving Average (SMA) data for a stock ticker. SMA is a technical indicator that calculates the average of a selected range of prices, usually closing prices, by the number of periods in that range."
    # Schemas will be inferred by FastMCP from function signature and docstring
}

EMA_TOOL_DEF: Dict[str, Any] = {
    "tool_name": "get_ema",
    "description": "Get Exponential Moving Average (EMA) data for a stock ticker. EMA is a type of moving average that places a greater weight and significance on the most recent data points."
}

MACD_TOOL_DEF: Dict[str, Any] = {
    "tool_name": "get_macd",
    "description": "Get Moving Average Convergence Divergence (MACD) data for a stock ticker. MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a security’s price."
}

RSI_TOOL_DEF: Dict[str, Any] = {
    "tool_name": "get_rsi",
    "description": "Get Relative Strength Index (RSI) data for a stock ticker. RSI is a momentum oscillator that measures the speed and change of price movements."
}

ALL_INDICATOR_TOOL_DEFS: List[Dict[str, Any]] = [
    SMA_TOOL_DEF,
    EMA_TOOL_DEF,
    MACD_TOOL_DEF,
    RSI_TOOL_DEF,
]

# --- Tool Handlers ---
# (Functions get_sma, get_ema, get_macd, get_rsi are defined below)

INDICATOR_TOOL_HANDLERS = {
    "get_sma": lambda stockTicker, timestamp=None, timestamp_gte=None, timestamp_gt=None, timestamp_lte=None, timestamp_lt=None, timespan="day", adjusted=True, window=50, series_type="close", expand_underlying=False, order="desc", limit=10: get_sma(stockTicker, timestamp, timestamp_gte, timestamp_gt, timestamp_lte, timestamp_lt, timespan, adjusted, window, series_type, expand_underlying, order, limit),
    "get_ema": lambda stockTicker, timestamp=None, timestamp_gte=None, timestamp_gt=None, timestamp_lte=None, timestamp_lt=None, timespan="day", adjusted=True, window=50, series_type="close", expand_underlying=False, order="desc", limit=10: get_ema(stockTicker, timestamp, timestamp_gte, timestamp_gt, timestamp_lte, timestamp_lt, timespan, adjusted, window, series_type, expand_underlying, order, limit),
    "get_macd": lambda stockTicker, timestamp=None, timestamp_gte=None, timestamp_gt=None, timestamp_lte=None, timestamp_lt=None, timespan="day", adjusted=True, short_window=12, long_window=26, signal_window=9, series_type="close", expand_underlying=False, order="desc", limit=10: get_macd(stockTicker, timestamp, timestamp_gte, timestamp_gt, timestamp_lte, timestamp_lt, timespan, adjusted, short_window, long_window, signal_window, series_type, expand_underlying, order, limit),
    "get_rsi": lambda stockTicker, timestamp=None, timestamp_gte=None, timestamp_gt=None, timestamp_lte=None, timestamp_lt=None, timespan="day", adjusted=True, window=14, series_type="close", expand_underlying=False, order="desc", limit=10: get_rsi(stockTicker, timestamp, timestamp_gte, timestamp_gt, timestamp_lte, timestamp_lt, timespan, adjusted, window, series_type, expand_underlying, order, limit),
}

# --- Registration Function ---
import logging
logger = logging.getLogger(__name__)

def register_tools(mcp_instance: FastMCP):
    """Registers all technical indicator tools with the provided FastMCP instance."""
    registered_count = 0
    for tool_def_info in ALL_INDICATOR_TOOL_DEFS:
        tool_name = tool_def_info.get("tool_name")
        handler_func = INDICATOR_TOOL_HANDLERS.get(tool_name)

        if not tool_name:
            logger.warning("Found an indicator tool definition without a 'tool_name'. Skipping.")
            continue
        if not handler_func:
            logger.warning(f"No handler function found for indicator tool '{tool_name}'. Skipping.")
            continue

        try:
            description = tool_def_info.get("description", handler_func.__doc__ or "")
            mcp_instance.tool(
                name=tool_name,
                description=description
            )(handler_func) # Pass the actual async function
            logger.info(f"Indicator Tool '{tool_name}' registered successfully.")
            registered_count += 1
        except Exception as e:
            logger.error(f"Failed to register indicator tool '{tool_name}': {e}", exc_info=True)
    
    if registered_count == 0:
        logger.warning("No indicator tools were successfully registered.")
    else:
        logger.info(f"Successfully registered {registered_count} indicator tool(s).")

# --- Simple Moving Average (SMA) ---
async def get_sma(
    stockTicker: str,
    # ctx: Context, # MCP Context for logging, etc. - REMOVED
    timestamp: Optional[str] = None,
    timestamp_gte: Optional[str] = None,
    timestamp_gt: Optional[str] = None,
    timestamp_lte: Optional[str] = None,
    timestamp_lt: Optional[str] = None,
    timespan: Optional[str] = "day",
    adjusted: Optional[bool] = True,
    window: Optional[int] = 50,
    series_type: Optional[str] = "close",
    expand_underlying: Optional[bool] = False,
    order: Optional[str] = "desc",
    limit: Optional[int] = 10
) -> Dict[str, Any]:
    """
    Get Simple Moving Average (SMA) data for a stock ticker.
    SMA is a technical indicator that calculates the average of a selected range of prices,
    usually closing prices, by the number of periods in that range.

    Args:
        stockTicker: The ticker symbol of the stock.
        timestamp: Query by timestamp. Either a date with the format YYYY-MM-DD or a millisecond timestamp.
        timestamp_gte: Timestamp greater than or equal to.
        timestamp_gt: Timestamp greater than.
        timestamp_lte: Timestamp less than or equal to.
        timestamp_lt: Timestamp less than.
        timespan: The size of the time window. Default: "day". Enum: "minute", "hour", "day", "week", "month", "quarter", "year".
        adjusted: Whether the aggregates used to calculate the SMA are adjusted for splits. Default: True.
        window: The window size for the SMA. Default: 50.
        series_type: The price series to use (e.g., "close", "open", "high", "low"). Default: "close".
        expand_underlying: Whether to include the underlying aggregate data in the response. Default: False.
        order: The order in which to return the results. Default: "desc". Enum: "asc", "desc".
        limit: Limit the number of results returned. Default: 10, Max: 5000.
    """
    params = {
        "timespan": timespan,
        "adjusted": str(adjusted).lower(),
        "window": window,
        "series_type": series_type,
        "expand_underlying": str(expand_underlying).lower(),
        "order": order,
        "limit": limit,
    }
    if timestamp:
        params["timestamp"] = timestamp
    if timestamp_gte:
        params["timestamp.gte"] = timestamp_gte
    if timestamp_gt:
        params["timestamp.gt"] = timestamp_gt
    if timestamp_lte:
        params["timestamp.lte"] = timestamp_lte
    if timestamp_lt:
        params["timestamp.lt"] = timestamp_lt
    
    # Remove None params
    params = {k: v for k, v in params.items() if v is not None}

    path = f"/v1/indicators/sma/{stockTicker}"
    # ctx.info(f"Fetching SMA for {stockTicker} with params: {params}") # REMOVED CTX USAGE
    logger.info(f"Fetching SMA for {stockTicker} with params: {params}") # Added basic logging
    return await _fetch_indicator_data(path, params)


# --- Exponential Moving Average (EMA) ---
async def get_ema(
    stockTicker: str,
    # ctx: Context, # MCP Context for logging, etc. - REMOVED
    timestamp: Optional[str] = None,
    timestamp_gte: Optional[str] = None,
    timestamp_gt: Optional[str] = None,
    timestamp_lte: Optional[str] = None,
    timestamp_lt: Optional[str] = None,
    timespan: Optional[str] = "day",
    adjusted: Optional[bool] = True,
    window: Optional[int] = 50,
    series_type: Optional[str] = "close",
    expand_underlying: Optional[bool] = False,
    order: Optional[str] = "desc",
    limit: Optional[int] = 10
) -> Dict[str, Any]:
    """
    Get Exponential Moving Average (EMA) data for a stock ticker.
    EMA is a type of moving average that places a greater weight and significance on the most recent data points.

    Args:
        stockTicker: The ticker symbol of the stock.
        timestamp: Query by timestamp. Either a date with the format YYYY-MM-DD or a millisecond timestamp.
        timestamp_gte: Timestamp greater than or equal to.
        timestamp_gt: Timestamp greater than.
        timestamp_lte: Timestamp less than or equal to.
        timestamp_lt: Timestamp less than.
        timespan: The size of the time window. Default: "day". Enum: "minute", "hour", "day", "week", "month", "quarter", "year".
        adjusted: Whether the aggregates used to calculate the EMA are adjusted for splits. Default: True.
        window: The window size for the EMA. Default: 50.
        series_type: The price series to use (e.g., "close", "open", "high", "low"). Default: "close".
        expand_underlying: Whether to include the underlying aggregate data in the response. Default: False.
        order: The order in which to return the results. Default: "desc". Enum: "asc", "desc".
        limit: Limit the number of results returned. Default: 10, Max: 5000.
    """
    params = {
        "timespan": timespan,
        "adjusted": str(adjusted).lower(),
        "window": window,
        "series_type": series_type,
        "expand_underlying": str(expand_underlying).lower(),
        "order": order,
        "limit": limit,
    }
    if timestamp:
        params["timestamp"] = timestamp
    if timestamp_gte:
        params["timestamp.gte"] = timestamp_gte
    if timestamp_gt:
        params["timestamp.gt"] = timestamp_gt
    if timestamp_lte:
        params["timestamp.lte"] = timestamp_lte
    if timestamp_lt:
        params["timestamp.lt"] = timestamp_lt

    # Remove None params
    params = {k: v for k, v in params.items() if v is not None}

    path = f"/v1/indicators/ema/{stockTicker}"
    # ctx.info(f"Fetching EMA for {stockTicker} with params: {params}") # REMOVED CTX USAGE
    logger.info(f"Fetching EMA for {stockTicker} with params: {params}") # Added basic logging
    return await _fetch_indicator_data(path, params)


# --- Moving Average Convergence Divergence (MACD) ---
async def get_macd(
    stockTicker: str,
    # ctx: Context, # MCP Context for logging, etc. - REMOVED
    timestamp: Optional[str] = None,
    timestamp_gte: Optional[str] = None,
    timestamp_gt: Optional[str] = None,
    timestamp_lte: Optional[str] = None,
    timestamp_lt: Optional[str] = None,
    timespan: Optional[str] = "day",
    adjusted: Optional[bool] = True,
    short_window: Optional[int] = 12,
    long_window: Optional[int] = 26,
    signal_window: Optional[int] = 9,
    series_type: Optional[str] = "close",
    expand_underlying: Optional[bool] = False,
    order: Optional[str] = "desc",
    limit: Optional[int] = 10
) -> Dict[str, Any]:
    """
    Get Moving Average Convergence Divergence (MACD) data for a stock ticker.
    MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a security’s price.

    Args:
        stockTicker: The ticker symbol of the stock.
        timestamp: Query by timestamp. Either a date with the format YYYY-MM-DD or a millisecond timestamp.
        timestamp_gte: Timestamp greater than or equal to.
        timestamp_gt: Timestamp greater than.
        timestamp_lte: Timestamp less than or equal to.
        timestamp_lt: Timestamp less than.
        timespan: The size of the time window. Default: "day". Enum: "minute", "hour", "day", "week", "month", "quarter", "year".
        adjusted: Whether the aggregates used to calculate the MACD are adjusted for splits. Default: True.
        short_window: The short window size for MACD. Default: 12.
        long_window: The long window size for MACD. Default: 26.
        signal_window: The signal window size for MACD. Default: 9.
        series_type: The price series to use (e.g., "close", "open", "high", "low"). Default: "close".
        expand_underlying: Whether to include the underlying aggregate data in the response. Default: False.
        order: The order in which to return the results. Default: "desc". Enum: "asc", "desc".
        limit: Limit the number of results returned. Default: 10, Max: 5000.
    """
    params = {
        "timespan": timespan,
        "adjusted": str(adjusted).lower(),
        "short_window": short_window,
        "long_window": long_window,
        "signal_window": signal_window,
        "series_type": series_type,
        "expand_underlying": str(expand_underlying).lower(),
        "order": order,
        "limit": limit,
    }
    if timestamp:
        params["timestamp"] = timestamp
    if timestamp_gte:
        params["timestamp.gte"] = timestamp_gte
    if timestamp_gt:
        params["timestamp.gt"] = timestamp_gt
    if timestamp_lte:
        params["timestamp.lte"] = timestamp_lte
    if timestamp_lt:
        params["timestamp.lt"] = timestamp_lt

    # Remove None params
    params = {k: v for k, v in params.items() if v is not None}

    path = f"/v1/indicators/macd/{stockTicker}"
    # ctx.info(f"Fetching MACD for {stockTicker} with params: {params}") # REMOVED CTX USAGE
    logger.info(f"Fetching MACD for {stockTicker} with params: {params}") # Added basic logging
    return await _fetch_indicator_data(path, params)


# --- Relative Strength Index (RSI) ---
async def get_rsi(
    stockTicker: str,
    # ctx: Context, # MCP Context for logging, etc. - REMOVED
    timestamp: Optional[str] = None,
    timestamp_gte: Optional[str] = None,
    timestamp_gt: Optional[str] = None,
    timestamp_lte: Optional[str] = None,
    timestamp_lt: Optional[str] = None,
    timespan: Optional[str] = "day",
    adjusted: Optional[bool] = True,
    window: Optional[int] = 14, # Default for RSI is typically 14
    series_type: Optional[str] = "close",
    expand_underlying: Optional[bool] = False,
    order: Optional[str] = "desc",
    limit: Optional[int] = 10
) -> Dict[str, Any]:
    """
    Get Relative Strength Index (RSI) data for a stock ticker.
    RSI is a momentum oscillator that measures the speed and change of price movements.

    Args:
        stockTicker: The ticker symbol of the stock.
        timestamp: Query by timestamp. Either a date with the format YYYY-MM-DD or a millisecond timestamp.
        timestamp_gte: Timestamp greater than or equal to.
        timestamp_gt: Timestamp greater than.
        timestamp_lte: Timestamp less than or equal to.
        timestamp_lt: Timestamp less than.
        timespan: The size of the time window. Default: "day". Enum: "minute", "hour", "day", "week", "month", "quarter", "year".
        adjusted: Whether the aggregates used to calculate the RSI are adjusted for splits. Default: True.
        window: The window size for the RSI. Default: 14.
        series_type: The price series to use (e.g., "close", "open", "high", "low"). Default: "close".
        expand_underlying: Whether to include the underlying aggregate data in the response. Default: False.
        order: The order in which to return the results. Default: "desc". Enum: "asc", "desc".
        limit: Limit the number of results returned. Default: 10, Max: 5000.
    """
    params = {
        "timespan": timespan,
        "adjusted": str(adjusted).lower(),
        "window": window,
        "series_type": series_type,
        "expand_underlying": str(expand_underlying).lower(),
        "order": order,
        "limit": limit,
    }
    if timestamp:
        params["timestamp"] = timestamp
    if timestamp_gte:
        params["timestamp.gte"] = timestamp_gte
    if timestamp_gt:
        params["timestamp.gt"] = timestamp_gt
    if timestamp_lte:
        params["timestamp.lte"] = timestamp_lte
    if timestamp_lt:
        params["timestamp.lt"] = timestamp_lt

    # Remove None params
    params = {k: v for k, v in params.items() if v is not None}

    path = f"/v1/indicators/rsi/{stockTicker}"
    # ctx.info(f"Fetching RSI for {stockTicker} with params: {params}") # REMOVED CTX USAGE
    logger.info(f"Fetching RSI for {stockTicker} with params: {params}") # Added basic logging
    return await _fetch_indicator_data(path, params)

# Ensure the async functions are defined before INDICATOR_TOOL_HANDLERS uses them.
# The lambda definitions in INDICATOR_TOOL_HANDLERS will capture these functions.

import httpx
import os
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP
import logging

# Module-level logger, used by the registration function.
logger = logging.getLogger(__name__)

POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"

# --- Tool Implementations ---

async def get_sma(
    ticker: str,
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
    """
    if not POLYGON_API_KEY:
        return {"error": "Polygon API key is not configured."}

    path = f"/v1/indicators/sma/{ticker}"
    params = {
        "timestamp": timestamp, "timestamp.gte": timestamp_gte, "timestamp.gt": timestamp_gt,
        "timestamp.lte": timestamp_lte, "timestamp.lt": timestamp_lt, "timespan": timespan,
        "adjusted": str(adjusted).lower(), "window": window, "series_type": series_type,
        "expand_underlying": str(expand_underlying).lower(), "order": order, "limit": limit,
        "apiKey": POLYGON_API_KEY
    }
    params = {k: v for k, v in params.items() if v is not None}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}{path}", params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "OK":
                return data 
            else:
                return {"error": data.get("error", "Failed to fetch SMA data from Polygon API"), "details": data}
        except httpx.HTTPStatusError as e:
            return {"error": f"Polygon API error: {e.response.status_code}", "message": str(e.response.text)}
        except httpx.RequestError as e:
            return {"error": "Failed to connect to Polygon API", "message": str(e)}
        except Exception as e:
            print(f"Unexpected error in get_sma for {ticker}: {e}") 
            return {"error": "An unexpected error occurred."}

async def get_ema(
    ticker: str,
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
    """
    if not POLYGON_API_KEY:
        return {"error": "Polygon API key is not configured."}
    path = f"/v1/indicators/ema/{ticker}"
    params = {
        "timestamp": timestamp, "timestamp.gte": timestamp_gte, "timestamp.gt": timestamp_gt,
        "timestamp.lte": timestamp_lte, "timestamp.lt": timestamp_lt, "timespan": timespan,
        "adjusted": str(adjusted).lower(), "window": window, "series_type": series_type,
        "expand_underlying": str(expand_underlying).lower(), "order": order, "limit": limit,
        "apiKey": POLYGON_API_KEY
    }
    params = {k: v for k, v in params.items() if v is not None}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}{path}", params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "OK":
                return data
            else:
                return {"error": data.get("error", "Failed to fetch EMA data from Polygon API"), "details": data}
        except httpx.HTTPStatusError as e:
            return {"error": f"Polygon API error: {e.response.status_code}", "message": str(e.response.text)}
        except httpx.RequestError as e:
            return {"error": "Failed to connect to Polygon API", "message": str(e)}
        except Exception as e:
            print(f"Unexpected error in get_ema for {ticker}: {e}")
            return {"error": "An unexpected error occurred."}

async def get_macd(
    ticker: str,
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
    """
    if not POLYGON_API_KEY:
        return {"error": "Polygon API key is not configured."}
    path = f"/v1/indicators/macd/{ticker}"
    params = {
        "timestamp": timestamp, "timestamp.gte": timestamp_gte, "timestamp.gt": timestamp_gt,
        "timestamp.lte": timestamp_lte, "timestamp.lt": timestamp_lt, "timespan": timespan,
        "adjusted": str(adjusted).lower(), "short_window": short_window, "long_window": long_window,
        "signal_window": signal_window, "series_type": series_type,
        "expand_underlying": str(expand_underlying).lower(), "order": order, "limit": limit,
        "apiKey": POLYGON_API_KEY
    }
    params = {k: v for k, v in params.items() if v is not None}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}{path}", params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "OK":
                return data
            else:
                return {"error": data.get("error", "Failed to fetch MACD data from Polygon API"), "details": data}
        except httpx.HTTPStatusError as e:
            return {"error": f"Polygon API error: {e.response.status_code}", "message": str(e.response.text)}
        except httpx.RequestError as e:
            return {"error": "Failed to connect to Polygon API", "message": str(e)}
        except Exception as e:
            print(f"Unexpected error in get_macd for {ticker}: {e}")
            return {"error": "An unexpected error occurred."}

async def get_rsi(
    ticker: str,
    timestamp: Optional[str] = None,
    timestamp_gte: Optional[str] = None,
    timestamp_gt: Optional[str] = None,
    timestamp_lte: Optional[str] = None,
    timestamp_lt: Optional[str] = None,
    timespan: Optional[str] = "day",
    adjusted: Optional[bool] = True,
    window: Optional[int] = 14, 
    series_type: Optional[str] = "close",
    expand_underlying: Optional[bool] = False,
    order: Optional[str] = "desc",
    limit: Optional[int] = 10
) -> Dict[str, Any]:
    """
    Get Relative Strength Index (RSI) data for a stock ticker.
    RSI is a momentum oscillator that measures the speed and change of price movements.
    """
    if not POLYGON_API_KEY:
        return {"error": "Polygon API key is not configured."}
    path = f"/v1/indicators/rsi/{ticker}"
    params = {
        "timestamp": timestamp, "timestamp.gte": timestamp_gte, "timestamp.gt": timestamp_gt,
        "timestamp.lte": timestamp_lte, "timestamp.lt": timestamp_lt, "timespan": timespan,
        "adjusted": str(adjusted).lower(), "window": window, "series_type": series_type,
        "expand_underlying": str(expand_underlying).lower(), "order": order, "limit": limit,
        "apiKey": POLYGON_API_KEY
    }
    params = {k: v for k, v in params.items() if v is not None}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}{path}", params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "OK":
                return data
            else:
                return {"error": data.get("error", "Failed to fetch RSI data from Polygon API"), "details": data}
        except httpx.HTTPStatusError as e:
            return {"error": f"Polygon API error: {e.response.status_code}", "message": str(e.response.text)}
        except httpx.RequestError as e:
            return {"error": "Failed to connect to Polygon API", "message": str(e)}
        except Exception as e:
            print(f"Unexpected error in get_rsi for {ticker}: {e}")
            return {"error": "An unexpected error occurred."}

# --- Tool Definitions ---

_INDICATOR_COMMON_INPUT_PROPS = {
    "ticker": {"type": "string", "description": "The stock ticker symbol (e.g., 'AAPL')."},
    "timestamp": {"type": "string", "description": "Query by timestamp. Either a date with the format YYYY-MM-DD or a millisecond timestamp.", "optional": True},
    "timestamp_gte": {"type": "string", "description": "Timestamp greater than or equal to.", "optional": True},
    "timestamp_gt": {"type": "string", "description": "Timestamp greater than.", "optional": True},
    "timestamp_lte": {"type": "string", "description": "Timestamp less than or equal to.", "optional": True},
    "timestamp_lt": {"type": "string", "description": "Timestamp less than.", "optional": True},
    "timespan": {"type": "string", "default": "day", "enum": ["minute", "hour", "day", "week", "month", "quarter", "year"], "description": "The size of the time window."},
    "adjusted": {"type": "boolean", "default": True, "description": "Whether the aggregates are adjusted for splits."},
    "series_type": {"type": "string", "default": "close", "enum": ["open", "high", "low", "close"], "description": "The price series to use."},
    "expand_underlying": {"type": "boolean", "default": False, "description": "Include underlying aggregate data."},
    "order": {"type": "string", "default": "desc", "enum": ["asc", "desc"], "description": "Order of results."},
    "limit": {"type": "integer", "default": 10, "description": "Limit the number of results (Max: 5000)."}
}

_INDICATOR_VALUE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "timestamp": {"type": "integer", "description": "Unix Msec timestamp of the indicator value."},
        "value": {"type": "number", "description": "The calculated indicator value."}
    },
    "required": ["timestamp", "value"]
}

_MACD_VALUE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "timestamp": {"type": "integer", "description": "Unix Msec timestamp of the indicator value."},
        "value": {"type": "number", "description": "The MACD line value."},
        "signal": {"type": "number", "description": "The signal line value."},
        "histogram": {"type": "number", "description": "The histogram value (MACD - Signal)."}
    },
    "required": ["timestamp", "value", "signal", "histogram"]
}

_INDICATOR_RESULTS_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "values": { "type": "array", "items": _INDICATOR_VALUE_OUTPUT_SCHEMA },
        "underlying": {
            "type": "object", "description": "Present if expand_underlying is true.",
            "properties": { "url": {"type": "string"}, "aggregates": {"type": "array", "items": {"type": "object"}} }
        }
    }
}

_MACD_RESULTS_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "values": { "type": "array", "items": _MACD_VALUE_OUTPUT_SCHEMA },
        "underlying": {
            "type": "object", "description": "Present if expand_underlying is true.",
            "properties": { "url": {"type": "string"}, "aggregates": {"type": "array", "items": {"type": "object"}} }
        }
    }
}

_INDICATOR_BASE_OUTPUT_SCHEMA_PROPERTIES = {
    "status": {"type": "string"}, "request_id": {"type": "string"},
    "next_url": {"type": "string", "description": "URL for the next page of results, if applicable."},
    "error": {"type": "string", "description": "Error message if the call failed."}
}

SMA_TOOL_DEF: Dict[str, Any] = {
    "tool_name": "get_sma", "description": get_sma.__doc__,
    "input_schema": {
        "type": "object",
        "properties": {**_INDICATOR_COMMON_INPUT_PROPS, "window": {"type": "integer", "default": 50, "description": "The window size for the SMA."}},
        "required": ["ticker"]
    },
    "output_schema": {"type": "object", "properties": {**_INDICATOR_BASE_OUTPUT_SCHEMA_PROPERTIES, "results": _INDICATOR_RESULTS_OUTPUT_SCHEMA}}
}

EMA_TOOL_DEF: Dict[str, Any] = {
    "tool_name": "get_ema", "description": get_ema.__doc__,
    "input_schema": {
        "type": "object",
        "properties": {**_INDICATOR_COMMON_INPUT_PROPS, "window": {"type": "integer", "default": 50, "description": "The window size for the EMA."}},
        "required": ["ticker"]
    },
    "output_schema": {"type": "object", "properties": {**_INDICATOR_BASE_OUTPUT_SCHEMA_PROPERTIES, "results": _INDICATOR_RESULTS_OUTPUT_SCHEMA}}
}

MACD_TOOL_DEF: Dict[str, Any] = {
    "tool_name": "get_macd", "description": get_macd.__doc__,
    "input_schema": {
        "type": "object",
        "properties": {
            **_INDICATOR_COMMON_INPUT_PROPS,
            "short_window": {"type": "integer", "default": 12, "description": "The short window size for MACD."},
            "long_window": {"type": "integer", "default": 26, "description": "The long window size for MACD."},
            "signal_window": {"type": "integer", "default": 9, "description": "The signal window size for MACD."}
        },
        "required": ["ticker"]
    },
    "output_schema": {"type": "object", "properties": {**_INDICATOR_BASE_OUTPUT_SCHEMA_PROPERTIES, "results": _MACD_RESULTS_OUTPUT_SCHEMA}}
}

RSI_TOOL_DEF: Dict[str, Any] = {
    "tool_name": "get_rsi", "description": get_rsi.__doc__,
    "input_schema": { 
        "type": "object",
        "properties": {**_INDICATOR_COMMON_INPUT_PROPS, "window": {"type": "integer", "default": 14, "description": "The window size for the RSI."}},
        "required": ["ticker"]
    },
    "output_schema": {"type": "object", "properties": {**_INDICATOR_BASE_OUTPUT_SCHEMA_PROPERTIES, "results": _INDICATOR_RESULTS_OUTPUT_SCHEMA}}
}

ALL_INDICATOR_TOOL_DEFS: List[Dict[str, Any]] = [SMA_TOOL_DEF, EMA_TOOL_DEF, MACD_TOOL_DEF, RSI_TOOL_DEF]

INDICATOR_TOOL_HANDLERS = {
    "get_sma": get_sma, "get_ema": get_ema,
    "get_macd": get_macd, "get_rsi": get_rsi,
}

# --- Registration Function ---
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
            # FastMCP infers input_schema and output_schema from type hints and docstrings
            # of the handler_func. We only need to pass name and description.
            mcp_instance.tool(
                name=tool_name,
                description=tool_def_info.get("description")
            )(handler_func)
            logger.info(f"Indicator Tool '{tool_name}' registered successfully.")
            registered_count += 1
        except Exception as e:
            logger.error(f"Failed to register indicator tool '{tool_name}': {e}", exc_info=True)
    
    if registered_count == 0:
        logger.warning("No indicator tools were successfully registered.")
    else:
        logger.info(f"Successfully registered {registered_count} indicator tool(s).")

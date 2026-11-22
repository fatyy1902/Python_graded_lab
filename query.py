"""Running queries against the flight database."""
import math

from validator import parse_exact_datetime

_RECORD_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
}
_ALLOWED_QUERY_KEYS = _RECORD_KEYS | {"min_price", "sort_by", "order", "limit"}

def _is_valid_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _is_valid_query(query: object) -> bool:
    if not isinstance(query, dict):
        return False

    if any(key not in _ALLOWED_QUERY_KEYS for key in query):
        return False

    if "order" in query and "sort_by" not in query:
        return False

    for key in ("flight_id", "origin", "destination"):
        if key in query and not isinstance(query[key], str):
            return False

    for key in ("departure_datetime", "arrival_datetime"):
        if key in query:
            if not isinstance(query[key], str) or parse_exact_datetime(query[key]) is None:
                return False

    for key in ("price", "min_price"):
        if key in query and not _is_valid_number(query[key]):
            return False

    if "sort_by" in query:
        if not isinstance(query["sort_by"], str) or query["sort_by"] not in _RECORD_KEYS:
            return False

    if "order" in query:
        if not isinstance(query["order"], str) or query["order"] not in ("asc", "desc"):
            return False

    if "limit" in query:
        val = query["limit"]
        if not isinstance(val, int) or isinstance(val, bool) or val < 0:
            return False

    return True


def _matches(flight: dict, query: dict) -> bool:
    if "flight_id" in query and flight["flight_id"] != query["flight_id"]:
        return False
    if "origin" in query and flight["origin"] != query["origin"]:
        return False
    if "destination" in query and flight["destination"] != query["destination"]:
        return False
    if "departure_datetime" in query and flight["departure_datetime"] < query["departure_datetime"]:
        return False
    if "arrival_datetime" in query and flight["arrival_datetime"] > query["arrival_datetime"]:
        return False
    if "price" in query and flight["price"] > query["price"]:
        return False
    if "min_price" in query and flight["price"] < query["min_price"]:
        return False
    return True

def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    if not _is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = [flight for flight in db if _matches(flight, query)]

    if "sort_by" in query:
        sort_key = query["sort_by"]
        reverse = query.get("order", "asc") == "desc"
        matches = sorted(matches, key=lambda r: r[sort_key], reverse=reverse)

    if "limit" in query:
        matches = matches[: query["limit"]]

    return {"query": query, "matches": matches}
    raise NotImplementedError


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    query_list = [queries] if isinstance(queries, dict) else queries
    return [run_query(db, q) for q in query_list]
    raise NotImplementedError

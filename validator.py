"""Row validation: airport list loading, single-row checks, record building."""
from datetime import datetime
import math
import re

_FLIGHT_ID_RE = re.compile(r"^[A-Za-z0-9]{2,8}$")
_AIRPORT_RE = re.compile(r"^[A-Z]{3}$")
_DATETIME_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}$")

def parse_exact_datetime(value: str) -> datetime | None:
    """Parse YYYY-MM-DD HH:MM strictly (zero-padded ASCII digits, 24-hour, single space)."""
    if not _DATETIME_RE.fullmatch(value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    airports: set[str] = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            code = line.strip()
            if not code or code.startswith("#"):
                continue
            airports.add(code)
    return airports
    raise NotImplementedError


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    stripped = [field.strip() for field in fields]

    if any(field == "" for field in stripped):
        return "MISSING_FIELD"

    flight_id, origin, destination, dep_str, arr_str, price_str = stripped

    if not _FLIGHT_ID_RE.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"

    if not _AIRPORT_RE.fullmatch(origin) or origin not in airports:
        return "INVALID_ORIGIN"

    if not _AIRPORT_RE.fullmatch(destination) or destination not in airports:
        return "INVALID_DESTINATION"

    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    dep_dt = parse_exact_datetime(dep_str)
    if dep_dt is None:
        return "INVALID_DEPARTURE"

    arr_dt = parse_exact_datetime(arr_str)
    if arr_dt is None:
        return "INVALID_ARRIVAL"

    if arr_dt <= dep_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price = float(price_str)
    except ValueError:
        return "INVALID_PRICE"
    if not math.isfinite(price):
        return "INVALID_PRICE"

    if price <= 0:
        return "NON_POSITIVE_PRICE"

    return None
    raise NotImplementedError


def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    flight_id, origin, destination, dep_str, arr_str, price_str = (
        field.strip() for field in fields
    )
    return {
        "flight_id": flight_id,
        "origin": origin,
        "destination": destination,
        "departure_datetime": dep_str,
        "arrival_datetime": arr_str,
        "price": float(price_str),
    }
    raise NotImplementedError

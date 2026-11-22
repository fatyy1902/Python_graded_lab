"""Reading CSV files into flight records and error messages."""
import csv
import os

from validator import to_record, validate_row


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """

    records: list[dict] = []
    errors: list[str] = []
    seen_flights: set[tuple[str, str]] = set()

    for path in paths:
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8", newline="") as f:
            for line_num, raw_line in enumerate(f, start=1):
                if line_num == 1:
                    continue

                stripped_line = raw_line.strip()
                if not stripped_line or stripped_line.startswith("#"):
                    continue

                clean_line = raw_line.rstrip("\r\n")
                fields = next(csv.reader([clean_line]))

                error_code = validate_row(fields, airports)
                if error_code is not None:
                    errors.append(f"{filename}:{line_num}: {error_code} | {clean_line}")
                    continue

                record = to_record(fields)
                flight_key = (record["flight_id"], record["departure_datetime"])

                if flight_key in seen_flights:
                    errors.append(
                        f"{filename}:{line_num}: DUPLICATE_FLIGHT | {clean_line}"
                    )
                    continue

                seen_flights.add(flight_key)
                records.append(record)

    return records, errors
    raise NotImplementedError

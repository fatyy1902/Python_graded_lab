"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import sys
import argparse
import json
import logging
import os
from datetime import datetime

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "260ADB182"
FIRST_NAME = "Sokhna"
LAST_NAME = "GUEYE"

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate flight schedule CSVs, build a JSON database, and run queries."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE", help="Parse a single CSV file.")
    source.add_argument(
        "-d", metavar="FOLDER", help="Parse all .csv files in a folder (sorted)."
    )
    source.add_argument(
        "-j", metavar="FILE", help="Load an existing JSON database instead of CSVs."
    )

    parser.add_argument(
        "-a", metavar="FILE", help="Airport list file (required with -i and -d)."
    )
    parser.add_argument(
        "-o",
        metavar="FILE",
        default=None,
        help="Output path for the JSON database (default: db.json; only with -i or -d).",
    )
    parser.add_argument(
        "-q", metavar="FILE", help="Run queries from this JSON file against the database."
    )
    parser.add_argument(
        "-r",
        metavar="FOLDER",
        default=".",
        help="Folder for the query response file (default: current directory).",
    )
    return parser


def _print_error(message: str) -> int:
    print(f"Error: {message}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    # TODO: parse arguments with argparse (-i, -d, -j, -a, -o, -q, -r).
    # TODO: load or parse the data, write the database and errors.log.
    # TODO: run the queries and write the response file.
    # Remember: remove and close the logging handler before returning,
    # also when returning early because of an error (use try/finally).
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
        if (args.i or args.d) and not args.a:
            parser.error("-a is required when using -i or -d.")
        if args.j and args.o is not None:
            parser.error("-o cannot be used with -j.")
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    db: list[dict] = []

    if args.i or args.d:
        try:
            airports = load_airports(args.a)
        except OSError as exc:
            return _print_error(f"Cannot read airport file '{args.a}': {exc}")

        if args.i:
            if not os.path.isfile(args.i):
                return _print_error(f"Input file not found: '{args.i}'")
            csv_paths = [args.i]
        else:
            if not os.path.isdir(args.d):
                return _print_error(f"Input folder not found: '{args.d}'")
            try:
                entries = sorted(os.listdir(args.d))
            except OSError as exc:
                return _print_error(f"Cannot read folder '{args.d}': {exc}")
            csv_paths = [
                os.path.join(args.d, name)
                for name in entries
                if name.endswith(".csv") and os.path.isfile(os.path.join(args.d, name))
            ]
            if not csv_paths:
                return _print_error(f"No .csv files found in '{args.d}'")

        output_path = args.o if args.o is not None else "db.json"
        log_dir = os.path.dirname(os.path.abspath(output_path))
        log_path = os.path.join(log_dir, "errors.log")

        logger = logging.getLogger("flight_parser")
        logger.setLevel(logging.INFO)
        handler: logging.FileHandler | None = None
        try:
            handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            logger.addHandler(handler)

            db, errors = parse_files(csv_paths, airports)
            for err_msg in errors:
                logger.warning(err_msg)

            with open(output_path, "w", encoding="utf-8") as out_f:
                json.dump(db, out_f, indent=2)
        except OSError as exc:
            return _print_error(f"File operation failed: {exc}")
        finally:
            if handler is not None:
                logger.removeHandler(handler)
                handler.close()

    else:
        try:
            with open(args.j, "r", encoding="utf-8") as f:
                loaded = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            return _print_error(f"Cannot load JSON database '{args.j}': {exc}")

        if not isinstance(loaded, list) or not all(isinstance(item, dict) for item in loaded):
            return _print_error("JSON database must be a JSON array of objects.")
        db = loaded

    if args.q:
        try:
            with open(args.q, "r", encoding="utf-8") as f:
                raw_queries = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            return _print_error(f"Cannot load query file '{args.q}': {exc}")

        valid_shape = isinstance(raw_queries, dict) or (
            isinstance(raw_queries, list)
            and all(isinstance(q, dict) for q in raw_queries)
        )
        if not valid_shape:
            return _print_error(
                "Query file must contain a JSON object or an array of JSON objects."
            )

        results = run_queries(db, raw_queries)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        response_filename = (
            f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp}.json"
        )
        response_path = os.path.join(args.r, response_filename)

        try:
            with open(response_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        except OSError as exc:
            return _print_error(f"Cannot write response file '{response_path}': {exc}")

 return 0



if __name__ == "__main__":
    sys.exit(main())

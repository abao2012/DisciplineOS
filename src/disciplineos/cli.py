from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import to_dict
from .services import DisciplineService, seed_demo_data


def main(argv: list[str] | None = None) -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--data-dir", default="data", help="Local JSON data directory.")

    parser = argparse.ArgumentParser(
        prog="disciplineos",
        description="Local-first investment discipline operating system.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "demo",
        parents=[common],
        help="Seed demo profile, card, and decision.",
    )

    check_parser = subparsers.add_parser(
        "check",
        parents=[common],
        help="Audit a decision JSON file.",
    )
    check_parser.add_argument("decision_file", type=Path)

    review_parser = subparsers.add_parser(
        "review",
        parents=[common],
        help="Generate monthly review.",
    )
    review_parser.add_argument("--month", required=True, help="Month in YYYY-MM format.")

    web_parser = subparsers.add_parser(
        "web",
        parents=[common],
        help="Start the local web UI.",
    )
    web_parser.add_argument("--host", default="127.0.0.1", help="Bind host.")
    web_parser.add_argument("--port", type=int, default=8765, help="Bind port.")

    args = parser.parse_args(argv)
    service = DisciplineService(args.data_dir)

    if args.command == "demo":
        seed_demo_data(service)
        print_json({"ok": True, "message": "Demo data seeded.", "data_dir": args.data_dir})
        return 0

    if args.command == "check":
        payload = json.loads(args.decision_file.read_text(encoding="utf-8"))
        result = service.check_decision_dict(payload)
        print_json(to_dict(result))
        return 0

    if args.command == "review":
        print_json(service.monthly_review(args.month))
        return 0

    if args.command == "web":
        from .web import run

        run(data_dir=args.data_dir, host=args.host, port=args.port)
        return 0

    return 1


def print_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())

"""CLI to aggregate KPI metrics from SQLite."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from app.utils.kpi_metrics import compute_kpi_summary


def _fetch_sessions(db_path: Path, user_id: int) -> List[Dict[str, Any]]:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        cursor = connection.execute(
            """
            SELECT id, user_id, phase, session_date, report_final, created_at
            FROM sessions
            WHERE user_id = ?
            ORDER BY created_at ASC
            """,
            (user_id,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        connection.close()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate KPI metrics from SQLite")
    parser.add_argument("--db", required=True, help="Path to SQLite DB file")
    parser.add_argument("--user-id", required=True, type=int, help="Target user_id")
    parser.add_argument(
        "--output",
        default="out/kpi_summary.json",
        help="Output JSON path (default: out/kpi_summary.json)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    db_path = Path(args.db).expanduser().resolve()
    output_path = Path(args.output)
    sessions = _fetch_sessions(db_path, args.user_id)
    summary = compute_kpi_summary(args.user_id, sessions)

    print("KPI Summary")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
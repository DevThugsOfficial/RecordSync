import csv
from pathlib import Path
from typing import Optional, Dict, Any, List

DB_DIR = Path(__file__).resolve().parent.parent / "database"
ADMIN_CSV = DB_DIR / "admin.csv"


def _ensure_db_dir():
    DB_DIR.mkdir(parents=True, exist_ok=True)


def _read_admin_csv() -> List[Dict[str, str]]:
    if not ADMIN_CSV.exists():
        return []
    with ADMIN_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def _write_admin_csv(rows: List[Dict[str, Any]]) -> None:
    _ensure_db_dir()
    fieldnames = ["id", "username", "password"]
    with ADMIN_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({"id": int(r.get("id", 0)), "username": r.get("username", ""), "password": r.get("password", "")})


def admin_login(username: str, password: str) -> bool:
    """
    Return True if username/password pair exists in admin.csv
    """
    for row in _read_admin_csv():
        if (row.get("username") or "") == (username or "") and (row.get("password") or "") == (password or ""):
            return True
    return False


def admin_signup(username: str, password: str) -> Dict[str, Any]:
    """
    Add a new admin account and return the created record.
    Raises ValueError if username already exists.
    """
    rows = _read_admin_csv()
    for r in rows:
        if (r.get("username") or "") == (username or ""):
            raise ValueError("username already exists")
    max_id = 0
    for r in rows:
        try:
            max_id = max(max_id, int(r.get("id", 0)))
        except Exception:
            continue
    new_id = max_id + 1
    new_row = {"id": new_id, "username": username or "", "password": password or ""}
    rows.append(new_row)
    _write_admin_csv(rows)
    return new_row
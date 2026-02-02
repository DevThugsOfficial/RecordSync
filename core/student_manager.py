from pathlib import Path
from typing import List, Dict, Any
import csv
import shutil
import re

DB_DIR = Path(__file__).resolve().parent.parent / "database"
PROFILE_DIR = Path(__file__).resolve().parent.parent / "assets" / "profiles"
STUDENTS_CSV = DB_DIR / "Students_Data.csv"
PLACEHOLDER_PHOTO = "/assets/placeholder.png"  # Web path


def _ensure_dirs():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)


def _read_students_csv() -> List[Dict[str, str]]:
    if not STUDENTS_CSV.exists():
        return []
    try:
        with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]
    except Exception:
        return []


def _write_students_csv(rows: List[Dict[str, str]]) -> None:
    _ensure_dirs()
    fieldnames = ["ID", "Name", "Status", "ClassesAttended", "TimeIn", "TimeOut", "Img_Path"]
    with STUDENTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})


def _next_id(rows: List[Dict[str, str]]) -> str:
    max_num = 0
    for r in rows:
        digits = "".join(c for c in (r.get("ID") or "") if c.isdigit())
        if digits:
            try:
                val = int(digits)
                if val > max_num:
                    max_num = val
            except Exception:
                pass
    return f"00-{max_num + 1:03d}"


def _copy_photo_to_profiles(photo_path: str) -> str:
    """Copy uploaded photo to PROFILE_DIR and return Web path for CSV"""
    if not photo_path:
        return ""
    src = Path(photo_path)
    if not src.exists():
        return ""

    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", src.name)
    dest = PROFILE_DIR / safe_name
    try:
        shutil.copy(src, dest)
        # return Web path starting with /assets/
        return f"/assets/profiles/{safe_name}"
    except Exception:
        return ""


def _resolve_photo_path(img_path: str) -> str:
    """Return Web-ready path for Flet Web"""
    if not img_path:
        return PLACEHOLDER_PHOTO
    path = str(img_path).replace("\\", "/")
    if not path.startswith("/assets/"):
        path = "/" + path
    return path


def get_all_students() -> List[Dict[str, Any]]:
    rows = _read_students_csv()
    out: List[Dict[str, Any]] = []

    for r in rows:
        photo = _resolve_photo_path(r.get("Img_Path", ""))
        try:
            attended = int(r.get("ClassesAttended", 0))
        except Exception:
            attended = 0
        out.append(
            {
                "id": r.get("ID", ""),
                "name": r.get("Name", ""),
                "photo": photo,
                "attended": attended,
                "classes_total": 20,
            }
        )
    return out


def add_student(payload: Dict[str, Any]) -> Dict[str, Any]:
    rows = _read_students_csv()
    new_id = _next_id(rows)
    attended = int(payload.get("attended", 0))
    photo_path = _copy_photo_to_profiles(payload.get("photo", ""))

    row = {
        "ID": new_id,
        "Name": payload.get("name", "").strip(),
        "Status": "",
        "ClassesAttended": str(attended),
        "TimeIn": "",
        "TimeOut": "",
        "Img_Path": photo_path,
    }
    rows.append(row)
    _write_students_csv(rows)

    return {
        "id": row["ID"],
        "name": row["Name"],
        "photo": _resolve_photo_path(row["Img_Path"]),
        "attended": attended,
        "classes_total": 20,
    }


def update_student(student_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    rows = _read_students_csv()
    updated = None

    for r in rows:
        if r.get("ID") == student_id:
            if "name" in payload:
                r["Name"] = payload["name"].strip()
            if "photo" in payload:
                r["Img_Path"] = _copy_photo_to_profiles(payload["photo"])
            if "attended" in payload:
                try:
                    r["ClassesAttended"] = str(int(payload["attended"]))
                except Exception:
                    pass
            updated = r
            break

    if updated is None:
        raise KeyError("student not found")
    _write_students_csv(rows)

    return {
        "id": updated["ID"],
        "name": updated["Name"],
        "photo": _resolve_photo_path(updated["Img_Path"]),
        "attended": int(updated.get("ClassesAttended") or 0),
        "classes_total": 20,
    }


def delete_student(student_id: str) -> None:
    rows = _read_students_csv()
    new_rows = [r for r in rows if r.get("ID") != student_id]
    if len(new_rows) == len(rows):
        raise KeyError("student not found")
    _write_students_csv(new_rows)

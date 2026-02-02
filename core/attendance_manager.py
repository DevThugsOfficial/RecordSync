import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

DB_DIR = Path(__file__).resolve().parent.parent / "database"
ATTENDANCE_CSV = DB_DIR / "Students_Data.csv"


def _ensure_db_dir():
    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error creating database directory: {e}")


def _read_attendance_csv() -> List[Dict[str, str]]:
    """Read Students_Data.csv safely"""
    if not ATTENDANCE_CSV.exists():
        return []

    try:
        with ATTENDANCE_CSV.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row for row in reader] if reader else []
    except Exception as e:
        print(f"Error reading attendance CSV: {e}")
        return []


def _write_attendance_csv(rows: List[Dict[str, str]]) -> None:
    """Write updated attendance data back to Students_Data.csv"""
    _ensure_db_dir()
    fieldnames = ["ID", "Name", "Status", "ClassesAttended", "TimeIn", "TimeOut", "Img_Path"]
    
    try:
        with ATTENDANCE_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in fieldnames})
    except Exception as e:
        print(f"Error writing attendance CSV: {e}")
        raise


def _parse_time(time_str: str) -> Optional[datetime.time]:
    """Parse time string in format 'HH:MM AM/PM' to datetime.time"""
    if not time_str or not isinstance(time_str, str):
        return None
    
    try:
        return datetime.strptime(time_str.strip(), "%I:%M %p").time()
    except Exception:
        return None


def _is_time_in_range(time_to_check: Optional[datetime.time], class_start: Optional[datetime.time], class_end: Optional[datetime.time]) -> bool:
    """Check if time_to_check falls within class_start and class_end"""
    if not all([time_to_check, class_start, class_end]):
        return False
    return class_start <= time_to_check <= class_end


def determine_status(time_in: str, class_start_time: str, class_end_time: str, class_start_grace_minutes: int = 5) -> str:
    """
    Determine attendance status based on Time_In and class schedule.
    Returns: "Present" | "Late" | "Absent"
    """
    if not time_in or not time_in.strip():
        return "Absent"
    
    try:
        time_in_parsed = _parse_time(time_in)
        class_start_parsed = _parse_time(class_start_time)
        class_end_parsed = _parse_time(class_end_time)
        
        if not all([time_in_parsed, class_start_parsed, class_end_parsed]):
            return "Absent"
        
        # If checked in after class end -> Absent
        if time_in_parsed > class_end_parsed:
            return "Absent"
        
        grace_end = datetime.combine(datetime.today(), class_start_parsed) + timedelta(minutes=class_start_grace_minutes)
        grace_end_time = grace_end.time()
        
        if time_in_parsed <= grace_end_time:
            return "Present"
        else:
            return "Late"
    except Exception as e:
        print(f"Error determining status: {e}")
        return "Absent"


def update_statuses(class_start_time: str, class_end_time: str, class_start_grace_minutes: int = 5) -> Dict[str, Any]:
    """
    Recompute status for each student in Students_Data.csv based on TimeIn and class schedule.
    - Updates Status field
    - Increments ClassesAttended when a student transitions from non-present to Present/Late
    Returns results dict with counts and errors.
    """
    _ensure_db_dir()
    results = {"updated": 0, "errors": [], "changed": {}}
    try:
        rows = _read_attendance_csv()
        if not rows:
            return results

        # operate on list of dicts; preserve order
        for row in rows:
            try:
                old_status = (row.get("Status") or "").strip()
                time_in = (row.get("TimeIn") or "").strip()
                new_status = determine_status(time_in, class_start_time, class_end_time, class_start_grace_minutes)
                # Only increment when transitioning from non-present to present/late
                if new_status in ("Present", "Late") and old_status not in ("Present", "Late"):
                    try:
                        ca = int(row.get("ClassesAttended") or 0)
                    except Exception:
                        ca = 0
                    ca += 1
                    row["ClassesAttended"] = str(ca)
                # Update status field to normalized value
                row["Status"] = new_status
                results["changed"][row.get("ID", "")] = {"old": old_status, "new": new_status}
                results["updated"] += 1
            except Exception as e:
                results["errors"].append(f"Row update error: {e}")
        # write back
        _write_attendance_csv(rows)
    except Exception as e:
        results["errors"].append(str(e))
        print(f"Error in update_statuses: {e}")
    return results


# backward-compatible name
def sync_students_data(class_start_time: str, class_end_time: str, class_start_grace_minutes: int = 5) -> Dict[str, Any]:
    return update_statuses(class_start_time, class_end_time, class_start_grace_minutes)


def logout_user(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Finalize attendance records during logout"""
    _ensure_db_dir()
    
    results = {
        "status": "success",
        "records_finalized": 0,
        "errors": []
    }
    
    try:
        attendance_rows = _read_attendance_csv()
        _write_attendance_csv(attendance_rows)
        results["records_finalized"] = len(attendance_rows)
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(f"Logout failed: {str(e)}")
        print(f"Error in logout_user: {e}")
    
    return results


def get_all_attendance() -> List[Dict[str, Any]]:
    """Get all attendance records"""
    try:
        rows = _read_attendance_csv()
        return [{
            "ID": r.get("ID", ""),
            "Name": r.get("Name", ""),
            "Status": r.get("Status", ""),
            "ClassesAttended": r.get("ClassesAttended", "0"),
            "TimeIn": r.get("TimeIn", ""),
            "TimeOut": r.get("TimeOut", ""),
            "Img_Path": r.get("Img_Path", ""),
        } for r in rows]
    except Exception as e:
        print(f"Error in get_all_attendance: {e}")
        return []


def get_student_attendance(name: str) -> Optional[Dict[str, Any]]:
    """Get attendance record for a specific student"""
    try:
        name = (name or "").strip()
        for r in get_all_attendance():
            if r.get("Name", "").strip().lower() == name.lower():
                return r
    except Exception as e:
        print(f"Error in get_student_attendance: {e}")
    return None


def get_attendance_summary() -> List[Dict[str, Any]]:
    """Compatibility helper"""
    return get_all_attendance()

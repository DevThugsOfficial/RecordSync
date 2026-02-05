from typing import List, Dict, Any, Optional
import flet as ft
from core.attendance_manager import sync_students_data, logout_user, get_all_attendance, write_settings
from core.student_manager import get_all_students, add_student as _add_student_real, update_student as _update_student_real, delete_student as _delete_student_real


class DashboardController:
    def __init__(self, page: ft.Page):
        self.page = page
        self._classes_per_quarter = 20
        self._class_time = "08:00 AM"
        self._class_duration_minutes = 45

        # Load persisted settings
        sess = getattr(page, "session", None)
        if sess is not None:
            try:
                v = sess.get("classes_per_quarter")
                if v is not None:
                    self._classes_per_quarter = int(v)
            except Exception:
                pass
            try:
                ct = sess.get("class_time")
                if ct is not None:
                    self._class_time = str(ct)
            except Exception:
                pass
            try:
                cd = sess.get("class_duration_minutes")
                if cd is not None:
                    self._class_duration_minutes = int(cd)
            except Exception:
                pass

    # Attendance: returns rows with time_in and time_out
    def get_attendance_data(self) -> List[Dict[str, Any]]:
        try:
            data = get_all_attendance()
            return data
        except Exception as e:
            print(f"Error loading attendance data: {e}")
            return []

    # Students CRUD using core
    def get_students(self) -> List[Dict[str, Any]]:
        try:
            students = get_all_students()
            enriched = []
            for s in students:
                attended = s.get("attended", 0)
                total = s.get("classes_total", self._classes_per_quarter)
                enriched.append({**s, "attended": attended, "classes_total": total})
            return enriched
        except Exception as e:
            print(f"Error loading students: {e}")
            return []

    def add_student(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return _add_student_real(payload)
        except Exception as e:
            print(f"Error adding student: {e}")
            return {}

    def update_student(self, student_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return _update_student_real(student_id, payload)
        except Exception as e:
            print(f"Error updating student: {e}")
            return {}

    def delete_student(self, student_id: str) -> None:
        try:
            _delete_student_real(student_id)
        except Exception as e:
            print(f"Error deleting student: {e}")

    # Settings
    def get_class_settings(self) -> int:
        return int(self._classes_per_quarter)

    def update_class_settings(self, v: int) -> None:
        self._classes_per_quarter = int(v)
        sess = getattr(self.page, "session", None)
        if sess is not None:
            try:
                sess["classes_per_quarter"] = v
            except Exception:
                pass
        # persist to disk so core functions can read the current class time if needed
        try:
            write_settings({
                "classes_per_quarter": int(self._classes_per_quarter),
                "class_start_time": str(self._class_time),
                "class_duration_minutes": int(self._class_duration_minutes),
            })
        except Exception:
            pass

    # Class time
    def get_class_time(self) -> str:
        return str(self._class_time)

    def set_class_time(self, t: str) -> None:
        self._class_time = str(t)
        sess = getattr(self.page, "session", None)
        if sess is not None:
            try:
                sess["class_time"] = t
            except Exception:
                pass
        try:
            write_settings({
                "classes_per_quarter": int(self._classes_per_quarter),
                "class_start_time": str(self._class_time),
                "class_duration_minutes": int(self._class_duration_minutes),
            })
        except Exception:
            pass

    # Class duration (minutes)
    def get_class_duration_minutes(self) -> int:
        return int(self._class_duration_minutes)

    def set_class_duration_minutes(self, minutes: int) -> None:
        try:
            self._class_duration_minutes = int(minutes)
        except Exception:
            self._class_duration_minutes = 0
        sess = getattr(self.page, "session", None)
        if sess is not None:
            try:
                sess["class_duration_minutes"] = int(self._class_duration_minutes)
            except Exception:
                pass
        try:
            write_settings({
                "classes_per_quarter": int(self._classes_per_quarter),
                "class_start_time": str(self._class_time),
                "class_duration_minutes": int(self._class_duration_minutes),
            })
        except Exception:
            pass

    # Quarter stats
    def get_quarter_stats(self) -> Dict[str, Any]:
        students = self.get_students()
        num_students = len(students)
        total_present = sum(s.get("attended", 0) for s in students)
        total_possible = sum(s.get("classes_total", self._classes_per_quarter) for s in students)
        total_absent = total_possible - total_present
        
        weeks = []
        for w in range(4):
            p = max(0, int(total_present * (0.25 + (0.05 * (w - 1)))))
            a = max(0, int((total_possible - total_present) * (0.25 + (0.03 * (3 - w)))))
            weeks.append({"label": f"W{w+1}", "present": p, "absent": a})
        
        return {
            "number_of_students": num_students,
            "total_present": total_present,
            "total_absent": total_absent,
            "weeks": weeks,
            "class_duration_minutes": int(self._class_duration_minutes),
        }

    # Logout
    def logout(self) -> Dict[str, Any]:
        class_start = self.get_class_time()
        class_end = "03:00 PM"

        results = {"sync": None, "logout": None}
        try:
            results["sync"] = sync_students_data(class_start, class_end)
        except Exception as e:
            results["sync"] = {"error": str(e)}
            print(f"Warning: sync_students_data failed: {e}")

        try:
            results["logout"] = logout_user()
        except Exception as e:
            results["logout"] = {"status": "error", "errors": [str(e)], "redirect": None}
            print(f"Warning: logout_user failed: {e}")

        # Clear session (existing behaviour)
        sess = getattr(self.page, "session", None)
        if sess is not None:
            try:
                for k in list(sess.keys() if hasattr(sess, "keys") else []):
                    try:
                        del sess[k]
                    except Exception:
                        try:
                            sess.pop(k, None)
                        except Exception:
                            pass
            except Exception:
                pass

        return results
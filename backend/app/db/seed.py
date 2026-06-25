"""Dev seed — demo departments (LongDuem) + a default owner_manager.

Run from backend/:  python -m app.db.seed
Idempotent. For local/dev only — change the default password immediately.
"""
from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.modules.departments.models import Department
from app.modules.users.models import User, UserDepartment
from app.shared.enums import Role

DEMO_DEPARTMENTS = [
    ("finance", "Finance"),
    ("marketing", "Marketing"),
    ("field", "Field / Production"),
    ("admin", "Admin"),
]
OWNER_EMAIL = "owner@longduem.local"
OWNER_PASSWORD = "changeme123"  # noqa: S105 — dev seed default, change after first login


def run() -> None:
    db = SessionLocal()
    try:
        existing_keys = set(db.scalars(select(Department.key)))
        for key, name in DEMO_DEPARTMENTS:
            if key not in existing_keys:
                db.add(Department(key=key, name=name))
        db.flush()

        owner = db.scalar(select(User).where(User.email == OWNER_EMAIL))
        if owner is None:
            owner = User(
                email=OWNER_EMAIL,
                password_hash=hash_password(OWNER_PASSWORD),
                full_name="LongDuem Owner",
                role=Role.owner_manager,
            )
            db.add(owner)
            db.flush()
            admin_dept = db.scalar(select(Department).where(Department.key == "admin"))
            if admin_dept is not None:
                db.add(
                    UserDepartment(
                        user_id=owner.id,
                        department_id=admin_dept.id,
                        role_in_department=Role.owner_manager,
                        is_active_default=True,
                    )
                )
        db.commit()
        print(f"Seed complete. Owner login: {OWNER_EMAIL} / {OWNER_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    run()

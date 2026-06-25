"""Data access for departments."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.departments.models import Department


class DepartmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, department_id: uuid.UUID) -> Department | None:
        return self.db.get(Department, department_id)

    def get_by_key(self, key: str) -> Department | None:
        return self.db.scalar(select(Department).where(Department.key == key))

    def list(self) -> list[Department]:
        return list(self.db.scalars(select(Department).order_by(Department.key)))

    def add(self, department: Department) -> Department:
        self.db.add(department)
        self.db.flush()
        return department

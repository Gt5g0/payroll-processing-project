# Store employees in a JSON file and reconstruct the correct subclass when loading.
# This is a singleton class – only one instance may exist.
# For a real product I would use a NoSQL database; JSON is okay for this project.

# Provides full CRUD (Create, Read, Update, Delete)
# like INSERT, SELECT, UPDATE, DELETE in SQL.

import json
import os
from typing import List, Optional
from employee import Employee, HourlyEmployee, SalariedEmployee, CommissionEmployee

class PayrollDatabase:

    _instance = None
    _employees: List[Employee] = []

    # __new__ controls creation. The first call creates the instance
    # and loads data from file. Every subsequent call returns the same object.
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        """Load employees from employee_db.json (or start fresh)."""
        if not os.path.exists('employee_db.json'):
            self._save()
            return
        try:
            with open('employee_db.json', 'r') as f:
                raw = json.load(f)
            self._employees = [self._MakeEmployee(item) for item in raw]
        except (json.JSONDecodeError, KeyError):
            print("Warning: corrupt data. Creating a new database.")
            self._employees = []
            self._save()

    def _save(self):
        """Write the current employee list to employee_db.json."""
        with open('employee_db.json', 'w') as f:
            json.dump([emp.to_dict() for emp in self._employees], f, indent=2)

    # Map the simple emp_type codes (stored under "emp_type" in JSON)
    # to the correct Python class.
    _class_map = {
        "hourly": HourlyEmployee,
        "salaried": SalariedEmployee,
        "commission": CommissionEmployee
    }

    def _MakeEmployee(self, data: dict) -> Employee:
        """Build an Employee object from a dictionary (read from JSON)."""
        data = data.copy()
        emp_type_code = data.pop("emp_type")
        try:
            employee_class = self._class_map[emp_type_code]
        except KeyError:
            raise ValueError(f"Unknown employee type: {emp_type_code}")
        return employee_class(**data)


    # CRUD operations

    def add(self, employee: Employee) -> None:
        """Add a new employee. Raises ValueError if ID already exists."""
        if self.find_by_id(employee.emp_id) is not None:
            raise ValueError(f"An employee with ID {employee.emp_id} already exists")
        self._employees.append(employee)
        self._save()

    def find_by_id(self, emp_id: str) -> Optional[Employee]:
        """Return the employee with the given ID, or None if not found."""
        for employee in self._employees:
            if employee.emp_id == emp_id:
                return employee
        return None

    def find_by_name(self, name: str) -> Optional[Employee]:
        """Return the employee with exactly matching name, or None."""
        for employee in self._employees:
            if employee.name == name:
                return employee
        return None

    def find_by_department(self, department: str) -> List[Employee]:
        """Return all employees in a department."""
        department = department.strip().lower()
        return [e for e in self._employees if e.dept.strip().lower() == department]

    def delete(self, emp_id: str) -> None:
        """Remove an employee by ID. Raises ValueError if not found."""
        emp = self.find_by_id(emp_id)
        if emp is None:
            raise ValueError(f"Employee {emp_id} not found")
        self._employees.remove(emp)
        self._save()

    def update(self, emp_id: str, updates: dict) -> Employee:
        """Update one or more fields of an employee.

        Uses setattr() so that the property setters (and their
        validation rules) are triggered automatically.
        """
        emp = self.find_by_id(emp_id)
        if emp is None:
            raise ValueError(f"Employee {emp_id} not found")
        for key, value in updates.items():
            setattr(emp, key, value)
        self._save()
        return emp
    
    def list_all(self) -> List[Employee]:
        """Return a list of all employees."""
        return list(self._employees)

    def count(self) -> int:
        """Return the total number of employees."""
        return len(self._employees)
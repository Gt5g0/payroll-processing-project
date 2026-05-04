# Contains an abstract base class which is easily extended to add more types of employees.
# Currently, I have hourly employees, salaried employees, and commission employees.
# For both salaried and commission employees, FLSA exemption status and overtime pay
# are handled automatically. For hourly employees, full-time and part-time status are noted.

from abc import ABC, abstractmethod
from typing import Any

class Employee(ABC):
    """Abstract base class - do not instantiate directly."""

    # The base constructor does NOT take the type code.
    # Instead, each subclass MUST set self._type to its code
    # ("hourly", "salaried", "commission") inside its own __init__.
    def __init__(self, emp_id: str, name: str, dept: str, hire_date: str, hours_worked: float = 0.0):
        self._type = ""                # placeholder – to be overridden by subclasses
        self._emp_id = emp_id
        self._name = name
        self._dept = dept
        self._hire_date = hire_date
        self._hours_worked = hours_worked

    # read‑only properties
    @property
    def emp_id(self):
        return self._emp_id

    @property
    def hire_date(self):
        return self._hire_date

    # mutable properties
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name: str):
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Name cannot be empty")
        self._name = new_name

    @property
    def dept(self):
        return self._dept

    @dept.setter
    def dept(self, new_dept: str):
        new_dept = new_dept.strip()
        if not new_dept:
            raise ValueError("Department cannot be empty")
        self._dept = new_dept

    @property
    def hours_worked(self):
        return self._hours_worked

    @hours_worked.setter
    def hours_worked(self, value: float):
        if value < 0:
            raise ValueError("Hours worked must not be negative")
        self._hours_worked = value

    # abstract methods / properties
    @abstractmethod
    def calculate_pay(self) -> float:
        pass

    @abstractmethod
    def employee_description(self) -> str:
        """Return a human-readable description (e.g. 'Full-Time Hourly Employee')."""
        pass

    # Property that returns the simple type code stored in self._type.
    @property
    def emp_type(self) -> str:
        """Simple classification code: 'hourly', 'salaried', or 'commission'."""
        return self._type

    # Serialisation
    # Important function for converting an Employee object into a
    # storable format. In this project I used a JSON object.
    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary suitable for JSON storage.
        Keys match the constructor parameters of subclasses exactly."""
        return {
            "emp_type": self.emp_type,
            "emp_id": self._emp_id,
            "name": self._name,
            "dept": self._dept,
            "hire_date": self._hire_date,
            "hours_worked": self._hours_worked,
        }

    def __str__(self) -> str:
        return f"[{self.emp_id}] {self.name} ({self.employee_description()})"

# Concrete employee types

class HourlyEmployee(Employee):
    def __init__(self, emp_id, name, dept, hours_worked, hire_date,
                 pay_rate: float = 0.0, is_full_time: bool = True):
        super().__init__(emp_id, name, dept, hire_date, hours_worked)
        self._type = "hourly"          # set the type code
        self._pay_rate = pay_rate
        self._is_full_time = is_full_time

    @property
    def pay_rate(self):
        return self._pay_rate

    @pay_rate.setter
    def pay_rate(self, rate):
        if rate < 0:
            raise ValueError("Pay rate must not be negative")
        self._pay_rate = rate

    @property
    def is_full_time(self):
        return self._is_full_time

    @is_full_time.setter
    def is_full_time(self, value: bool):
        self._is_full_time = value

    def employee_description(self) -> str:
        return "Full-Time Hourly Employee" if self._is_full_time else "Part-Time Hourly Employee"

    def calculate_pay(self) -> float:
        # Overtime after 40 hours in a week (1.5x)
        ot_hours = max(0, self._hours_worked - 40)
        base_pay = (self._hours_worked - ot_hours) * self._pay_rate
        ot_pay = ot_hours * self._pay_rate * 1.5
        return base_pay + ot_pay

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data.update({
            "pay_rate": self._pay_rate,
            "is_full_time": self._is_full_time,
        })
        return data


class SalariedEmployee(Employee):
    def __init__(self, emp_id, name, dept, hire_date, annual_salary,
                 flsa_exempt: bool, hours_worked=0.0):
        super().__init__(emp_id, name, dept, hire_date, hours_worked)
        self._type = "salaried"        # set the type code
        self._salary = annual_salary
        self._flsa_exempt = flsa_exempt
        self._validate_flsa_exempt()

    def _validate_flsa_exempt(self):
        """Enforce FLSA minimum weekly salary of $684."""
        if self._flsa_exempt and (self._salary / 52 < 684):
            raise ValueError(
                f"FLSA-exempt employees must earn at least $684 per week. "
                f"Current salary gives ${self._salary / 52:.2f} per week."
            )

    @property
    def salary(self):
        return self._salary

    @salary.setter
    def salary(self, salary_input: float):
        if not salary_input:
            raise ValueError("Salary cannot be empty")
        if salary_input < 0:
            raise ValueError("Salary must be > 0")
        self._salary = salary_input
        if self._flsa_exempt:
            self._validate_flsa_exempt()

    @property
    def flsa_exempt(self):
        return self._flsa_exempt

    @flsa_exempt.setter
    def flsa_exempt(self, status: bool):
        if status:
            self._validate_flsa_exempt()
        self._flsa_exempt = status

    def employee_description(self) -> str:
        if self._flsa_exempt:
            return "Full-Time Salaried Employee, FLSA Exempt"
        return "Full-Time Salaried Employee, FLSA Non-Exempt"

    def calculate_pay(self) -> float:
        """Weekly base = annual/52; overtime for non-exempt > 40 hrs."""
        base_pay = self._salary / 52
        if not self._flsa_exempt and self._hours_worked > 40:
            ot_hours = self._hours_worked - 40
            hourly_rate = self._salary / 2080   # 40 hrs/wk * 52 wks
            ot_pay = ot_hours * hourly_rate * 1.5
            return base_pay + ot_pay
        return base_pay

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data.update({
            "annual_salary": self._salary,
            "flsa_exempt": self._flsa_exempt,
        })
        return data


class CommissionEmployee(SalariedEmployee):
    def __init__(self, emp_id, name, dept, hire_date, annual_salary,
                 flsa_exempt: bool, hours_worked=0.0,
                 commission_rate: float = 0.0, sales: float = 0.0):
        super().__init__(emp_id, name, dept, hire_date, annual_salary,
                         flsa_exempt, hours_worked)
        self._type = "commission"      # override "salaried"
        if commission_rate < 0:
            raise ValueError("Commission rate must not be negative.")
        self._commission_rate = commission_rate
        self._sales = sales

    @property
    def commission_rate(self):
        return self._commission_rate

    @property
    def sales(self):
        return self._sales

    @sales.setter
    def sales(self, amount: float):
        if not amount:
            raise ValueError("Sales value must not be empty")
        if amount < 0:
            raise ValueError("Sales value must not be negative")
        self._sales = amount

    def employee_description(self) -> str:
        if self._flsa_exempt:
            return "Full-Time Salaried Employee with Commission Pay, FLSA Exempt"
        return "Full-Time Salaried Employee with Commission Pay, FLSA Non-Exempt"

    def calculate_pay(self) -> float:
        base_pay = super().calculate_pay()
        commission_pay = self._commission_rate * self.sales
        return base_pay + commission_pay

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data.update({
            "commission_rate": self._commission_rate,
            "sales": self._sales,
        })
        return data
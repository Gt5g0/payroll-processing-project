# Uses a popular library called pydantic to check user input before creating or updating employees.
# Keeps bad data out of the system, but someone could still edit the JSON file by hand or with another application.

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date

# Allowed department names
allowed_departments = [
    "engineering",
    "sales",
    "marketing",
    "hr",
    "finance",
    "it",
    "legal",
]


class EmployeeCreate(BaseModel):
    """Validates employee creation data automatically using pydantic."""

    # Define a class with fields and their types, and pydantic
    # automatically raises errors if the data doesn't match.
    # Uses regex (regular expressions) to validate the data matches a specific pattern.

    # "EMP-"" followed by 3 or 4 digits
    emp_id: str = Field(..., pattern=r"^EMP-\d{3,4}$")

    # Between 2 and 200 characters
    name: str = Field(..., min_length=2, max_length=200)

    # Must not be empty
    # Script checks if it's in the allowed_departments list later
    department: str = Field(..., min_length=1)

    # Must look like YYYY-MM-DD
    hire_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")

    # Default 0.0, cannot be negative
    hours_worked: Optional[float] = Field(0.0, ge=0)

    # type-specific fields
    pay_rate: Optional[float] = Field(None, ge=0)
    annual_salary: Optional[float] = Field(None, ge=0)
    flsa_exempt: Optional[bool] = False
    commission_rate: Optional[float] = Field(None, ge=0, le=1.0)
    sales: Optional[float] = Field(0.0, ge=0)

    # custom validators
    # @field_validator marks a method that runs after the basic checks.

    @field_validator("hire_date")
    @classmethod
    def check_hire_date_not_future(cls, v: str) -> str:
        """Make sure the date is valid and not in the future."""
        try:
            d = date.fromisoformat(v)
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")
        if d > date.today():
            raise ValueError("Hire date cannot be in the future.")
        return v

    @field_validator("department")
    @classmethod
    def department_must_be_allowed(cls, v: str) -> str:
        """Only accept departments from the approved list."""
        if v.lower() not in allowed_departments:
            raise ValueError(
                f"'{v}' is not a recognised department. "
                f"Allowed: {', '.join(allowed_departments)}"
            )
        return v

    @field_validator("pay_rate")
    @classmethod
    def pay_rate_required_if_hourly(cls, v, info):
        """Pay rate is mandatory for hourly employees."""
        if info.data.get("employee_type") == "hourly" and v is None:
            raise ValueError("Hourly employees must have a pay rate.")
        return v

    @field_validator("annual_salary")
    @classmethod
    def annual_salary_required_if_salaried_or_commission(cls, v, info):
        """Annual salary is mandatory for salaried and commission employees."""
        emp_type = info.data.get("employee_type")
        if emp_type in ("salaried", "commission") and v is None:
            raise ValueError("Salaried and commission employees must have an annual salary.")
        return v

    @field_validator("commission_rate")
    @classmethod
    def commission_rate_required_if_commission(cls, v, info):
        """Commission rate is mandatory for commission employees."""
        if info.data.get("employee_type") == "commission" and v is None:
            raise ValueError("Commission employees must have a commission rate.")
        return v
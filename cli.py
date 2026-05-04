# A CLI is a text-based interface where the user types commands to navigate menus and provide input
# This file presents a simple loop that prints a menu, reads the user's choice, and calls the corresponding function.

from database import PayrollDatabase
from taxes import PayrollCalculator
from payslip import ConsolePayslipGenerator
from validation import EmployeeCreate
from pydantic import ValidationError
from employee import HourlyEmployee, SalariedEmployee, CommissionEmployee
from typing import Any


def main():
    # Create the core objects – database, tax calculator, payslip formatter.
    db = PayrollDatabase()
    calc = PayrollCalculator()
    payslip_gen = ConsolePayslipGenerator(calc)

    while True:
        # Print the menu every iteration
        print("\n" + "=" * 45)
        print("  PAYROLL PROCESSING ENGINE  ")
        print("=" * 45)
        print("1. Add Employee")
        print("2. List All Employees")
        print("3. Run Payroll (Single Employee)")
        print("4. Run Payroll (All Employees)")
        print("5. Run Payroll by Department")
        print("6. Update Employee")
        print("7. Delete Employee")
        print("8. Exit")
        print("-" * 45)

        choice = input("Choose an option: ").strip()

        # Map the choice to the right function
        if choice == "1":
            add_employee(db)
        elif choice == "2":
            list_employees(db)
        elif choice == "3":
            run_single_payroll(db, payslip_gen)
        elif choice == "4":
            run_all_payroll(db, payslip_gen)
        elif choice == "5":
            run_department_payroll(db, payslip_gen)
        elif choice == "6":
            update_employee(db)
        elif choice == "7":
            delete_employee(db)
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

#  Add Employee

def add_employee(db):
    """Collect user input, validate it, and store a new employee."""

    print("\n--- Add New Employee ---")
    emp_type = input("Type (hourly / salaried / commission): ").strip().lower()

    # Uses a dictionary to collect raw input before validation.
    data: dict[str, Any] = {}

    data["emp_id"] = input("Employee ID (e.g., EMP-001): ").strip()
    data["name"] = input("Full Name: ").strip()
    data["department"] = input("Department: ").strip()
    data["hire_date"] = input("Hire Date (YYYY-MM-DD): ").strip()
    data["employee_type"] = emp_type

    # Ask for extra fields based on employee type
    if emp_type == "hourly":
        try:
            data["hours_worked"] = float(input("Hours worked this week: ").strip() or 0)
            data["pay_rate"] = float(input("Hourly rate: ").strip())
        except ValueError:
            print("Error: Hours worked and hourly rate must be numbers.")
            return
    elif emp_type == "salaried":
        try:
            data["annual_salary"] = float(input("Annual salary: ").strip())
            flsa = input("FLSA exempt? (y/n): ").strip().lower()
            data["flsa_exempt"] = flsa == "y" or flsa == "yes"
        except ValueError:
            print("Error: Salary must be a number.")
            return
    elif emp_type == "commission":
        try:
            data["annual_salary"] = float(input("Annual base salary: ").strip())
            data["commission_rate"] = float(input("Commission rate (0-1): ").strip())
            flsa = input("FLSA exempt? (y/n): ").strip().lower()
            data["flsa_exempt"] = flsa == "y" or flsa == "yes"
        except ValueError:
            print("Error: Salary, commission rate, and FLSA status must be valid.")
            return
    else:
        print("Unknown employee type.")
        return

    # Validate the gathered data using pydantic
    try:
        validated = EmployeeCreate(**data)
    except ValidationError as e:
        print("Validation error(s):")
        print(e)
        return

    # Build the correct Employee subclass from the validated data
    if emp_type == "hourly":
        # HourlyEmployee expects: emp_id, name, dept, hours_worked, hire_date, pay_rate
        emp = HourlyEmployee(
            validated.emp_id,
            validated.name,
            validated.department,
            validated.hours_worked or 0.0,
            validated.hire_date,
            validated.pay_rate or 0.0,
        )
    elif emp_type == "salaried":
        emp = SalariedEmployee(
            validated.emp_id,
            validated.name,
            validated.department,
            validated.hire_date,
            validated.annual_salary or 0.0,
            validated.flsa_exempt or False,
            validated.hours_worked or 0.0,
        )
    elif emp_type == "commission":
        emp = CommissionEmployee(
            validated.emp_id,
            validated.name,
            validated.department,
            validated.hire_date,
            validated.annual_salary or 0.0,
            validated.flsa_exempt or False,
            validated.hours_worked or 0.0,
            validated.commission_rate or 0.0,
            validated.sales or 0.0,
        )
    else:
        return

    # Save to database
    try:
        db.add(emp)
        print(f"Added {emp}")
    except ValueError as e:
        print(f"Error: {e}")


#  List All Employees

def list_employees(db):
    """Print a simple list of all employees currently in the database."""
    employees = db.list_all()
    if not employees:
        print("No employees found.")
        return
    print(f"\n--- All Employees ({len(employees)}) ---")
    for emp in employees:
        print(f"  {emp}")


#  Run Payroll (Single Employee)

def run_single_payroll(db, payslip_gen):
    """Show a detailed payslip for one employee by their ID."""
    emp_id = input("Employee ID: ").strip()
    emp = db.find_by_id(emp_id)
    if emp is None:
        print("Employee not found.")
        return
    print(payslip_gen.generate(emp))


#  Run Payroll (All Employees)

def run_all_payroll(db, payslip_gen):
    """Payslip summary lines for every employee, plus total gross and net."""
    employees = db.list_all()
    if not employees:
        print("No employees.")
        return
    total_gross = 0.0
    total_net = 0.0
    for emp in employees:
        data = payslip_gen.calculator.calculate_net_pay(emp)
        total_gross += data["gross_pay"]
        total_net += data["net_pay"]
        print(f"  {emp.name}: Gross = ${data['gross_pay']:,.2f}  ->  Net = ${data['net_pay']:,.2f}")
    print(f"\n--- Totals ---")
    print(f"  Total gross: ${total_gross:,.2f}")
    print(f"  Total net:   ${total_net:,.2f}")


#  Run Payroll by Department

def run_department_payroll(db, payslip_gen):
    """Full payslips for every employee in a chosen department."""
    dept = input("Department: ").strip()
    employees = db.find_by_department(dept)
    if not employees:
        print(f"No employees in '{dept}'.")
        return
    for emp in employees:
        print(payslip_gen.generate(emp))
        print()


#  Update Employee

def update_employee(db):
    """Change hours worked (all types) or sales amount (commission only)."""
    emp_id = input("Employee ID to update: ").strip()
    emp = db.find_by_id(emp_id)
    if not emp:
        print("Employee not found.")
        return

    print(f"Updating {emp.name} ({emp.employee_description()})")
    if isinstance(emp, HourlyEmployee):
        try:
            new_hours = input(f"Hours worked (currently {emp.hours_worked}): ").strip()
            if new_hours:
                db.update(emp_id, {"hours_worked": float(new_hours)})
                print("Hours updated.")
            else:
                print("No change.")
        except ValueError as e:
            print(f"Error: {e}")
    elif isinstance(emp, CommissionEmployee):
        try:
            new_sales = input(f"Sales amount (currently {emp.sales}): ").strip()
            if new_sales:
                db.update(emp_id, {"sales": float(new_sales)})
                print("Sales updated.")
            else:
                print("No change.")
        except ValueError as e:
            print(f"Error: {e}")
    else:
        # Salaried non‑commission: only hours_worked is mutable
        try:
            new_hours = input(f"Hours worked (currently {emp.hours_worked}): ").strip()
            if new_hours:
                db.update(emp_id, {"hours_worked": float(new_hours)})
                print("Hours updated.")
            else:
                print("No change.")
        except ValueError as e:
            print(f"Error: {e}")


#  Delete Employee

def delete_employee(db):
    """Remove an employee after confirmation."""
    emp_id = input("Employee ID to delete: ").strip()
    emp = db.find_by_id(emp_id)
    if not emp:
        print("Employee not found.")
        return
    confirm = input(f"Delete {emp.name} ({emp_id})? (y/n): ").strip().lower()
    if confirm == "y":
        db.delete(emp_id)
        print("Employee deleted.")
    else:
        print("Deletion cancelled.")


if __name__ == "__main__":
    main()
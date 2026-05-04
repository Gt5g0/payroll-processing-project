PAYROLL PROCESSING APPLICATION PROJECT
Joshua Shapiro

SUMMARY
---------------------------------------------------------------------------------------------------
I built this payroll command line application for my Object Oriented Programming final project.
It provides navigable menus and guided prompts to add, delete, update hours and sales, and generate
payslips for employees. It demonstrates OOP concepts: inheritance, polymorphism, and encapsulation.
A Singleton pattern ensures the database has only a single instance, keeping employee data
consistent. The Pydantic library validates human input, checking hire dates match the YYYY-MM-DD
format and are not in the future. I researched actual 2026 federal and New Jersey marginal tax
rates, Social Security, and Medicare withholdings for realistic calculations. This is a demo, It's
limited to single-week payroll for simplicity. It is not for production use. One way I could expand
on this project is to include the No Tax on Overtime deduction for eligible employees.

Main pieces:

  employee.py        Define an Employee abstract base class and three concrete
                     classes (hourly, salaried, commission) and encapsulates
                     pay calculation and serialisation (to_dict function).

  database.py        Singleton PayrollDatabase: save employee objects to
                     a JSON file, reconstructs them at runtime, and
                     provides CRUD operations (Create, Read, Update, Delete).

  taxes.py           Tax calculation engine which uses real, up-to-date (for 2026)
                     information for social security and medicare withholdings, and
                     both federal and New Jersey state income tax.

  payslip.py         Console payslip generator that creates a pretty
                     pay stub from the PayrollCalculator’s output for
                     printing to the terminal.

  validation.py      Pydantic model EmployeeCreate: enforces data integrity
                     with regex patterns, a department whitelist, and
                     cross‑field conditional rules

  cli.py             Command‑line interface that orchestrates
                     employee management, payroll processing, and payslip
                     display with navigable menus and error handling.

  employee_db.json   Human‑readable JSON file which is updated whenever an employee
                     is added, removed, or updated. I use it as a database for this
                     project, but a real product would use something else such as NoSQL.


REQUIREMENTS
---------------------------------------------------------------------------------------------------

  - Python 3.10 or newer is recommended


INSTALLATION
---------------------------------------------------------------------------------------------------

1. Download payroll_processing_project.zip and extract it using a program like 7zip

2. Open a terminal and change to the project directory (the folder you just extracted)

     cd payroll_processing_project

3. Install dependencies:

     pip install -r requirements.txt

   This installs the third-party library listed in requirements.txt (pydantic)

4. Run the command line interface to use the program

    python cli.py


USAGE
---------------------------------------------------------------------------------------------------

Always run commands from the project directory (or ensure employee_db.json is
present in your current working directory). Otherwise the database may start
empty or read/write a different file than you expect.

Command Line Interface
~~~~~~~~~~~~~~~~~

You will see a menu similar to:

  1. Add Employee                   - guided prompts; input is validated with Pydantic
  2. List All Employees             - prints every employee
  3. Run Payroll (Single)           - asks for an ID, prints one payslip
  4. Run Payroll (All)              - gross/net summary for everyone
  5. Run Payroll by Department      - payslips for each employee in a department
  6. Update Employee                - update hours or commission sales
  7. Delete Employee                - remove by entering employee ID, asks you to confirm
  8. Exit

Choose a number and press Enter. Follow the exact format for dates (YYYY-MM-DD),
employee types (hourly / salaried / commission), and departments (from the
allowed list enforced in validation.py)

LIBRARIES AND PACKAGES
---------------------------------------------------------------------------------------------------

Third-party (installed via pip install -r requirements.txt)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Pydantic : a popular library for data validation
    - Used in validation.py for EmployeeCreate: typed fields, regex patterns,
      and custom validators (hire date not in the future, department whitelist,
      conditional required fields by employee type).
    - cli.py imports ValidationError from pydantic to report validation failures
      when adding an employee.

Standard library (bundled with Python)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The project also relies on Python's standard library, including:

  json, os          database.py - read/write employee_db.json; path checks
  abc               employee.py, taxes.py - abstract base classes
  typing            several modules - type hints (List, Optional, Any, etc.)
  datetime          validation.py - confirm that hire dates are in the correct format and before the current date
from abc import ABC, abstractmethod
from employee import Employee

class PayrollCalculator:
    """Used by the payslip generator. Instantiate this class and then call the calculate_net_pay function and provide an employee"""
    def calculate_net_pay(self, employee: Employee):
        gross = employee.calculate_pay()
        soc = SocialSecurity().compute(employee)
        med = Medicare().compute(employee)
        fed = IncomeTax("federal").compute(employee)
        state = IncomeTax("state").compute(employee)
        total_deductions = soc + med + fed + state
        net = round(gross - total_deductions, 2)

        return {
            "employee_name" : employee.name,
            "employee_id" : employee.emp_id,
            "employee_description" : employee.employee_description(),
            "department" : employee.dept,
            "gross_pay" : gross,
            "social_security" : soc,
            "medicare" : med,
            "federal_income_tax" : fed,
            "state_income_tax" : state,
            "total_deductions" : total_deductions,
            "net_pay" : net,
        }

class TaxCalculator(ABC):
    """This is an abstract base class to simplify adding or removing different tax calculators"""
    @abstractmethod
    def compute(self, employee: Employee) -> float:
        return employee.calculate_pay()

class SocialSecurity(TaxCalculator):
    """Compute the social security tax: 6.2% with a maximum witholding of $184,500"""
    def compute(self, employee: Employee) -> float:
        gross = super().compute(employee)
        tax = min(184_500/52, gross) * 0.062
        return round(tax, 2) # only return values expressable in dollars and cents

class Medicare(TaxCalculator):
    """Compute the medicare tax: 1.45% with an additional 0.9% tax on income over $200,000"""
    def compute(self, employee: Employee) -> float:
        gross = super().compute(employee)
        base_tax = gross * 0.0145
        additional_tax = max(0, gross - 200_000/52) * 0.009
        return round(base_tax + additional_tax, 2)
    
class IncomeTax(TaxCalculator):
    """Computes either state or federal income tax if provided
    "state" or "federal" argument. Uses an algorithm to calculate the annual
    marginal income tax, and returns that amount divided by 52"""
    def __init__(self, level: str):
        if level == "federal": # 2026 federal income tax brackets
            self.tax_brackets = [
                (11_600, 0.10),
                (47_150, 0.12),
                (100_525, 0.22),
                (191_950, 0.24),
                (243_725, 0.32),
                (609_350, 0.35),
                (float("inf"), 0.37)
            ]
        elif level == "state": # 2026 new jersey state income tax brackets (single or married filing seperately)
            self.tax_brackets = [
                (20_000, 0.014),
                (35_000, 0.0175),
                (40_000, 0.035),
                (75_000, 0.05525),
                (500_000, 0.0637),
                (1_000_000, 0.0897),
                (float("inf"), 0.1075)
            ]
        else:
            raise ValueError("IncomeTax ONLY takes arguments 'state' or 'federal'")          

    def compute(self, employee: Employee) -> float:
        annual_gross = 52 * super().compute(employee)
        weekly_tax = self._compute_annual(annual_gross) / 52
        return round(weekly_tax, 2)

    def _compute_annual(self, income: float) -> float:
        """internal function to calculate annual marginal income tax"""
        tax = 0.0
        prev_limit = 0.0
        for limit, rate in self.tax_brackets:
            if income > prev_limit:
                taxable_in_bracket = min(income, limit) - prev_limit
                tax += taxable_in_bracket * rate
            prev_limit = limit
            if income <= limit:
                break
        return tax
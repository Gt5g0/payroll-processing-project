from employee import Employee
from taxes import PayrollCalculator

class ConsolePayslipGenerator:
    def __init__(self, calculator: PayrollCalculator):
        """
        'calculator' is a PayrollCalculator instance that provides
        the pay breakdown via calculate_net_pay().
        """
        self.calculator = calculator

    def generate(self, employee: Employee) -> str:
        """Return a formatted payslip for the given employee."""
        data = self.calculator.calculate_net_pay(employee)

        lines = [
            f"{'=' * 100}",
            f"  PAYSLIP",
            f"{'=' * 100}",
            f"  Employee:              {data['employee_name']}",
            f"  ID:                    {data['employee_id']}",
            f"  Department:            {data['department']}",
            f"  Classification:        {data['employee_description']}",
            f"{'=' * 100}",
            f"  Gross Pay:            ${data['gross_pay']:>10,.2f}",
            f"  Federal Income Tax:   ${data['federal_income_tax']:>10,.2f}",
            f"  Social Security:      ${data['social_security']:>10,.2f}",
            f"  Medicare:             ${data['medicare']:>10,.2f}",
            f"  State Income Tax:     ${data['state_income_tax']:>10,.2f}",
            f"  {'-' * 40}",
            f"  Total Deductions:     ${data['total_deductions']:>10,.2f}",
            f"{'=' * 100}",
            f"  Net Pay:              ${data['net_pay']:>10,.2f}",
            f"{'=' * 100}",
        ]
        return "\n".join(lines)
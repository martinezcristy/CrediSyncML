# models.py

class Evaluation:
    def __init__(self, dependents: bool, loan_amount: int, employment_status: str, asset_owner: bool,
                 monthly_salary: int, have_savings_account: bool, have_outstanding_debts: bool,
                 currently_employed: bool, years_current_residence: int, loan_term: int,
                 years_employed: int, credit_card_owner: bool, repayment_sched: str, loan_purpose: str):
        self._dependents = dependents
        self._loan_amount = loan_amount
        self._employment_status = employment_status
        self._asset_owner = asset_owner
        self._monthly_salary = monthly_salary
        self._have_savings_account = have_savings_account
        self._have_outstanding_debts = have_outstanding_debts
        self._currently_employed = currently_employed
        self._years_current_residence = years_current_residence
        self._loan_term = loan_term
        self._years_employed = years_employed
        self._credit_card_owner = credit_card_owner
        self._repayment_sched = repayment_sched
        self._loan_purpose = loan_purpose

    @property
    def dependents(self):
        return self._dependents

    @property
    def loan_amount(self):
        return self._loan_amount

    @property
    def employment_status(self):
        return self._employment_status

    @property
    def asset_owner(self):
        return self._asset_owner

    @property
    def monthly_salary(self):
        return self._monthly_salary

    @property
    def have_savings_account(self):
        return self._have_savings_account

    @property
    def have_outstanding_debts(self):
        return self._have_outstanding_debts

    @property
    def currently_employed(self):
        return self._currently_employed

    @property
    def years_current_residence(self):
        return self._years_current_residence

    @property
    def loan_term(self):
        return self._loan_term

    @property
    def years_employed(self):
        return self._years_employed

    @property
    def credit_card_owner(self):
        return self._credit_card_owner

    @property
    def repayment_sched(self):
        return self._repayment_sched

    @property
    def loan_purpose(self):
        return self._loan_purpose

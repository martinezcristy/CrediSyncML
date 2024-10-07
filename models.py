# models.py
class Member:
    def __init__(self, account_number: str, name: str, contact_number: str, email: str,
                 address: str, date_applied: str):
        self._account_number: str = account_number
        self._name: str = name
        self._contact_number: str = contact_number
        self._email: str = email
        self._address: str = address
        self._date_applied: str = date_applied

    @property
    def account_number(self) -> str:
        return self._account_number

    @property
    def name(self) -> str:
        return self._name

    @property
    def contact_number(self) -> str:
        return self._contact_number

    @property
    def email(self) -> str:
        return self._email

    @property
    def address(self) -> str:
        return self._address

    @property
    def date_applied(self) -> str:
        return self._date_applied

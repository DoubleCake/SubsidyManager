class Subsidy:
    def __init__(self, subsidy_id, family_id, amount, issue_date, status="待发放"):
        self.subsidy_id = subsidy_id
        self.family_id = family_id
        self.amount = amount
        self.issue_date = issue_date
        self.status = status

    def to_dict(self):
        return {
            "subsidy_id": self.subsidy_id,
            "family_id": self.family_id,
            "amount": self.amount,
            "issue_date": self.issue_date,
            "status": self.status
        }
class Family:
    def __init__(self, family_id, address, income, members_count):
        self.family_id = family_id
        self.address = address
        self.income = income
        self.members_count = members_count

    def to_dict(self):
        return {
            "family_id": self.family_id,
            "address": self.address,
            "income": self.income,
            "members_count": self.members_count
        }
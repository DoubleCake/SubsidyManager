class Person:
    def __init__(self, person_id, family_id, name, phone, has_social_card, is_head):
        self.person_id = person_id
        self.family_id = family_id
        self.name = name
        self.phone = phone
        self.has_social_card = has_social_card
        self.is_head = is_head

    def to_dict(self):
        return {
            "person_id": self.person_id,
            "family_id": self.family_id,
            "name": self.name,
            "phone": self.phone,
            "has_social_card": self.has_social_card,
            "is_head": self.is_head
        }
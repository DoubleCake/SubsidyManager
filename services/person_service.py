# services.py
from models import  PersonDAO
from datetime import date

class PersonService:
    def __init__(self):
        self.person_dao = PersonDAO()
    
    def add_person(self, person_id, family_id, name, **kwargs):
        return self.person_dao.add_person(person_id, family_id, name, **kwargs)
    
    def get_family_members(self, family_id):
        return self.person_dao.get_persons(family_id)
    
    def set_as_head(self, person_id):
        return self.person_dao.set_as_head(person_id)
    
    def update_person(self, person_id, **kwargs):
        # 在实际实现中需要构建动态SQL
        pass
    
    def delete_person(self, person_id):
        return self.person_dao.delete_person(person_id)

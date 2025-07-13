# service/family_service.py
from models import FamilyDAO


class FamilyService:
    def __init__(self, db_path='family_subsidies.db'):
        self.dao = FamilyDAO(db_path)

    def create_family(self, head_id: int, land_area: float):
        return self.dao.create_family(head_id, land_area )

    def get_family(self, family_id: int):
        return self.dao.get_family_by_id(family_id)
    
    def update_family(self, family_id: int, land_area: float):
        return self.dao.update_family(family_id, land_area)

    def delete_family(self, family_id: int):
        return self.dao.delete_family(family_id)

    def get_all_families(self):
        return self.dao.get_all_families()
    
    def get_all_families_paginated(self, page: int, page_size: int):
        offset = (page - 1) * page_size
        return self.dao.get_all_families_paginated(offset, page_size)

    def search_family(self, keyword: str):
        return self.dao.search_family(keyword)

    def get_total_count(self):
        return self.dao.get_total_count()
    

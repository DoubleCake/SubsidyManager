# services.py
from dao import FamilyDAO, PersonDAO, LandDAO, SubsidyTypeDAO, SubsidyRecordDAO, ConflictRuleDAO
from datetime import date

class FamilyService:
    def __init__(self):
        self.family_dao = FamilyDAO()
        self.person_dao = PersonDAO()
        self.land_dao = LandDAO()
        self.subsidy_record_dao = SubsidyRecordDAO()
    
    def create_family(self, family_id):
        return self.family_dao.add_family(family_id)
    
    def get_families(self):
        return self.family_dao.get_families()
    
    def get_family_report(self, family_id):
        # 获取家庭成员
        members = self.person_dao.get_persons(family_id)
        # 获取用地信息
        lands = self.land_dao.get_lands(family_id)
        # 获取补贴记录
        records = self.subsidy_record_dao.get_records(family_id)
        # 计算总金额
        total_amount = sum(record[6] for record in records) if records else 0
        return {
            "family_id": family_id,
            "members": members,
            "lands": lands,
            "subsidies": records,
            "total_amount": total_amount
        }
    
    def delete_family(self, family_id):
        # 删除相关记录
        self.subsidy_record_dao.execute(
            "DELETE FROM subsidy_record WHERE person_id IN (SELECT person_id FROM person WHERE family_id = ?)",
            (family_id,)
        )
        self.land_dao.execute(
            "DELETE FROM land WHERE family_id = ?",
            (family_id,)
        )
        self.person_dao.execute(
            "DELETE FROM person WHERE family_id = ?",
            (family_id,)
        )
        return self.family_dao.delete_family(family_id)

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

class LandService:
    def __init__(self):
        self.land_dao = LandDAO()
    
    def add_land(self, family_id, area, land_type, year):
        return self.land_dao.add_land(family_id, area, land_type, year)
    
    def get_family_lands(self, family_id, year=None):
        return self.land_dao.get_lands(family_id, year)
    
    def update_land(self, land_id, **kwargs):
        # 在实际实现中需要构建动态SQL
        pass
    
    def delete_land(self, land_id):
        return self.land_dao.delete_land(land_id)

class SubsidyService:
    def __init__(self):
        self.subsidy_type_dao = SubsidyTypeDAO()
        self.subsidy_record_dao = SubsidyRecordDAO()
        self.conflict_rule_dao = ConflictRuleDAO()
    
    def create_subsidy_type(self, subsidy_id, name, amount_per_unit, **kwargs):
        return self.subsidy_type_dao.add_subsidy_type(
            subsidy_id, name, amount_per_unit, **kwargs
        )
    
    def get_subsidy_types(self):
        return self.subsidy_type_dao.get_subsidy_types()
    
    def grant_subsidy(self, person_id, subsidy_id, applied_area, land_id, year, **kwargs):
        return self.subsidy_record_dao.add_subsidy_record(
            person_id, subsidy_id, applied_area, land_id, year, **kwargs
        )
    
    def get_family_subsidies(self, family_id, year=None):
        return self.subsidy_record_dao.get_records(family_id, year)
    
    def add_conflict_rule(self, subsidy_id, conflicting_subsidy_id, description=None):
        return self.conflict_rule_dao.add_conflict_rule(
            subsidy_id, conflicting_subsidy_id, description
        )
    
    def get_conflict_rules(self, subsidy_id=None):
        return self.conflict_rule_dao.get_rules(subsidy_id)

class ReportService:
    def __init__(self):
        self.family_service = FamilyService()
        self.subsidy_service = SubsidyService()
    
    def generate_family_report(self, family_id, year):
        # 获取家庭成员
        members = PersonDAO().get_persons(family_id)
        
        # 获取补贴记录
        records = self.subsidy_service.get_family_subsidies(family_id, year)
        
        # 计算总金额
        total_amount = sum(record[6] for record in records) if records else 0
        
        # 计算总补贴面积
        total_area = sum(record[5] for record in records) if records else 0
        
        # 计算人均补贴
        member_count = len(members) if members else 1
        average_amount = total_amount / member_count if member_count > 0 else 0
        
        return {
            "family_id": family_id,
            "year": year,
            "members": members,
            "subsidies": records,
            "total_amount": total_amount,
            "total_area": total_area,
            "average_amount": average_amount
        }
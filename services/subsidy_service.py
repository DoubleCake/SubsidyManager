# services.py
from dao import FamilyDAO, PersonDAO, LandDAO, SubsidyTypeDAO, SubsidyRecordDAO, ConflictRuleDAO
from datetime import date


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
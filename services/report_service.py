# services.py
from dao import FamilyDAO, PersonDAO, LandDAO, SubsidyTypeDAO, SubsidyRecordDAO, ConflictRuleDAO
from datetime import date
from . import FamilyService,SubsidyService

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
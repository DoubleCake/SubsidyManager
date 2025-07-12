# services.py
from dao import FamilyDAO, PersonDAO, LandDAO, SubsidyRecordDAO
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

    def search_families(self, keyword):
        #根据输入的身份证号\姓名\家庭编号等信息模糊查询家庭
        return self.family_dao.search_families(keyword)
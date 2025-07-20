
from models import FamilyDAO, PersonDAO, VillageDAO

class FamilyService:
    def __init__(self, db_manager):
        self.family_dao = FamilyDAO(db_manager)
        self.person_dao = PersonDAO(db_manager)
        self.village_dao = VillageDAO(db_manager)
    
    def create_family(self, landarea, villageid, groupid, address=None):
        return self.family_dao.create_family(landarea, villageid, groupid, address)
    
    def get_family_details(self, family_id):
        family = self.family_dao.get_family_by_id(family_id)
        if not family:
            return None
        
        # 获取村庄信息
        village = self.village_dao.get_village_by_id(family['villageid'])
        
        # 获取家庭成员
        members = self.person_dao.get_family_members(family_id)
        
        # 获取户主
        head = self.person_dao.get_family_head(family_id)
        
        return {
            'id': family['id'],
            'name': family['name'],
            'landarea': family['landarea'],
            'village': village['name'] if village else "未知村庄",
            'town': village['town'] if village else "未知镇",
            'groupid': family['groupid'],
            'groupname': f"第{family['groupid']}组",
            'address': family['address'] or "未知地址",
            'head': head['name'] if head else "未设置户主",
            'members': [dict(member) for member in members]
        }
    
    def search_families(self, village_id=None, group_id=None, name=None):
        families = self.family_dao.search_families(village_id, group_id, name)
        result = []
        
        for family in families:
            village = self.village_dao.get_village_by_id(family['villageid'])
            head = self.person_dao.get_family_head(family['id'])
            
            result.append({
                'id': family['id'],
                'name': family['name'],
                'landarea': family['landarea'],
                'village': village['name'] if village else "未知村庄",
                'groupname': f"第{family['groupid']}组",
                'address': family['address'] or "未知地址",
                'head': head['name'] if head else "未设置户主"
            })
        
        return result
    
    def update_family_info(self, family_id, landarea=None, address=None):
        return self.family_dao.update_family(family_id, landarea=landarea, address=address)
    
    def delete_family(self, family_id):
        # 先删除家庭成员
        self.person_dao.delete_family_members(family_id)
        # 再删除家庭
        return self.family_dao.delete_family(family_id)
    
    def set_family_head(self, family_id, person_id):
        success = self.person_dao.set_family_head(family_id, person_id)
        if success:
            # 更新家庭名称
            head = self.person_dao.get_person_by_id(person_id)
            if head:
                return self.family_dao.update_family_name(family_id, head['name'])
        return False

    def add_family_member(self, family_id, name, relation, gender=None, age=None, idcard=None):
        return self.person_dao.create_person(family_id, name, relation, gender, age, idcard)
    
    def update_family_member(self, person_id, name=None, gender=None, age=None, idcard=None, relation=None):
        return self.person_dao.update_person(person_id, name, gender, age, idcard, relation)
    
    def delete_family_member(self, person_id):
        return self.person_dao.delete_person(person_id)
    
    def get_group_names(self):
        """获取所有小组名称（这里根据需求直接转换为汉字）"""
        return {i: f"{i}组" for i in range(1, 21)}  # 假设最多20个组
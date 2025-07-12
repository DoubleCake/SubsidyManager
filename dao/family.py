# models/family.py
from database import execute_query

class FamilyDAO:
    def __init__(self, db_path='family_subsidies.db'):
        self.db_path = db_path
    
    def add_family(self, family_id, create_date=None):
        """添加新家庭"""
        if not create_date:
            create_date = date.today().isoformat()
        return execute_query(
            self.db_path,
            "INSERT INTO family (family_id, create_date) VALUES (?, ?)",
            (family_id, create_date)
        )
    
    def get_families(self):
        """获取所有家庭"""
        return execute_query(
            self.db_path,
            "SELECT * FROM family",
            fetch=True
        )
    
    def get_family(self, family_id):
        """获取单个家庭信息"""
        return execute_query(
            self.db_path,
            "SELECT * FROM family WHERE family_id = ?",
            (family_id,),
            fetch=True
        )
    
    def update_family(self, family_id, create_date):
        """更新家庭信息"""
        return execute_query(
            self.db_path,
            "UPDATE family SET create_date = ? WHERE family_id = ?",
            (create_date, family_id)
        )
    
    def delete_family(self, family_id):
        """删除家庭"""
        return execute_query(
            self.db_path,
            "DELETE FROM family WHERE family_id = ?",
            (family_id,)
        )
    
    def get_member_count(self, family_id):
        """获取家庭成员数量"""
        result = execute_query(
            self.db_path,
            "SELECT COUNT(*) FROM person WHERE family_id = ?",
            (family_id,),
            fetch=True
        )
        return result[0][0] if result else 0
    
    def get_lands(self, family_id):
        """获取家庭用地"""
        return execute_query(
            self.db_path,
            "SELECT * FROM land WHERE family_id = ?",
            (family_id,),
            fetch=True
        )
    
    def get_subsidies(self, family_id, year=None):
        """获取家庭补贴记录"""
        query = """
            SELECT r.*, p.name AS person_name, s.name AS subsidy_name, l.land_type
            FROM subsidy_record r
            JOIN person p ON r.person_id = p.person_id
            JOIN subsidy_type s ON r.subsidy_id = s.subsidy_id
            JOIN land l ON r.land_id = l.land_id
            WHERE p.family_id = ?
        """
        params = [family_id]
        
        if year:
            query += " AND r.year = ?"
            params.append(year)
        
        return execute_query(
            self.db_path,
            query,
            params,
            fetch=True
        )


# models/land.py
from database import execute_query

class LandDAO:
    def __init__(self, db_path='family_subsidies.db'):
        self.db_path = db_path
    
    def add_land(self, family_id, area, land_type, year):
        """添加用地记录"""
        # 检查家庭是否存在
        family_exists = execute_query(
            self.db_path,
            "SELECT 1 FROM family WHERE family_id = ?",
            (family_id,),
            fetch=True
        )
        if not family_exists:
            raise ValueError(f"家庭 {family_id} 不存在")
        
        return execute_query(
            self.db_path,
            '''INSERT INTO land 
            (family_id, area, land_type, year)
            VALUES (?, ?, ?, ?)''',
            (family_id, area, land_type, year)
        )
    
    def get_land(self, land_id):
        """获取单个用地信息"""
        result = execute_query(
            self.db_path,
            "SELECT * FROM land WHERE land_id = ?",
            (land_id,),
            fetch=True
        )
        if result:
            return {
                "land_id": result[0][0],
                "family_id": result[0][1],
                "area": result[0][2],
                "land_type": result[0][3],
                "year": result[0][4]
            }
        return None
    
    def get_lands(self, family_id=None, year=None):
        """获取用地列表"""
        query = "SELECT * FROM land"
        params = []
        
        conditions = []
        if family_id:
            conditions.append("family_id = ?")
            params.append(family_id)
        if year is not None:
            conditions.append("year = ?")
            params.append(year)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        results = execute_query(self.db_path, query, params, fetch=True)
        lands = []
        for row in results:
            lands.append({
                "land_id": row[0],
                "family_id": row[1],
                "area": row[2],
                "land_type": row[3],
                "year": row[4]
            })
        return lands
    
    def update_land(self, land_id, area=None, land_type=None, year=None):
        """更新用地信息"""
        # 获取当前用地信息
        land = self.get_land(land_id)
        if not land:
            raise ValueError(f"用地 {land_id} 不存在")
        
        # 构建更新字段和参数
        updates = []
        params = []
        
        if area is not None:
            updates.append("area = ?")
            params.append(area)
        
        if land_type is not None:
            updates.append("land_type = ?")
            params.append(land_type)
        
        if year is not None:
            updates.append("year = ?")
            params.append(year)
        
        # 如果没有更新字段，直接返回
        if not updates:
            return False
        
        # 添加WHERE条件
        params.append(land_id)
        query = f"UPDATE land SET {', '.join(updates)} WHERE land_id = ?"
        
        return execute_query(self.db_path, query, params)
    
    def delete_land(self, land_id):
        """删除用地"""
        # 检查用地是否被补贴记录引用
        subsidy_ref = execute_query(
            self.db_path,
            "SELECT 1 FROM subsidy_record WHERE land_id = ?",
            (land_id,),
            fetch=True
        )
        if subsidy_ref:
            raise ValueError("该用地已被补贴记录引用，无法删除")
        
        return execute_query(
            self.db_path,
            "DELETE FROM land WHERE land_id = ?",
            (land_id,)
        )
    
    def get_family_land_summary(self, family_id, year=None):
        """获取家庭用地统计摘要"""
        query = """
        SELECT land_type, SUM(area) AS total_area
        FROM land
        WHERE family_id = ?
        """
        params = [family_id]
        
        if year:
            query += " AND year = ?"
            params.append(year)
        
        query += " GROUP BY land_type"
        
        results = execute_query(self.db_path, query, params, fetch=True)
        
        summary = {}
        for row in results:
            summary[row[0]] = row[1]
        
        return summary
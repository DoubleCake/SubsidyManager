import sqlite3
from datetime import datetime
from PySide6.QtCore import QDate
from models.subsidy_model import SubsidyDAO
class SubsidyService:
    def __init__(self, db_path='family_subsidies.db'):
        self.dao = SubsidyDAO(db_path)
    
    def get_subsidy_type(self, subsidy_id):
        """获取单个补贴类型详情"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT subsidy_id, name, code, year, amount_per_unit, 
                   is_mutual_exclusive, allow_multiple, land_requirement,
                   start_date, end_date, is_active
            FROM subsidy_type
            WHERE subsidy_id = ?
        """, (subsidy_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # 转换为字典
        data = {
            "id": row[0],
            "name": row[1],
            "code": row[2],
            "year": row[3],
            "unit_amount": row[4],
            "is_mutual_exclusive": bool(row[5]),
            "allow_multiple": bool(row[6]),
            "land_requirement": row[7],
            "start_date": self.parse_date(row[8]),
            "end_date": self.parse_date(row[9]),
            "is_active": bool(row[10])
        }
        
        # 添加互斥规则ID
        cursor.execute("""
            SELECT conflicting_subsidy_id 
            FROM conflict_rule
            WHERE subsidy_id = ?
        """, (subsidy_id,))
        
        conflict_row = cursor.fetchone()
        data["conflict_id"] = conflict_row[0] if conflict_row else None
        
        conn.close()
        return data
    
    def get_all_subsidy_types(self):
        """获取所有补贴类型"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT subsidy_id, name, code, year, amount_per_unit, is_active
            FROM subsidy_type
            ORDER BY year DESC, name
        """)
        
        types = []
        for row in cursor.fetchall():
            types.append({
                "id": row[0],
                "name": row[1],
                "code": row[2],
                "year": row[3],
                "unit_amount": row[4],
                "is_active": bool(row[5])
            })
        
        conn.close()
        return types
    
    def create_subsidy_type(self, data):
        """创建新的补贴类型"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 生成唯一ID
        subsidy_id = f"{data['code']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 插入补贴类型
        cursor.execute("""
            INSERT INTO subsidy_type (
                subsidy_id, name, code, year, amount_per_unit, 
                is_mutual_exclusive, allow_multiple, land_requirement,
                start_date, end_date, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            subsidy_id,
            data["name"],
            data["code"],
            data["year"],
            data["unit_amount"] if data["amount_type"] > 0 else 0,
            int(data["is_mutual_exclusive"]),
            int(data["allow_multiple"]),
            data.get("land_requirement", ""),
            data["start_date"].toString("yyyy-MM-dd"),
            data["end_date"].toString("yyyy-MM-dd"),
            int(data["is_active"])
        ))
        
        # 插入互斥规则
        if data["is_mutual_exclusive"] and data["conflict_id"]:
            cursor.execute("""
                INSERT INTO conflict_rule (
                    subsidy_id, conflicting_subsidy_id, description
                ) VALUES (?, ?, ?)
            """, (
                subsidy_id,
                data["conflict_id"],
                f"{data['name']}与{self.get_subsidy_name(data['conflict_id'])}互斥"
            ))
        
        conn.commit()
        conn.close()
        
        # 返回创建的数据
        return {
            "id": subsidy_id,
            "name": data["name"],
            "code": data["code"],
            "year": data["year"],
            "is_active": data["is_active"]
        }
    
    def update_subsidy_type(self, subsidy_id, data):
        """更新补贴类型"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 更新补贴类型
        cursor.execute("""
            UPDATE subsidy_type SET
                name = ?,
                code = ?,
                year = ?,
                amount_per_unit = ?,
                is_mutual_exclusive = ?,
                allow_multiple = ?,
                land_requirement = ?,
                start_date = ?,
                end_date = ?,
                is_active = ?
            WHERE subsidy_id = ?
        """, (
            data["name"],
            data["code"],
            data["year"],
            data["unit_amount"] if data["amount_type"] > 0 else 0,
            int(data["is_mutual_exclusive"]),
            int(data["allow_multiple"]),
            data.get("land_requirement", ""),
            data["start_date"].toString("yyyy-MM-dd"),
            data["end_date"].toString("yyyy-MM-dd"),
            int(data["is_active"]),
            subsidy_id
        ))
        
        # 删除旧的互斥规则
        cursor.execute("DELETE FROM conflict_rule WHERE subsidy_id = ?", (subsidy_id,))
        
        # 插入新的互斥规则
        if data["is_mutual_exclusive"] and data["conflict_id"]:
            cursor.execute("""
                INSERT INTO conflict_rule (
                    subsidy_id, conflicting_subsidy_id, description
                ) VALUES (?, ?, ?)
            """, (
                subsidy_id,
                data["conflict_id"],
                f"{data['name']}与{self.get_subsidy_name(data['conflict_id'])}互斥"
            ))
        
        conn.commit()
        conn.close()
        
        # 返回更新的数据
        return {
            "id": subsidy_id,
            "name": data["name"],
            "code": data["code"],
            "year": data["year"],
            "is_active": data["is_active"]
        }
    
    def get_subsidy_name(self, subsidy_id):
        """获取补贴类型名称"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM subsidy_type WHERE subsidy_id = ?", (subsidy_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "未知补贴"
    
    def parse_date(self, date_str):
        """将字符串日期转换为QDate"""
        if not date_str:
            return QDate.currentDate()
        return QDate.fromString(date_str, "yyyy-MM-dd")
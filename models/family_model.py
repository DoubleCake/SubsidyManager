# dao/family_dao.py
from database import execute_query  # 假设这是你的数据库执行函数


class FamilyDAO:
    def __init__(self, db_path='family_subsidies.db'):
        self.db_path = db_path
# dao/family_dao.py
import sqlite3


class FamilyDAO:
    def __init__(self, db_path='family_subsidies.db'):
        self.db_path = db_path

    def create_family(self, head_id: int, land_area: float, ):
        """
        创建一个家庭，并为其分配一块新的土地。
        
        :param head_id: 户主ID（来自 person 表）
        :param land_area: 承包土地的面积
        :param contract_code: 承包合同编码，默认为 0
        :return: 新增的家庭ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:

            # 插入家庭信息，包含 contract_code
            cursor.execute(
                "INSERT INTO family (head_id, land_area) VALUES (?, ?)",
                (head_id, land_area)
            )
            family_id = cursor.lastrowid
            conn.commit()
            return family_id

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_family_by_id(self, family_id: int):
        """
        获取家庭详情（包含户主、土地大小--对应的存在的家庭成员等等信息）
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        sql = """    
        SELECT 
            f.id AS family_id,       -- 获取家庭ID并重命名为family_id
            f.head_id,               -- 获取户主ID
            p.name AS head_name,     -- 获取户主姓名并重命名为head_name
            f.land_area                  -- 获取家庭的面积大小
        FROM family f                -- 从family表查询，别名为f
        JOIN person p ON f.head_id = p.person_id            -- 连接person表，别名为p 连接条件：家庭表中的户主ID等于人员表中的ID
        WHERE f.id = ?               -- 筛选条件：只查询指定ID的家庭
        """
        cursor.execute(sql, (family_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return None

        return {
            'id': result[0],
            'head_id': result[1],
            'head_name': result[2],
            'land_area': result[3],

        }

    def update_family(self, family_id: int, land_area:float):
        """
        更新家庭信息
        """
        # 更新家庭基本信息
        execute_query(
            self.db_path,
            "UPDATE family SET land_area = ?, WHERE id = ?",
            (land_area,  family_id)
        )


    def delete_family(self, family_id: int):
        """
        删除一个家庭及其关联数据
        """
        # 删除成员和土地关联
        execute_query(self.db_path, "DELETE FROM family_member WHERE family_id = ?", (family_id,))
        execute_query(self.db_path, "DELETE FROM family_land WHERE family_id = ?", (family_id,))
        # 删除家庭本身
        execute_query(self.db_path, "DELETE FROM family WHERE id = ?", (family_id,))

    def get_all_families(self):
        """
        获取所有家庭的基础信息（用于表格显示）
        """
        families = execute_query(
            self.db_path,
            "SELECT id, land_id, head_id FROM family",
            fetch_all=True
        )
        return [
            {"id": f[0], "land_id": f[1], "head_id": f[2]} for f in families
        ]
    # dao/family_dao.py

    def get_all_families_paginated(self, offset, limit):
        """
        获取分页的家庭信息（用于表格显示）
        返回包含家庭ID、土地面积、户主姓名、村名、组号和家庭成员数的完整家庭信息
        参数:
            offset (int): 起始位置（跳过多少条记录）
            limit (int): 每页记录数
            
        返回:
            list: 包含家庭信息的字典列表
        """
        sql = """
            SELECT 
                f.id AS family_id,
                f.land_area,
                p_head.name AS head_name,
                v.villageName AS village_name,
                p_head.groupNum AS group_number,
                (
                    SELECT COUNT(*) 
                    FROM person 
                    WHERE family_id = f.id
                ) AS member_count
            FROM family f   -- 连接户主信息（获取村ID和组号）
          
            LEFT JOIN person p_head ON f.head_id = p_head.person_id  -- 通过户主的村ID获取村名
            LEFT JOIN village v ON p_head.village_id = v.id
            ORDER BY f.id
            LIMIT ? OFFSET ?
        """
    
        
        families = execute_query(
            self.db_path,
            sql,
            (limit, offset),
            fetch_all=True
        )
        
        # 如果查询结果为 None（没有数据），返回空列表
        if families is None:
            return []
        
        return [
            {
                "id": family[0],          # family_id
                "land_area": family[1],    # land_area
                "head_name": family[2],    # head_name
                "village_name": family[3], # village_name
                "group_number": family[4], # group_number
                "member_count": family[5]  # member_count
            } for family in families
        ]
    
    def search_family(self, keyword: str):
        families = execute_query(
            self.db_path,
            "SELECT id, land_id, head_id FROM family WHERE head_id LIKE ? OR land_id LIKE ?",
            (f"%{keyword}%", f"%{keyword}%"),
            fetch_all=True
        )
        return [
            {"id": f[0], "land_id": f[1], "head_id": f[2]} for f in families
        ]

    def get_total_count(self):
        count = execute_query(
            self.db_path,
            "SELECT COUNT(*) FROM family",
            fetch_one=True
        )
        return count[0]
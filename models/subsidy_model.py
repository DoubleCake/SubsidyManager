# models/subsidy_model.py
from database import get_db_connection


class SubsidyDAO:
    """
    数据访问对象（DAO）类：用于对补贴类型进行数据库操作
    表结构：
        subsidy_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT NOT NULL,  -- 补贴名称
            amount REAL DEFAULT 0, -- 补贴标准/金额
            year INTEGER, -- 补贴年份
            description TEXT, -- 详细描述
            land_type TEXT, -- 针对的土地属性（如耕地、林地、宅基地等）
            is_mutual_exclusive BOOLEAN DEFAULT 0 -- 是否互斥（布尔值）
        )
    """
    def __init__(self, db_path='family_subsidies.db'):
        self.db_path = db_path
    def get_all_subsidies(self):
        """
        获取所有补贴类型
        :return: 字典列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()  # 创建游标
        cursor.execute('''
            SELECT id, name, amount, year, description, land_type, is_mutual_exclusive # 选择需要的字段
            FROM subsidy_types
            ''')
        rows = cursor.fetchall()  # 获取所有结果
        conn.close()  # 关闭数据库连接
        return [dict(row) for row in rows]  # 将结果转换为字典列表 
        

    def search_subsidies(self, name=""):
        """
        按名称模糊搜索补贴类型
        :param name: 搜索关键词
        :return: 字典列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, amount, year, description, land_type, is_mutual_exclusive 
            FROM subsidy_types
            WHERE name LIKE ?
        ''', (f'%{name}%',))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_subsidy(self, name, amount=0.0, year=None, description="", land_type="", is_mutual_exclusive=False):
        """
        添加新补贴类型
        :param name: 补贴名称（必填）
        :param amount: 补贴标准/金额
        :param year: 补贴年份
        :param description: 详细描述
        :param land_type: 针对的土地属性（如耕地、林地、宅基地等）
        :param is_mutual_exclusive: 是否互斥（布尔值）
        :return: 成功与否
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO subsidy_types (name, amount, year, description, land_type, is_mutual_exclusive)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, amount, year, description, land_type, int(is_mutual_exclusive)))
            conn.commit()
            return True
        except Exception as e:
            print("添加补贴类型失败:", e)
            return False
        finally:
            conn.close()

    def update_subsidy(self, subsidy_id, **kwargs):
        """
        更新补贴类型信息
        :param subsidy_id: 补贴ID
        :param kwargs: 可变参数（name, amount, year, description, land_type, is_mutual_exclusive）
        :return: 成功与否
        """
        if not kwargs:
            return False

        keys = ', '.join([f"{k} = ?" for k in kwargs])
        values = list(kwargs.values()) + [subsidy_id]
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                UPDATE subsidy_types SET {keys} WHERE id = ?
            ''', values)
            conn.commit()
            return True
        except Exception as e:
            print("更新补贴类型失败:", e)
            return False
        finally:
            conn.close()

    def delete_subsidy(self, subsidy_id):
        """
        删除补贴类型
        :param subsidy_id: 补贴ID
        :return: 成功与否
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM subsidy_types WHERE id = ?', (subsidy_id,))
            conn.commit()
            return True
        except Exception as e:
            print("删除补贴类型失败:", e)
            return False
        finally:
            conn.close()
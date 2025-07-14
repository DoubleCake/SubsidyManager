# models/subsidy_record_model.py

from database import get_db_connection


class SubsidyRecordDAO:
    def __init__(self):
        self.conn = get_db_connection()
        self.create_table()

    def create_table(self):
        """创建补贴发放记录表（如果不存在）"""
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS subsidy_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    family_id INTEGER NOT NULL,
                    subsidy_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    year INTEGER,
                   发放日期 TEXT DEFAULT CURRENT_DATE,
                   备注 TEXT,
                    FOREIGN KEY (family_id) REFERENCES families(id),
                    FOREIGN KEY (subsidy_id) REFERENCES subsidies(id)
                )
            ''')

    def add_record(self, family_id, subsidy_id, amount, year=None,发放日期=None,备注=""):
        """
        添加补贴发放记录
        :param family_id: 家庭ID
        :param subsidy_id: 补贴类型ID
        :param amount: 发放金额
        :param year: 年份
        :param 发放日期: 发放日期（默认今天）
        :param 备注: 备注信息
        :return: 成功与否
        """
        try:
            with self.conn:
                self.conn.execute('''
                    INSERT INTO subsidy_records (family_id, subsidy_id, amount, year, 发放日期, 备注)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (family_id, subsidy_id, amount, year, 发放日期,备注))
            return True
        except Exception as e:
            print(f"添加记录失败: {e}")
            return False

    def get_all_records(self):
        """
        获取所有补贴发放记录
        :return: 记录列表（字典形式）
        """
        cursor = self.conn.execute('''
            SELECT r.id, r.family_id, f.户主姓名 AS family_name, 
                   r.subsidy_id, s.name AS subsidy_name,
                   r.amount, r.year, r.发放日期, r.备注
            FROM subsidy_records r
            LEFT JOIN families f ON r.family_id = f.id
            LEFT JOIN subsidies s ON r.subsidy_id = s.id
        ''')
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def search_records(self, family_id=None, subsidy_id=None, year=None):
        """
        按条件搜索补贴发放记录
        :param family_id: 家庭ID
        :param subsidy_id: 补贴类型ID
        :param year: 年份
        :return: 记录列表（字典形式）
        """
        query = '''
            SELECT r.id, r.family_id, f.户主姓名 AS family_name, 
                   r.subsidy_id, s.name AS subsidy_name,
                   r.amount, r.year, r.发放日期, r.备注
            FROM subsidy_records r
            LEFT JOIN families f ON r.family_id = f.id
            LEFT JOIN subsidies s ON r.subsidy_id = s.id
            WHERE 1=1
        '''
        params = []

        if family_id:
            query += " AND r.family_id = ?"
            params.append(family_id)
        if subsidy_id:
            query += " AND r.subsidy_id = ?"
            params.append(subsidy_id)
        if year:
            query += " AND r.year = ?"
            params.append(year)

        cursor = self.conn.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def update_record(self, record_id, **kwargs):
        """
        更新补贴发放记录
        :param record_id: 记录ID
        :param kwargs: 可变字段（如 amount, year, 备注等）
        :return: 成功与否
        """
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        query = f"UPDATE subsidy_records SET {', '.join(fields)} WHERE id = ?"
        values.append(record_id)

        try:
            with self.conn:
                self.conn.execute(query, values)
            return True
        except Exception as e:
            print(f"更新记录失败: {e}")
            return False

    def delete_record(self, record_id):
        """
        删除指定ID的补贴发放记录
        :param record_id: 记录ID
        :return: 成功与否
        """
        try:
            with self.conn:
                self.conn.execute("DELETE FROM subsidy_records WHERE id = ?", (record_id,))
            return True
        except Exception as e:
            print(f"删除记录失败: {e}")
            return False
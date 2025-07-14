# services/record_service.py

from database import get_db_connection


class RecordService:
    def __init__(self):
        self.conn = get_db_connection()

    def get_all_records(self):
        cursor = self.conn.execute('''
            SELECT r.id, f.户主姓名 AS 家庭, s.名称 AS 补贴类型, r.金额, r.发放日期
            FROM records r
            JOIN families f ON r.家庭ID = f.id
            JOIN subsidies s ON r.补贴ID = s.id
        ''')
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_all_families(self):
        cursor = self.conn.execute('SELECT id, 户主姓名 FROM families')
        return [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_subsidies(self):
        cursor = self.conn.execute('SELECT id, 名称 FROM subsidies')
        return [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]

    def search_records(self, family_id=None, subsidy_id=None):
        query = '''
            SELECT r.id, f.户主姓名 AS 家庭, s.名称 AS 补贴类型, r.金额, r.发放日期
            FROM records r
            JOIN families f ON r.家庭ID = f.id
            JOIN subsidies s ON r.补贴ID = s.id
            WHERE 1=1
        '''
        params = []

        if family_id:
            query += ' AND r.家庭ID = ?'
            params.append(family_id)
        if subsidy_id:
            query += ' AND r.补贴ID = ?'
            params.append(subsidy_id)

        cursor = self.conn.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def add_record(self, 家庭, 补贴类型, 金额, 发放日期):
        try:
            with self.conn:
                self.conn.execute('''
                    INSERT INTO records (家庭ID, 补贴ID, 金额, 发放日期)
                    VALUES (?, ?, ?, ?)
                ''', (家庭, 补贴类型, 金额, 发放日期))
            return True
        except Exception as e:
            print(f"添加记录失败: {e}")
            return False

    def update_record(self, record_id, 家庭, 补贴类型, 金额, 发放日期):
        try:
            with self.conn:
                self.conn.execute('''
                    UPDATE records SET 家庭ID=?, 补贴ID=?, 金额=?, 发放日期=?
                    WHERE id=?
                ''', (家庭, 补贴类型, 金额, 发放日期, record_id))
            return True
        except Exception as e:
            print(f"更新记录失败: {e}")
            return False

    def delete_record(self, record_id):
        try:
            with self.conn:
                self.conn.execute("DELETE FROM records WHERE id=?", (record_id,))
            return True
        except Exception as e:
            print(f"删除记录失败: {e}")
            return False
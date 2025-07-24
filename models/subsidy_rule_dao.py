from typing import List, Dict, Optional
from .dbManager import DatabaseManager


class SubsidyRuleDAO:
    def __init__(self):
        self.db = DatabaseManager()

    # ---------- 增 ----------
    def add_rule(self, name: str, a_id: str, b_id: str, relation: str, desc: str = "") -> int:
        sql = """INSERT INTO subsidy_rules(name, subsidy_a_id, subsidy_b_id, relation, description)
                 VALUES(?, ?, ?, ?, ?)"""
        return self._execute(sql, (name, a_id, b_id, relation, desc), commit=True)

    # ---------- 删 ----------
    def delete_rule(self, rule_id: int) -> bool:
        return self._execute("DELETE FROM subsidy_rules WHERE id = ?", (rule_id,), commit=True) > 0

    # ---------- 改 ----------
    def update_rule(self, rule_id: int, **kwargs) -> bool:
        fields = [f"{k}=?" for k in kwargs]
        sql = f"UPDATE subsidy_rules SET {', '.join(fields)} WHERE id = ?"
        params = list(kwargs.values()) + [rule_id]
        return self._execute(sql, tuple(params), commit=True) > 0

    # ---------- 查 ----------
    def get_all_rules(self) -> List[Dict]:
        sql = """SELECT id, name, subsidy_a_id, subsidy_b_id, relation, description
                 FROM subsidy_rules ORDER BY id DESC"""
        return self._execute(sql, fetch_all=True)

    def search_rules(self, a_id: Optional[str] = None,
                     b_id: Optional[str] = None,
                     relation: Optional[str] = None,
                     keyword: Optional[str] = None) -> List[Dict]:
        sql = "SELECT * FROM subsidy_rules WHERE 1=1"
        params = []
        if a_id:
            sql += " AND subsidy_a_id = ?"
            params.append(a_id)
        if b_id:
            sql += " AND subsidy_b_id = ?"
            params.append(b_id)
        if relation:
            sql += " AND relation = ?"
            params.append(relation)
        if keyword:
            sql += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        sql += " ORDER BY id DESC"
        return self._execute(sql, tuple(params), fetch_all=True)

    # ---------- 通用 --------
    def _execute(self, sql: str, params=(), *, fetch_all=False, commit=False):
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        if commit:
            conn.commit()
        return cur.fetchall() if fetch_all else cur.lastrowid or cur.rowcount
# models/subsidy_model.py
"""
单例版 SubsidyDAO
所有数据库操作都走 DatabaseManager() 单例连接
其余字段/方法保持 100% 兼容
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
import sqlite3
# 单例数据库管理器
from .dbManager import DatabaseManager


class SubsidyDAO:
    def __init__(self, db_path: str = 'family_subsidies.db'):
        self.db = DatabaseManager(db_path)
        self._initialize_database()

    # ---------------- 建表 ---------------- #
    def _initialize_database(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS subsidy_types (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT    NOT NULL,
                amount          REAL    DEFAULT 0,
                year            INTEGER,
                description     TEXT,
                land_type       TEXT,
                is_mutual_exclusive BOOLEAN DEFAULT 0,
                is_activate     BOOLEAN DEFAULT 1,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS conflict_rules (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                subsidy_id           INTEGER NOT NULL,
                conflicting_subsidy_id INTEGER NOT NULL,
                description          TEXT,
                created_at           DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(subsidy_id, conflicting_subsidy_id),
                FOREIGN KEY (subsidy_id)           REFERENCES subsidy_types(id),
                FOREIGN KEY (conflicting_subsidy_id) REFERENCES subsidy_types(id)
            );
        """)
        conn.commit()

    # ---------------- 通用执行 ---------------- #
    def _execute(self, sql: str, params: tuple = (), *,
                 fetch_one=False, fetch_all=False, commit=False):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        if commit:
            conn.commit()
        if fetch_one:
            row = cursor.fetchone()
            return dict(row) if row else None
        if fetch_all:
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        return cursor.lastrowid or cursor.rowcount

    # ---------------- CRUD ---------------- #
    def create_subsidy_type(self, data: Dict[str, Any]) -> Optional[int]:
        cols = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql = f"INSERT INTO subsidy_types ({cols}) VALUES ({placeholders})"
        return self._execute(sql, tuple(data.values()), commit=True)

    def get_subsidy_by_id(self, subsidy_id: int) -> Optional[Dict]:
        sql = """SELECT * FROM subsidy_types WHERE id = ?"""
        return self._execute(sql, (subsidy_id,), fetch_one=True)

    def get_all_subsidies(self, active_only: bool = True) -> List[Dict]:
        sql = "SELECT * FROM subsidy_types"
        if active_only:
            sql += " WHERE is_activate = 1"
        sql += " ORDER BY year DESC, name"
        return self._execute(sql, fetch_all=True)

    def search_subsidies(self, name: str = "", year: Optional[int] = None,
                         land_type: str = "", active_only: bool = True) -> List[Dict]:
        sql = "SELECT * FROM subsidy_types WHERE 1=1"
        params = []
        if name:
            sql += " AND name LIKE ?"
            params.append(f"%{name}%")
        if year is not None:
            sql += " AND year = ?"
            params.append(year)
        if land_type:
            sql += " AND land_type = ?"
            params.append(land_type)
        if active_only:
            sql += " AND is_activate = 1"
        sql += " ORDER BY year DESC, name"
        return self._execute(sql, tuple(params), fetch_all=True)

    def update_subsidy(self, subsidy_id: int, update_data: Dict[str, Any]) -> bool:
        if not update_data:
            return False
        update_data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        set_clause = ', '.join([f"{k} = ?" for k in update_data])
        sql = f"UPDATE subsidy_types SET {set_clause} WHERE id = ?"
        params = list(update_data.values()) + [subsidy_id]
        return self._execute(sql, tuple(params), commit=True) > 0

    def delete_subsidy(self, subsidy_id: int) -> bool:
        sql = "DELETE FROM subsidy_types WHERE id = ?"
        return self._execute(sql, (subsidy_id,), commit=True) > 0

    # ---------------- 冲突规则 ---------------- #
    def create_conflict_rule(self, subsidy_id: int, conflicting_subsidy_id: int,
                             description: str = "") -> bool:
        sql = """INSERT INTO conflict_rules
                 (subsidy_id, conflicting_subsidy_id, description)
                 VALUES (?, ?, ?)
                 ON CONFLICT(subsidy_id, conflicting_subsidy_id) DO UPDATE SET
                 description=excluded.description"""
        return self._execute(sql, (subsidy_id, conflicting_subsidy_id, description), commit=True) > 0

    def get_conflict_rules(self, subsidy_id: int) -> List[Dict]:
        sql = """SELECT * FROM conflict_rules WHERE subsidy_id = ?"""
        return self._execute(sql, (subsidy_id,), fetch_all=True)

    def delete_conflict_rules(self, subsidy_id: int) -> bool:
        sql = "DELETE FROM conflict_rules WHERE subsidy_id = ?"
        return self._execute(sql, (subsidy_id,), commit=True) > 0
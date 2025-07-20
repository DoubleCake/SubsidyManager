# models/subsidy_model.py
from datetime import datetime
import sqlite3
from typing import List, Dict, Optional, Any, Union
from database import get_db_connection

class SubsidyDAO:
    """
    补贴类型数据访问对象 (DAO)
    提供对补贴类型数据的 CRUD 操作
    
    表结构：
        subsidy_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT NOT NULL,                -- 补贴名称
            amount REAL DEFAULT 0,             -- 补贴标准/金额
            year INTEGER,                      -- 补贴年份
            description TEXT,                  -- 详细描述
            land_type TEXT,                    -- 适用土地类型（耕地/林地/宅基地等）
            is_mutual_exclusive BOOLEAN DEFAULT 0, -- 是否互斥
            is_activate BOOLEAN DEFAULT 1,     -- 是否激活
            pre_submit BOOLEAN DEFAULT 0,      -- 是否预提交
            g_checked BOOLEAN DEFAULT 0,       -- 是否已审核
            town_checked BOOLEAN DEFAULT 0,    -- 是否乡镇审核
            is_finished BOOLEAN DEFAULT 0,     -- 是否已完成
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- 创建时间
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- 更新时间
        )
        
        conflict_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subsidy_id INTEGER NOT NULL,           -- 主补贴ID
            conflicting_subsidy_id INTEGER NOT NULL, -- 冲突补贴ID
            description TEXT,                       -- 冲突描述
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subsidy_id) REFERENCES subsidy_types(id),
            FOREIGN KEY (conflicting_subsidy_id) REFERENCES subsidy_types(id)
        )
    """
    
    def __init__(self, db_path: str = 'family_subsidies.db'):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """确保数据库表结构存在"""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            # 创建补贴类型表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subsidy_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    amount REAL DEFAULT 0,
                    year INTEGER,
                    description TEXT,
                    land_type TEXT,
                    is_mutual_exclusive BOOLEAN DEFAULT 0,
                    is_activate BOOLEAN DEFAULT 1,
                    pre_submit BOOLEAN DEFAULT 0,
                    g_checked BOOLEAN DEFAULT 0,
                    town_checked BOOLEAN DEFAULT 0,
                    is_finished BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建冲突规则表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conflict_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subsidy_id INTEGER NOT NULL,
                    conflicting_subsidy_id INTEGER NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subsidy_id) REFERENCES subsidy_types(id),
                    FOREIGN KEY (conflicting_subsidy_id) REFERENCES subsidy_types(id),
                    UNIQUE(subsidy_id, conflicting_subsidy_id)
                )
            ''')
            
            conn.commit()
    
    def _execute_query(
        self, 
        query: str, 
        params: tuple = (), 
        fetch_one: bool = False,
        fetch_all: bool = False,
        commit: bool = False
    ) -> Union[List[Dict], Dict, int, None]:
        """
        执行SQL查询的通用方法
        
        :param query: SQL查询语句
        :param params: 查询参数
        :param fetch_one: 是否获取单条结果
        :param fetch_all: 是否获取所有结果
        :param commit: 是否提交事务
        :return: 查询结果
        """
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute(query, params)
                
                if commit:
                    conn.commit()
                
                if fetch_one:
                    row = cursor.fetchone()
                    return dict(row) if row else None
                
                if fetch_all:
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                
                # 对于增删改操作，返回受影响的行数
                return cursor.rowcount
                
            except sqlite3.Error as e:
                print(f"数据库操作失败: {e}")
                if commit:
                    conn.rollback()
                raise e
    
    def create_subsidy_type(self, data: Dict[str, Any]) -> int:
        """
        创建新的补贴类型
        
        :param data: 补贴类型数据字典
        :return: 新创建的补贴类型ID
        """
        # 准备插入语句
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO subsidy_types ({columns}) VALUES ({placeholders})"
        
        # 执行插入操作
        rowcount = self._execute_query(query, tuple(data.values()), commit=True)
        
        if rowcount > 0:
            # 获取最后插入的ID
            last_id = self._execute_query("SELECT last_insert_rowid()", fetch_one=True)
            return last_id['last_insert_rowid()'] if last_id else None
        return None
    
    def create_conflict_rule(self, subsidy_id: int, conflicting_subsidy_id: int, description: str = "") -> bool:
        """
        创建冲突规则
        
        :param subsidy_id: 主补贴ID
        :param conflicting_subsidy_id: 冲突补贴ID
        :param description: 冲突描述
        :return: 是否成功
        """
        query = """
        INSERT INTO conflict_rules (subsidy_id, conflicting_subsidy_id, description)
        VALUES (?, ?, ?)
        """
        rowcount = self._execute_query(
            query, 
            (subsidy_id, conflicting_subsidy_id, description),
            commit=True
        )
        return rowcount > 0
    
    def get_subsidy_by_id(self, subsidy_id: int) -> Optional[Dict]:
        """
        根据ID获取单个补贴类型详情
        
        :param subsidy_id: 补贴ID
        :return: 补贴类型字典或None
        """
        query = """
        SELECT id, name, amount, year, description, land_type, 
               is_mutual_exclusive, is_activate, pre_submit, g_checked, 
               town_checked, is_finished, created_at, updated_at
        FROM subsidy_types
        WHERE id = ?
        """
        return self._execute_query(query, (subsidy_id,), fetch_one=True)
    
    def get_all_subsidies(self, active_only: bool = True) -> List[Dict]:
        """
        获取所有补贴类型
        
        :param active_only: 是否只获取激活的补贴
        :return: 补贴类型字典列表
        """
        query = """
        SELECT id, name, amount, year, description, land_type, 
               is_mutual_exclusive, is_activate
        FROM subsidy_types
        """
        
        if active_only:
            query += " WHERE is_activate = 1"
            
        query += " ORDER BY year DESC, name"
        
        return self._execute_query(query, fetch_all=True)
    
    def search_subsidies(
        self, 
        name: str = "", 
        year: Optional[int] = None,
        land_type: str = "",
        active_only: bool = True
    ) -> List[Dict]:
        """
        搜索补贴类型
        
        :param name: 名称关键词
        :param year: 年份
        :param land_type: 土地类型
        :param active_only: 是否只搜索激活的补贴
        :return: 补贴类型字典列表
        """
        query = """
        SELECT id, name, amount, year, description, land_type, 
               is_mutual_exclusive, is_activate
        FROM subsidy_types
        WHERE 1=1
        """
        params = []
        
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        
        if year is not None:
            query += " AND year = ?"
            params.append(year)
        
        if land_type:
            query += " AND land_type = ?"
            params.append(land_type)
        
        if active_only:
            query += " AND is_activate = 1"
        
        query += " ORDER BY year DESC, name"
        
        return self._execute_query(query, tuple(params), fetch_all=True)
    
    def update_subsidy(self, subsidy_id: int, update_data: Dict[str, Any]) -> bool:
        """
        更新补贴类型信息
        
        :param subsidy_id: 补贴ID
        :param update_data: 更新数据字典
        :return: 是否成功更新
        """
        if not update_data:
            return False
        
        # 添加更新时间戳
        update_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        set_clause = ', '.join([f"{k} = ?" for k in update_data.keys()])
        params = list(update_data.values()) + [subsidy_id]
        
        query = f"""
        UPDATE subsidy_types 
        SET {set_clause}
        WHERE id = ?
        """
        
        rowcount = self._execute_query(query, tuple(params), commit=True)
        return rowcount > 0
    
    def delete_subsidy(self, subsidy_id: int) -> bool:
        """
        删除补贴类型
        
        :param subsidy_id: 补贴ID
        :return: 是否成功删除
        """
        query = "DELETE FROM subsidy_types WHERE id = ?"
        rowcount = self._execute_query(query, (subsidy_id,), commit=True)
        return rowcount > 0
    
    def get_conflict_rules(self, subsidy_id: int) -> List[Dict]:
        """
        获取补贴的冲突规则
        
        :param subsidy_id: 补贴ID
        :return: 冲突规则列表
        """
        query = """
        SELECT id, conflicting_subsidy_id, description
        FROM conflict_rules
        WHERE subsidy_id = ?
        """
        return self._execute_query(query, (subsidy_id,), fetch_all=True)
    
    def delete_conflict_rules(self, subsidy_id: int) -> bool:
        """
        删除补贴的所有冲突规则
        
        :param subsidy_id: 补贴ID
        :return: 是否成功删除
        """
        query = "DELETE FROM conflict_rules WHERE subsidy_id = ?"
        rowcount = self._execute_query(query, (subsidy_id,), commit=True)
        return rowcount > 0
    
    def activate_subsidy(self, subsidy_id: int, activate: bool = True) -> bool:
        """
        激活或停用补贴
        
        :param subsidy_id: 补贴ID
        :param activate: 是否激活
        :return: 是否成功
        """
        query = "UPDATE subsidy_types SET is_activate = ? WHERE id = ?"
        rowcount = self._execute_query(
            query, 
            (1 if activate else 0, subsidy_id), 
            commit=True
        )
        return rowcount > 0
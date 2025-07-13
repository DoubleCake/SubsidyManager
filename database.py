# database.py
import sqlite3
import os

# 数据库文件路径（可自定义）
DB_PATH = "family_subsidies.db"


def init_database(db_path='family_subsidies.db'):
    """初始化数据库，创建所有表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建家庭表
    cursor.execute('''CREATE TABLE IF NOT EXISTS family (
                    family_id TEXT PRIMARY KEY,
                    create_date DATE DEFAULT (DATE('now'))
                )''')
    
    # 创建用地表
    cursor.execute('''CREATE TABLE IF NOT EXISTS land (
                    land_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    family_id TEXT NOT NULL,
                    area DECIMAL(10, 2) NOT NULL,
                    land_type TEXT NOT NULL CHECK(land_type IN ('承包种植地', '自留地', '林地')),
                    year INTEGER NOT NULL,
                    FOREIGN KEY (family_id) REFERENCES family(family_id)
                )''')
    
    # 创建人员表
    cursor.execute('''CREATE TABLE IF NOT EXISTS person (
                    person_id TEXT PRIMARY KEY,
                    family_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    phone TEXT,
                    has_social_card BOOLEAN DEFAULT 0,
                    is_head BOOLEAN DEFAULT 0,
                    FOREIGN KEY (family_id) REFERENCES family(family_id)
                )''')
    
    # 创建补贴类型表
    cursor.execute('''CREATE TABLE IF NOT EXISTS subsidy_type (
                    subsidy_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    land_requirement TEXT,
                    is_mutual_exclusive BOOLEAN DEFAULT 0,
                    allow_multiple BOOLEAN DEFAULT 0,
                    amount_per_unit DECIMAL(10, 2) NOT NULL
                )''')
    
    # 创建补贴记录表
    cursor.execute('''CREATE TABLE IF NOT EXISTS subsidy_record (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_id TEXT NOT NULL,
                    subsidy_id TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    grant_date DATE NOT NULL,
                    applied_area DECIMAL(10, 2) NOT NULL,
                    total_amount DECIMAL(10, 2) NOT NULL,
                    payment_method TEXT CHECK(payment_method IN ('社保卡', '银行卡', '现金')),
                    land_id INTEGER NOT NULL,
                    FOREIGN KEY (person_id) REFERENCES person(person_id),
                    FOREIGN KEY (subsidy_id) REFERENCES subsidy_type(subsidy_id),
                    FOREIGN KEY (land_id) REFERENCES land(land_id)
                )''')
    
    # 创建冲突规则表
    cursor.execute('''CREATE TABLE IF NOT EXISTS conflict_rule (
                    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subsidy_id TEXT NOT NULL,
                    conflicting_subsidy_id TEXT NOT NULL,
                    description TEXT,
                    FOREIGN KEY (subsidy_id) REFERENCES subsidy_type(subsidy_id),
                    FOREIGN KEY (conflicting_subsidy_id) REFERENCES subsidy_type(subsidy_id)
                )''')
    
    # 添加示例数据（如果不存在）
    try:
        cursor.execute("SELECT COUNT(*) FROM subsidy_type")
        if cursor.fetchone()[0] == 0:
            # 添加示例补贴类型
            subsidies = [
                ('EDU_A', '义务教育补贴', '适龄儿童教育补贴', '承包种植地', 0, 0, 1500),
                ('EDU_B', '特殊教育补贴', '特殊儿童教育补贴', '承包种植地', 1, 0, 2000),
                ('MED_C', '基本医疗保险', '农村合作医疗补贴', '自留地', 0, 1, 800),
                ('OLD_AGE', '养老补贴', '60岁以上老人补贴', '林地', 0, 1, 1200)
            ]
            cursor.executemany('''INSERT INTO subsidy_type 
                               (subsidy_id, name, description, land_requirement, 
                                is_mutual_exclusive, allow_multiple, amount_per_unit)
                               VALUES (?, ?, ?, ?, ?, ?, ?)''', subsidies)
            
            # 添加示例冲突规则
            rules = [
                ('EDU_B', 'EDU_A', '教育补贴互斥规则'),
                ('MED_C', 'OLD_AGE', '养老医疗冲突规则')
            ]
            cursor.executemany('''INSERT INTO conflict_rule 
                               (subsidy_id, conflicting_subsidy_id, description)
                               VALUES (?, ?, ?)''', rules)
    except:
        pass
    
    conn.commit()
    conn.close()


def get_db_connection():
    """
    获取数据库连接
    :return: 数据库连接对象
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 允许以字典形式访问查询结果
    return conn


def execute_query(db_path, query, params=None, fetch_all=False):
    """执行SQL查询"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if fetch_all:
            result = cursor.fetchall()
        else:
            result = cursor.fetchone()
            
        conn.commit()
        return result
    except sqlite3.Error as e:
        return None
    finally:
        conn.close()
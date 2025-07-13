# init_db.py
import sqlite3

def init_database(db_path='family_subsidies.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建 person 表（户主和成员都来自这个表）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS person (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gender TEXT,
        age INTEGER
    )
    ''')

    # 创建 land 表（土地信息）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS land (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT NOT NULL,
        area REAL
    )
    ''')

    # 创建 family 表（家庭基本信息）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS family (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        land_id INTEGER NOT NULL,
        head_id INTEGER NOT NULL,
        FOREIGN KEY (land_id) REFERENCES land(id),
        FOREIGN KEY (head_id) REFERENCES person(id)
    )
    ''')

    # 创建 family_member 表（家庭成员关联）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS family_member (
        family_id INTEGER NOT NULL,
        member_id INTEGER NOT NULL,
        FOREIGN KEY (family_id) REFERENCES family(id),
        FOREIGN KEY (member_id) REFERENCES person(id),
        PRIMARY KEY (family_id, member_id)
    )
    ''')

    # 创建 family_land 表（家庭其他土地关联）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS family_land (
        family_id INTEGER NOT NULL,
        land_id INTEGER NOT NULL,
        FOREIGN KEY (family_id) REFERENCES family(id),
        FOREIGN KEY (land_id) REFERENCES land(id),
        PRIMARY KEY (family_id, land_id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ 数据库和表已成功初始化！")

if __name__ == '__main__':
    init_database()
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ui import NewWindow
from database import execute_query
def print_database_schema(db_path):
    """打印数据库完整表结构"""
    # 获取所有表名
    
    print("="*50)
    tables_sql = "SELECT name FROM sqlite_master WHERE type='table'"
    tables = execute_query(db_path, tables_sql, fetch_all=True)
    
    if not tables:
        print("数据库中没有表")
        return
    
    print("="*50)
    print("数据库表结构")
    print("="*50)
    
    for table in tables:
        table_name = table[0]
        print(f"\n表名: {table_name}")
        print("-"*40)
        
        # 获取表结构
        schema_sql = f"PRAGMA table_info({table_name})"
        schema = execute_query(db_path, schema_sql, fetch_all=True)
        
        if not schema:
            print("  无字段信息")
            continue
            
        for col in schema:
            # cid, name, type, notnull, dflt_value, pk
            print(f"  字段: {col[1]:<15} 类型: {col[2]:<10} 主键: {col[5]} 非空: {col[3]}")
    
    print("="*50)

# 使用示例


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewWindow()
    window.show()
    sys.exit(app.exec())
    # print_database_schema("family_subsidies.db")
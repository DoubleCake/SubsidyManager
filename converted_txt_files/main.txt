import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from ui import LoginWindow
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
    # 创建应用
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 使用Fusion样式确保跨平台一致性
    # 设置应用程序字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    # 创建登录窗口
    login_window = LoginWindow()
    login_window.show()
    
    # 运行应用
    sys.exit(app.exec())
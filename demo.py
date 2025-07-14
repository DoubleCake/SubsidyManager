from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, 
    QHeaderView, QTableWidgetItem, QPushButton
)
from PySide6.QtCore import Qt

class TableDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("表格列宽自适应示例")
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "家庭ID", "户主名称", "总土地面积", "村", "组", "家庭人数"
        ])
        
        # 设置自适应列宽策略
        self.setup_column_resizing()
        
        # 添加示例数据
        self.fill_sample_data()
        
        # 添加刷新按钮
        btn_refresh = QPushButton("刷新列宽")
        btn_refresh.clicked.connect(self.adjust_columns)
        
        layout.addWidget(self.table)
        layout.addWidget(btn_refresh)
    
    def setup_column_resizing(self):
        """设置列宽自适应策略"""
        header = self.table.horizontalHeader()
        
        # 设置默认调整模式
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # 特定列设置
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 家庭ID - 根据内容调整
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 户主名称 - 根据内容调整
        header.setSectionResizeMode(5, QHeaderView.Stretch)           # 家庭人数 - 填充剩余空间
        
        # 设置初始列宽
        self.table.setColumnWidth(2, 150)  # 总土地面积 - 固定宽度
        self.table.setColumnWidth(3, 120)  # 村 - 固定宽度
        self.table.setColumnWidth(4, 80)   # 组 - 固定宽度
    
    def fill_sample_data(self):
        """填充示例数据"""
        sample_data = [
            [1001, "张三", "1250.75 平方米", "向阳村", 3, 4],
            [1002, "李四", "980.50 平方米", "幸福村", 5, 3],
            [1003, "王五", "2100.25 平方米", "光明村", 2, 5],
            [1004, "赵六", "750.00 平方米", "和平村", 4, 2],
            [1005, "钱七", "3200.00 平方米", "繁荣村", 1, 6],
            [1006, "孙八", "1580.30 平方米", "希望村", 6, 4],
            [1007, "周九", "920.45 平方米", "和谐村", 3, 3],
            [1008, "吴十", "2850.60 平方米", "富裕村", 2, 5],
        ]
        
        self.table.setRowCount(len(sample_data))
        
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                
                # 特殊处理数值类型
                if col in [0, 4, 5]:  # ID和数字列
                    item.setData(Qt.DisplayRole, int(value) if col in [0, 4, 5] else value)
                
                self.table.setItem(row, col, item)
        
        # 初始调整列宽
        self.adjust_columns()
    
    def adjust_columns(self):
        """调整列宽以适应内容"""
        # 对需要自适应的列进行调整
        for col in [0, 1]:
            self.table.resizeColumnToContents(col)
        
        # 确保表头可见
        self.table.horizontalHeader().setMinimumSectionSize(50)
        
        # 设置最大宽度限制
        self.table.setColumnWidth(1, min(self.table.columnWidth(1), 200))

if __name__ == "__main__":
    app = QApplication([])
    window = TableDemo()
    window.show()
    app.exec()
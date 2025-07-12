from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QMenuBar, QMenu, QTabWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("低收入家庭补贴管理系统")
        self.setGeometry(100, 100, 1200, 800)

        # 主窗口布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()

        # 左侧菜单栏
        self.menu_bar = QFrame()
        self.menu_bar.setStyleSheet("background-color: #3498db; color: white;")
        self.menu_bar.setFixedWidth(200)
        menu_layout = QVBoxLayout()
        menu_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        menu_items = ["用户管理", "家庭管理", "补贴发放", "统计报表"]
        self.menu_buttons = []

        for item in menu_items:
            btn = QPushButton(item)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: white;
                    padding: 15px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn.clicked.connect(self.handle_menu_click)
            menu_layout.addWidget(btn)
            self.menu_buttons.append(btn)

        menu_layout.addStretch()
        self.menu_bar.setLayout(menu_layout)
        main_layout.addWidget(self.menu_bar)

        # 右侧内容区域
        self.content_area = QFrame()
        self.content_area.setStyleSheet("background-color: #f5f6fa;")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        # 默认页面
        self.default_content = QLabel("请选择左侧功能以查看内容")
        self.default_content.setStyleSheet("font-size: 18px; color: #7f8c8d;")
        self.default_content.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.default_content)

        self.content_area.setLayout(self.content_layout)
        main_layout.addWidget(self.content_area)

        central_widget.setLayout(main_layout)

    def handle_menu_click(self):
        sender = self.sender()
        selected_text = sender.text()

        # 清空当前内容
        self.clear_content()

        if selected_text == "用户管理":
            self.show_person_table()
        elif selected_text == "家庭管理":
            self.show_family_table()
        elif selected_text == "补贴发放":
            self.show_subsidy_list()
        elif selected_text == "统计报表":
            self.show_report_summary()

    def clear_content(self):
        """清除当前 content_area 中的所有控件"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def show_person_table(self):
        label = QLabel("人员信息列表")
        label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.content_layout.addWidget(label)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["ID", "身份证号", "姓名", "年龄", "性别"])

        # 模拟数据
        data = [
            ("1", "110101199003072516", "张三", "34", "男"),
            ("2", "110101198506123456", "李四", "39", "女"),
            ("3", "110101199212012345", "王五", "32", "男"),
        ]

        table.setRowCount(len(data))
        for row, (id_, pid, name, age, gender) in enumerate(data):
            table.setItem(row, 0, QTableWidgetItem(id_))
            table.setItem(row, 1, QTableWidgetItem(pid))
            table.setItem(row, 2, QTableWidgetItem(name))
            table.setItem(row, 3, QTableWidgetItem(age))
            table.setItem(row, 4, QTableWidgetItem(gender))

        self.content_layout.addWidget(table)

    def show_family_table(self):
        label = QLabel("家庭信息列表")
        label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.content_layout.addWidget(label)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["家庭ID", "地址", "总收入", "成员数"])

        # 模拟数据
        data = [
            ("F1001", "北京市朝阳区XX街道", "5000元", "4人"),
            ("F1002", "北京市海淀区YY社区", "4200元", "3人"),
            ("F1003", "北京市东城区ZZ小区", "3800元", "5人"),
        ]

        table.setRowCount(len(data))
        for row, (fid, addr, income, members) in enumerate(data):
            table.setItem(row, 0, QTableWidgetItem(fid))
            table.setItem(row, 1, QTableWidgetItem(addr))
            table.setItem(row, 2, QTableWidgetItem(income))
            table.setItem(row, 3, QTableWidgetItem(members))

        self.content_layout.addWidget(table)

    def show_subsidy_list(self):
        label = QLabel("补贴发放记录")
        label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.content_layout.addWidget(label)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["补贴编号", "家庭ID", "金额", "发放时间"])

        # 模拟数据
        data = [
            ("S20250701", "F1001", "1200元", "2025-07-01"),
            ("S20250702", "F1002", "1000元", "2025-07-02"),
            ("S20250703", "F1003", "1500元", "2025-07-03"),
        ]

        table.setRowCount(len(data))
        for row, (sid, fid, amount, date) in enumerate(data):
            table.setItem(row, 0, QTableWidgetItem(sid))
            table.setItem(row, 1, QTableWidgetItem(fid))
            table.setItem(row, 2, QTableWidgetItem(amount))
            table.setItem(row, 3, QTableWidgetItem(date))

        self.content_layout.addWidget(table)

    def show_report_summary(self):
        label = QLabel("统计报告摘要")
        label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.content_layout.addWidget(label)

        summary = """
        <p><strong>总家庭数：</strong> 128户</p>
        <p><strong>累计补贴金额：</strong> ￥128,000.00</p>
        <p><strong>已发放金额：</strong> ￥115,000.00</p>
        <p><strong>未发放金额：</strong> ￥13,000.00</p>
        <p><strong>人均补贴金额：</strong> ￥890.00</p>
        """

        report_label = QLabel(summary)
        report_label.setTextFormat(Qt.RichText)
        self.content_layout.addWidget(report_label)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec_())
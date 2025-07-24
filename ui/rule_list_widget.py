# ui/conflict_rule_page.py
import json
from pathlib import Path
from typing import List, Dict

from PySide6.QtCore import Qt, QDate, QPoint
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QHeaderView, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QFrame, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QAbstractItemView,QMainWindow
)
from qfluentwidgets import (
    PrimaryPushButton, InfoBar, InfoBarPosition, TitleLabel, BodyLabel
)

from services import SubsidyService

class ConflictRulePage(QWidget):
    """补贴互斥规则独立页面（可拖动 + 表格 + 搜索）"""
    def __init__(self, subsidy_list: List[Dict], parent=None):
        super().__init__(parent)
        self.subsidy_service=SubsidyService()
        self.subsidies = self.subsidy_service.get_all_subsidies(active_only=True)
        self.setWindowTitle("补贴互斥规则")
        self.resize(700, 550)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.drag_position = QPoint()
        self.build_ui()
        self.load_rules()

    # ---------------- 外观框架 ---------------- #
    def build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(10, 10, 10, 10)

        content = QWidget()
        content.setObjectName("content")
        content.setStyleSheet("""
            #content {background-color:white;border-radius:8px;}
            QLabel#titleLabel {color:white;font-size:14px;font-weight:bold;}
            QPushButton#closeBtn {background:transparent;color:white;font-size:20px;border:none;width:30px;}
            QPushButton#closeBtn:hover {background:#e81123;}
        """)
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(0, 0, 0, 0)

        # 标题栏
        title_bar = self.create_title_bar()
        vbox.addWidget(title_bar)

        # 搜索条
        search_bar = self.create_search_bar()
        vbox.addLayout(search_bar)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["补贴A", "补贴B", "关系", "说明", "操作"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        vbox.addWidget(self.table)

        # 按钮区
        btn_box = QHBoxLayout()
        btn_box.setContentsMargins(20, 10, 20, 10)
        add_btn = PrimaryPushButton("＋ 新增")
        del_btn = QPushButton("－ 删除")
        save_btn = PrimaryPushButton("保存")
        btn_box.addWidget(add_btn)
        btn_box.addWidget(del_btn)
        btn_box.addStretch()
        btn_box.addWidget(save_btn)
        vbox.addLayout(btn_box)

        main.addWidget(content)
        add_btn.clicked.connect(self.add_row)
        del_btn.clicked.connect(self.delete_row)
        save_btn.clicked.connect(self.save_rules)

    def create_title_bar(self):
        bar = QWidget()
        bar.setFixedHeight(40)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(15, 0, 15, 0)
        lay.addWidget(QLabel("补贴互斥规则", objectName="titleLabel"))
        lay.addStretch()
        close_btn = QPushButton("×", objectName="closeBtn")
        close_btn.clicked.connect(self.close)
        lay.addWidget(close_btn)
        return bar

    def create_search_bar(self):
        hbox = QHBoxLayout()
        self.filter_a = QComboBox()
        self.filter_b = QComboBox()
        self.filter_rel = QComboBox()
        self.search_box = QLineEdit()

        self.filter_a.addItem("-- 全部 --")
        self.filter_b.addItem("-- 全部 --")
        self.filter_rel.addItems(["-- 全部 --", "互斥", "叠加"])
        for s in self.subsidies:
            self.filter_a.addItem(s["name"], s["id"])
            self.filter_b.addItem(s["name"], s["id"])

        self.search_box.setPlaceholderText("输入说明关键字搜索")

        hbox.addWidget(QLabel("补贴A:"))
        hbox.addWidget(self.filter_a)
        hbox.addWidget(QLabel("补贴B:"))
        hbox.addWidget(self.filter_b)
        hbox.addWidget(QLabel("关系:"))
        hbox.addWidget(self.filter_rel)
        hbox.addWidget(self.search_box)
        self.filter_a.currentTextChanged.connect(self.filter_table)
        self.filter_b.currentTextChanged.connect(self.filter_table)
        self.filter_rel.currentTextChanged.connect(self.filter_table)
        self.search_box.textChanged.connect(self.filter_table)
        return hbox

    # ---------------- 数据 ---------------- #
    def load_rules(self):
        file = Path("config/conflict_rules.json")
        self.rules = json.loads(file.read_text(encoding="utf-8")) if file.exists() else []
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.rules))
        for row, r in enumerate(self.rules):
            print(r)
            self.table.setItem(row, 0, QTableWidgetItem(self.name_by_id(r["a"])))
            self.table.setItem(row, 1, QTableWidgetItem(self.name_by_id(r["b"])))
            rel = {"conflict": "互斥", "stack": "叠加"}[r["rel"]]
            self.table.setItem(row, 2, QTableWidgetItem(rel))
            self.table.setItem(row, 3, QTableWidgetItem(r["desc"]))
            del_btn = QPushButton("删除")
            del_btn.clicked.connect(lambda _, r=row: self.delete_row(r))
            self.table.setCellWidget(row, 4, del_btn)

    def name_by_id(self, sid):
        return next((s["name"] for s in self.subsidies if s["id"] == sid), sid)

    def filter_table(self):
        a_id = self.filter_a.currentData()
        b_id = self.filter_b.currentData()
        rel_text = self.filter_rel.currentText()
        keyword = self.search_box.text().lower()
        for row, r in enumerate(self.rules):
            show = True
            if a_id and r["a"] != a_id:
                show = False
            if b_id and r["b"] != b_id:
                show = False
            if rel_text != "-- 全部 --":
                rel = {"conflict": "互斥", "stack": "叠加"}[r["rel"]]
                if rel != rel_text:
                    show = False
            if keyword and keyword not in r["desc"].lower():
                show = False
            self.table.setRowHidden(row, not show)

    def add_row(self):
        self.rules.append({"a": "", "b": "", "rel": "conflict", "desc": ""})
        self.refresh_table()

    def delete_row(self, row):
        self.rules.pop(row)
        self.refresh_table()

    def save_rules(self):
        Path("config").mkdir(exist_ok=True)
        Path("config/conflict_rules.json").write_text(
            json.dumps(self.rules, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        # 热加载
        try:
            from engine.rule_loader import RuleLoader
            RuleLoader.reload()
        except Exception:
            pass
        InfoBar.success("成功", "规则已保存并生效", parent=self, position=InfoBarPosition.TOP)

    # ---------------- 拖动 ---------------- #
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            
# class MainWindow(QMainWindow):
#     """主应用程序窗口"""
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("补贴管理系统")
#         self.resize(800, 600)
        
#         # 设置主题
        
#         # 创建中心部件
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
        
#         # 创建布局
#         layout = QVBoxLayout(central_widget)
#         layout.setAlignment(Qt.AlignCenter)
#         layout.setSpacing(30)
        
#         # 添加标题
#         title = QLabel("补贴管理系统")
#         title.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
#         title.setStyleSheet("color: #2b579a;")
#         title.setAlignment(Qt.AlignCenter)
#         layout.addWidget(title)
        
#         # 添加说明
#         description = QLabel("高效管理各类农业补贴项目")
#         description.setFont(QFont("Microsoft YaHei", 14))
#         description.setAlignment(Qt.AlignCenter)
#         layout.addWidget(description)
        
#         # 添加按钮
#         self.create_btn = PrimaryPushButton("创建补贴类型")
#         self.create_btn.setFixedSize(200, 50)
#         self.create_btn.clicked.connect(self.open_popup)
#         layout.addWidget(self.create_btn, alignment=Qt.AlignCenter)
        
#         # 添加底部信息
#         footer = QLabel("© 2023 补贴管理系统 | 版本 1.0.0")
#         footer.setAlignment(Qt.AlignCenter)
#         footer.setStyleSheet("color: gray; font-size: 12px;")
#         layout.addWidget(footer, alignment=Qt.AlignBottom)
    
#     def open_popup(self):
#         """打开弹出窗口"""
#         self.popup = ConflictRulePage(self)
#         self.popup.show()
        
#         # 居中显示
#         self.center_popup()
    
#     def center_popup(self):
#         """居中弹出窗口"""
#         # 计算主窗口中心位置
#         main_geo = self.geometry()
#         main_center = main_geo.center()
        
#         # 计算弹出窗口位置
#         popup_geo = self.popup.geometry()
#         popup_geo.moveCenter(main_center)
        
#         self.popup.move(popup_geo.topLeft())


# if __name__ == "__main__":
#     app = QApplication()
#     app.setStyle("Fusion")  # 使用Fusion样式确保跨平台一致性
    
#     # 设置应用程序字体
#     font = QFont("Microsoft YaHei", 10)
#     app.setFont(font)
    
#     window = MainWindow()
#     window.show()
#     app.exec()
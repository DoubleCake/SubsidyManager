# ui/rule_table_page.py
import json
from pathlib import Path
from typing import List, Dict

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QHeaderView, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QFrame, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QAbstractItemView
)
from qfluentwidgets import (
    PrimaryPushButton, InfoBar, InfoBarPosition, TitleLabel, BodyLabel
)
from services.subsidy_service import SubsidyService


class RuleTablePage(QWidget):
    """补贴规则独立页面（可拖动 + 表格 + 搜索）"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = SubsidyService()
        self.subsidies = self.service.get_all_subsidies(active_only=True)
        self.setWindowTitle("补贴互斥规则")
        self.resize(780, 550)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.drag_position = QPoint()
        self.build_ui()
        self.load_data()
    # ---------- 外观框架 ----------
    def build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(10, 10, 10, 10)

        content = QWidget()
        content.setObjectName("content")
        content.setStyleSheet("""
            #content{background-color:white;border-radius:8px;}
            QLabel#titleLabel{color:white;font-size:14px;font-weight:bold;}
            QPushButton#closeBtn{background:transparent;color:white;font-size:20px;border:none;width:30px;}
            QPushButton#closeBtn:hover{background:#e81123;}
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
        self.table.setHorizontalHeaderLabels(["ID", "规则名称", "补贴A", "补贴B", "关系"])
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

    # ---------- 标题栏 ----------
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

    # ---------- 搜索 ----------
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
        self.search_box.setPlaceholderText("搜索规则名称/说明")

        self.filter_a.currentTextChanged.connect(self.filter_table)
        self.filter_b.currentTextChanged.connect(self.filter_table)
        self.filter_rel.currentTextChanged.connect(self.filter_table)
        self.search_box.textChanged.connect(self.filter_table)
        return hbox

    # ---------- 数据 ----------
    def load_data(self):
        self.rules = self.service.list_rules()
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.rules))
        for row, r in enumerate(self.rules):
            self.table.setItem(row, 0, QTableWidgetItem(str(r["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(r["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(r["subsidy_a_id"]))
            self.table.setItem(row, 3, QTableWidgetItem(r["subsidy_b_id"]))
            rel = {"conflict": "互斥", "stack": "叠加"}[r["relation"]]
            self.table.setItem(row, 4, QTableWidgetItem(rel))
            del_btn = QPushButton("删除")
            del_btn.clicked.connect(lambda _, rid=r["id"]: self.delete_row(rid))
            self.table.setCellWidget(row, 4, del_btn)

    def filter_table(self):
        a_id = self.filter_a.currentData()
        b_id = self.filter_b.currentData()
        rel_text = self.filter_rel.currentText()
        keyword = self.search_box.text().lower()
        for row, r in enumerate(self.rules):
            show = True
            if a_id and r["subsidy_a_id"] != a_id:
                show = False
            if b_id and r["subsidy_b_id"] != b_id:
                show = False
            if rel_text != "-- 全部 --" and r["relation"] != rel_text.lower():
                show = False
            if keyword and keyword not in r["name"].lower() + r["description"].lower():
                show = False
            self.table.setRowHidden(row, not show)

    def add_row(self):
        self.rules.append({"name": "", "subsidy_a_id": "", "subsidy_b_id": "", "relation": "conflict", "description": ""})
        self.refresh_table()

    def delete_row(self, rule_id):
        self.service.delete_rule(rule_id)
        self.load_data()

    def save_rules(self):
        # 表格 → 数据库
        for row in range(self.table.rowCount()):
            data = {
                "name": self.table.item(row, 1).text(),
                "subsidy_a_id": self.table.item(row, 2).text(),
                "subsidy_b_id": self.table.item(row, 3).text(),
                "relation": "conflict" if self.table.item(row, 4).text() == "互斥" else "stack",
                "description": ""  # 可扩展
            }
            if self.table.item(row, 0).text():
                # 更新
                self.service.update_rule(int(self.table.item(row, 0).text()), **data)
            else:
                # 新增
                self.service.add_rule(**data)

        InfoBar.success("成功", "规则已保存", parent=self, position=InfoBarPosition.TOP)
        self.load_data()

    # ---------- 拖动 ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
# ui/matrix_rule_widget.py
from PySide6.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                               QHeaderView, QVBoxLayout, QPushButton)
from PySide6.QtCore import Qt
import json
from pathlib import Path

class MatrixRuleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_matrix()

    def init_ui(self):
        vbox = QVBoxLayout(self)
        self.table = QTableWidget()
        vbox.addWidget(self.table)

        # 底部按钮
        save_btn = QPushButton("保存并热加载")
        save_btn.clicked.connect(self.save_matrix)
        vbox.addWidget(save_btn)

    def load_matrix(self):
        # 1. 读取补贴列表
        rules_file = Path("config/subsidy_rules.json")
        if not rules_file.exists():
            self.subsidies = []
            return
        self.subsidies = json.loads(rules_file.read_text(encoding="utf-8"))

        names = [s["name"] for s in self.subsidies]
        self.table.setColumnCount(len(names))
        self.table.setRowCount(len(names))
        self.table.setHorizontalHeaderLabels(names)
        self.table.setVerticalHeaderLabels(names)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 2. 读取矩阵规则
        matrix_file = Path("config/matrix_rules.json")
        matrix = json.loads(matrix_file.read_text(encoding="utf-8")).get("matrix", {}) \
                 if matrix_file.exists() else {}

        # 3. 填充单元格
        for r, row_sub in enumerate(self.subsidies):
            for c, col_sub in enumerate(self.subsidies):
                if r == c:  # 对角线
                    item = QTableWidgetItem("—")
                    item.setFlags(Qt.NoItemFlags)
                else:
                    state = matrix.get(row_sub["id"], {}).get(col_sub["id"], "")
                    text = {"conflict": "❌", "stack": "✅"}.get(state, "")
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(r, c, item)

    def save_matrix(self):
        """把表格写回 JSON 并热加载"""
        matrix = {}
        for r, row_sub in enumerate(self.subsidies):
            for c, col_sub in enumerate(self.subsidies):
                if r == c:
                    continue
                cell = self.table.item(r, c).text()
                state = {"❌": "conflict", "✅": "stack"}.get(cell, "")
                if state:
                    matrix.setdefault(row_sub["id"], {})[col_sub["id"]] = state

        Path("config").mkdir(exist_ok=True)
        Path("config/matrix_rules.json").write_text(
            json.dumps({"matrix": matrix}, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        # 立即热加载
        from engine.rule_loader import RuleLoader
        RuleLoader.reload()
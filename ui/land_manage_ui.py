from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget,
    QPushButton, QLineEdit, QHBoxLayout, QTableWidgetItem,
    QMenu, QAction, QDialog, QFormLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from services import LandService

class LandManageUI(QWidget):
    def __init__(self):
        super().__init__()
        self.subsidy_service = LandService()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("补贴管理")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # 搜索框和添加按钮
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入补贴名称搜索")
        self.search_input.textChanged.connect(self.load_table_data)
        search_layout.addWidget(self.search_input)

        add_btn = QPushButton("新增补贴类型")
        add_btn.clicked.connect(self.show_add_dialog)
        search_layout.addWidget(add_btn)

        layout.addLayout(search_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "补贴名称", "金额", "频率", "状态", "操作"])
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_table_data()

    def load_table_data(self, keyword=""):
        subsidies = self.subsidy_service.search_subsidies(name=keyword)

        self.table.setRowCount(len(subsidies))
        for row, subsidy in enumerate(subsidies):
            data = [
                subsidy["id"],
                subsidy["name"],
                f"{subsidy['amount']} 元",
                subsidy["frequency"],
                subsidy["status"]
            ]
            for col, value in enumerate(data):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda _, s_id=subsidy["id"]: self.show_edit_dialog(s_id))
            self.table.setCellWidget(row, 5, edit_btn)

    def show_context_menu(self, position):
        indexes = self.table.selectedIndexes()
        if len(indexes) > 0:
            menu = QMenu()
            delete_action = menu.addAction("删除补贴类型")
            action = menu.exec_(self.table.viewport().mapToGlobal(position))

            if action == delete_action:
                selected_row = indexes[0].row()
                subsidy_id = self.table.item(selected_row, 0).text()
                self.delete_subsidy(subsidy_id)

    def delete_subsidy(self, subsidy_id):
        reply = QMessageBox.question(self, '确认', "确定要删除该补贴类型吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success = self.subsidy_service.delete_subsidy(subsidy_id)
            if success:
                self.load_table_data()
            else:
                QMessageBox.warning(self, "错误", "删除失败，请检查是否有关联数据。")

    def show_add_dialog(self):
        dialog = SubsidyEditDialog(self.subsidy_service)
        if dialog.exec_():
            self.load_table_data()

    def show_edit_dialog(self, subsidy_id):
        subsidy = self.subsidy_service.get_subsidy(subsidy_id)
        dialog = SubsidyEditDialog(self.subsidy_service, subsidy)
        if dialog.exec_():
            self.load_table_data()

    def __init__(self, service, subsidy=None):
        super().__init__()
        self.service = service
        self.subsidy = subsidy
        self.setWindowTitle("新增/编辑补贴类型")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["每月", "每季度", "每年"])
        self.status_combo = QComboBox()
        self.status_combo.addItems(["启用", "停用"])

        if self.subsidy:
            self.name_input.setText(self.subsidy["name"])
            self.amount_input.setText(str(self.subsidy["amount"]))
            self.frequency_combo.setCurrentText(self.subsidy["frequency"])
            self.status_combo.setCurrentText(self.subsidy["status"])

        form_layout.addRow("补贴名称：", self.name_input)
        form_layout.addRow("金额（元）：", self.amount_input)
        form_layout.addRow("发放频率：", self.frequency_combo)
        form_layout.addRow("状态：", self.status_combo)

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save)

        layout.addLayout(form_layout)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save(self):
        name = self.name_input.text()
        try:
            amount = float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的金额！")
            return

        frequency = self.frequency_combo.currentText()
        status = self.status_combo.currentText()

        if not name:
            QMessageBox.warning(self, "错误", "补贴名称不能为空！")
            return

        if self.subsidy:
            success = self.service.update_subsidy(
                self.subsidy["id"], name=name, amount=amount,
                frequency=frequency, status=status
            )
        else:
            success = self.service.add_subsidy(
                name=name, amount=amount,
                frequency=frequency, status=status
            )

        if success:
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "保存失败，请重试。")
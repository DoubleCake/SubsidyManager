

from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, FluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont, InfoBadge,
                            InfoBadgePosition, FluentBackgroundTheme)
from qfluentwidgets import FluentIcon as FIF
from services import PersonService


class PersonManageUI(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.service = PersonService()
        self.setObjectName("PersonManageUI")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("人员补贴管理")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # 搜索框和添加按钮
        search_layout = QHBoxLayout()
        self.search_input = LineEdit()
        self.search_input.setPlaceholderText("输入补贴名称搜索")
        self.search_input.textChanged.connect(self.load_table_data)
        search_layout.addWidget(self.search_input, stretch=1)

        add_btn = PrimaryPushButton("新增补贴类型", self)
        add_btn.clicked.connect(self.show_add_dialog)
        search_layout.addWidget(add_btn)

        layout.addLayout(search_layout)

        # 表格
        self.table = TableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "补贴名称", "金额", "频率", "状态", "操作"])
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.table)

        self.load_table_data()

    def load_table_data(self, keyword=""):
        subsidies = self.service.search_subsidies(name=keyword)

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

            edit_btn = PushButton("编辑")
            edit_btn.clicked.connect(lambda _, s_id=subsidy["id"]: self.show_edit_dialog(s_id))
            self.table.setCellWidget(row, 5, edit_btn)

    def show_context_menu(self, position):
        indexes = self.table.selectedIndexes()
        if len(indexes) > 0:
            menu = MessageBox("操作", "请选择操作", self)
            delete_btn = menu.addButton("删除补贴类型")
            menu.exec_()
            if menu.clickedButton() == delete_btn:
                selected_row = indexes[0].row()
                subsidy_id = self.table.item(selected_row, 0).text()
                self.delete_subsidy(subsidy_id)

    def delete_subsidy(self, subsidy_id):
        result = MessageBox("确认", "确定要删除该补贴类型吗？", self).exec_()
        if result:
            success = self.service.delete_subsidy(subsidy_id)
            if success:
                self.load_table_data()
            else:
                MessageBox("错误", "删除失败，请检查是否有关联数据。", self).exec_()

    def show_add_dialog(self):
        dialog = SubsidyEditDialog(self.service, parent=self)
        if dialog.exec():
            self.load_table_data()

    def show_edit_dialog(self, subsidy_id):
        subsidy = self.service.get_subsidy(subsidy_id)
        dialog = SubsidyEditDialog(self.service, subsidy=subsidy, parent=self)
        if dialog.exec():
            self.load_table_data()


class SubsidyEditDialog(Dialog):
    def __init__(self, service, subsidy=None, parent=None):
        title = "新增补贴类型" if subsidy is None else "编辑补贴类型"
        super().__init__(title, parent)
        self.service = service
        self.subsidy = subsidy
        self.init_ui()
        if subsidy:
            self.load_data(subsidy)

    def init_ui(self):
        form_layout = QFormLayout()

        self.name_input = LineEdit()
        self.amount_input = LineEdit()
        self.frequency_combo = ComboBox()
        self.status_combo = ComboBox()

        self.frequency_combo.addItems(["每月", "每季度", "每年"])
        self.status_combo.addItems(["启用", "停用"])

        form_layout.addRow("补贴名称：", self.name_input)
        form_layout.addRow("金额（元）：", self.amount_input)
        form_layout.addRow("发放频率：", self.frequency_combo)
        form_layout.addRow("状态：", self.status_combo)

        self.addContent(form_layout)

        self.yesButton.setText("保存")
        self.cancelButton.setText("取消")

    def load_data(self, subsidy):
        self.name_input.setText(subsidy["name"])
        self.amount_input.setText(str(subsidy["amount"]))
        self.frequency_combo.setCurrentText(subsidy["frequency"])
        self.status_combo.setCurrentText(subsidy["status"])

    def done(self, result):
        if result == Dialog.Accepted:
            name = self.name_input.text()
            try:
                amount = float(self.amount_input.text())
            except ValueError:
                MessageBox("错误", "请输入有效的金额！", self).exec_()
                return

            frequency = self.frequency_combo.currentText()
            status = self.status_combo.currentText()

            if not name:
                MessageBox("错误", "补贴名称不能为空！", self).exec_()
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
                super().done(result)
            else:
                MessageBox("错误", "保存失败，请重试。", self).exec_()
        else:
            super().done(result)
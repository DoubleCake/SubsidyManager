# ui/subsidy_record_ui.py

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu
from qfluentwidgets import (
    SubInterface, TableWidget, PushButton, LineEdit, MessageBox,
    Dialog, ComboBox, PrimaryPushButton, DatePicker
)
from services.record_service import RecordService


class SubsidyRecordUI(SubInterface):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.service = RecordService()
        self.setObjectName("SubsidyRecordUI")

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 搜索区域
        search_layout = QHBoxLayout()

        self.family_combo = ComboBox()
        self.subsidy_combo = ComboBox()
        self.search_btn = PushButton("搜索", self, FIF.SEARCH)
        self.reset_btn = PushButton("重置", self, FIF.CANCEL)

        self.load_combos()

        search_layout.addWidget(QLabel("家庭："))
        search_layout.addWidget(self.family_combo, 1)
        search_layout.addWidget(QLabel("补贴类型："))
        search_layout.addWidget(self.subsidy_combo, 1)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.reset_btn)

        layout.addLayout(search_layout)

        # 表格
        self.table = TableWidget(self)
        self.table.setWordWrap(False)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "家庭", "补贴类型", "金额", "发放日期"
        ])
        self.table.setSortingEnabled(True)

        layout.addWidget(self.table)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.add_btn = PushButton("新增", self, FIF.ADD)
        self.edit_btn = PushButton("编辑", self, FIF.EDIT)
        self.del_btn = PushButton("删除", self, FIF.DELETE)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.del_btn)

        layout.addLayout(btn_layout)

        # 绑定事件
        self.search_btn.clicked.connect(self.on_search)
        self.reset_btn.clicked.connect(self.on_reset)
        self.add_btn.clicked.connect(self.show_add_dialog)
        self.edit_btn.clicked.connect(self.show_edit_dialog)
        self.del_btn.clicked.connect(self.delete_selected_record)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

    def load_combos(self):
        families = self.service.get_all_families()
        subsidies = self.service.get_all_subsidies()

        self.family_combo.clear()
        self.subsidy_combo.clear()

        self.family_combo.addItem("全部", None)
        for f in families:
            self.family_combo.addItem(f["户主姓名"], f["id"])

        self.subsidy_combo.addItem("全部", None)
        for s in subsidies:
            self.subsidy_combo.addItem(s["名称"], s["id"])

    def load_data(self, family_id=None, subsidy_id=None):
        data = self.service.search_records(family_id, subsidy_id)
        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(item['家庭']))
            self.table.setItem(row, 2, QTableWidgetItem(item['补贴类型']))
            self.table.setItem(row, 3, QTableWidgetItem(str(item['金额']) + " 元"))
            self.table.setItem(row, 4, QTableWidgetItem(item['发放日期']))

    def on_search(self):
        family_id = self.family_combo.currentData()
        subsidy_id = self.subsidy_combo.currentData()
        self.load_data(family_id, subsidy_id)

    def on_reset(self):
        self.family_combo.setCurrentIndex(0)
        self.subsidy_combo.setCurrentIndex(0)
        self.load_data()

    def show_add_dialog(self):
        dialog = RecordEditDialog(self)
        if dialog.exec():
            self.load_data()

    def show_edit_dialog(self):
        selected = self.table.selectedItems()
        if not selected:
            MessageBox("提示", "请先选择一行进行编辑", self).exec_()
            return
        record_id = int(selected[0].text())
        dialog = RecordEditDialog(self, record_id)
        if dialog.exec():
            self.load_data()

    def delete_selected_record(self):
        selected = self.table.selectedItems()
        if not selected:
            MessageBox("提示", "请先选择一行进行删除", self).exec_()
            return
        record_id = int(selected[0].text())
        reply = MessageBox("确认", "确定要删除该记录？", self)
        if reply.exec_():
            if self.service.delete_record(record_id):
                MessageBox("成功", "删除成功", self).exec_()
                self.load_data()
            else:
                MessageBox("错误", "删除失败", self).exec_()

    def show_context_menu(self, position):
        menu = QMenu(self)
        edit_action = menu.addAction("编辑")
        del_action = menu.addAction("删除")
        action = menu.exec_(self.table.mapToGlobal(position))
        if action == edit_action:
            self.show_edit_dialog()
        elif action == del_action:
            self.delete_selected_record()


class RecordEditDialog(Dialog):
    def __init__(self, parent=None, record_id=None):
        super().__init__("新增补贴记录", parent)
        self.record_id = record_id
        self.service = RecordService()
        self.init_ui()
        if record_id is not None:
            self.load_data(record_id)

    def init_ui(self):
        self.family_combo = ComboBox()
        self.subsidy_combo = ComboBox()
        self.amount_input = LineEdit()
        self.date_picker = DatePicker()

        self.load_combos()

        self.addContent("家庭：", self.family_combo)
        self.addContent("补贴类型：", self.subsidy_combo)
        self.addContent("金额（元）：", self.amount_input)
        self.addContent("发放日期：", self.date_picker)

        self.yesButton.setText("保存")
        self.cancelButton.setText("取消")

    def load_combos(self):
        families = self.service.get_all_families()
        subsidies = self.service.get_all_subsidies()

        for f in families:
            self.family_combo.addItem(f["户主姓名"], f["id"])
        for s in subsidies:
            self.subsidy_combo.addItem(s["名称"], s["id"])

    def load_data(self, record_id):
        data = self.service.get_all_records()
        record = next((item for item in data if item['id'] == record_id), None)
        if record:
            self.family_combo.setCurrentText(record['家庭'])
            self.subsidy_combo.setCurrentText(record['补贴类型'])
            self.amount_input.setText(str(record['金额']))
            self.date_picker.setDate(record['发放日期'])

    def done(self, result):
        if result == Dialog.Accepted:
            family_id = self.family_combo.currentData()
            subsidy_id = self.subsidy_combo.currentData()
            amount = float(self.amount_input.text()) if self.amount_input.text() else 0.0
            date = self.date_picker.text()

            if not family_id or not subsidy_id:
                MessageBox("错误", "请选择家庭和补贴类型", self).exec_()
                return

            if self.record_id is None:
                success = self.service.add_record(
                    家庭=family_id,
                    补贴类型=subsidy_id,
                    金额=amount,
                    发放日期=date
                )
            else:
                success = self.service.update_record(
                    self.record_id,
                    家庭=family_id,
                    补贴类型=subsidy_id,
                    金额=amount,
                    发放日期=date
                )

            if success:
                MessageBox("成功", "保存成功", self).exec_()
                super().done(result)
            else:
                MessageBox("错误", "保存失败", self).exec_()
        else:
            super().done(result)
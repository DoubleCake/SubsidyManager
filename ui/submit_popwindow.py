from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

from qfluentwidgets import (
    MessageBoxBase,
    SubtitleLabel,
    LineEdit,
    PrimaryPushButton,
    CaptionLabel,
    PushButton,
    MessageBox,
    ComboBox, PrimaryPushButton, DatePicker
)
from services.record_service import RecordService

class SubsidyTypeMessageBox(MessageBoxBase):
    def __init__(self, parent=None, subsidy_id=None):
        super().__init__(parent)
        self.service = RecordService()

        self.titleLabel = SubtitleLabel("补贴类型管理", self)
        self.subsidy_id = subsidy_id
        # 创建输入控件
        self.name_edit = LineEdit()
        self.code_edit = LineEdit()
        self.land_req_edit = LineEdit()

        self.name_edit.setPlaceholderText("请输入补贴名称")
        self.code_edit.setPlaceholderText("请输入唯一编码")
        self.land_req_edit.setPlaceholderText("请输入土地要求")

        self.name_edit.setMinimumHeight(40)
        self.code_edit.setMinimumHeight(40)
        self.land_req_edit.setMinimumHeight(40)

        # 错误提示标签
        self.error_label = CaptionLabel("名称或编码不能为空")
        self.error_label.setTextColor("#cf1010", Qt.red)
        self.error_label.hide()

        # 初始化按钮
        self.save_button = PrimaryPushButton("保存")
        self.cancel_button = PushButton("取消")

        self.yesButton = self.save_button
        self.cancelButton = self.cancel_button

        # 连接点击事件（注意：不是直接 connect 到 clicked）
        self.save_button.clicked.connect(self.onSaveClicked)
        # 布局设置
        self.init_ui()
        # 设置窗口大小
        self.resize(700, 600)

        # 设置标题
        title = "编辑补贴类型" if subsidy_id else "新建补贴类型"
        self.titleLabel.setText(title)

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

    def validate(self):
        name = self.name_edit.text().strip()
        code = self.code_edit.text().strip()

        print(f"🔍 [validate] 名称: '{name}', 编码: '{code}'")

        name_valid = bool(name)
        code_valid = bool(code)

        is_valid = name_valid and code_valid
        self.error_label.setHidden(is_valid)
        return is_valid



    def onSaveClicked(self):
        """当用户点击保存按钮时触发"""
        print("✅ 开始保存数据...")
        if not self.validate():
            print("❌ 数据不合法，未保存")
            return

        print("✅ 数据合法，正在保存")
        data = {
            "name": self.name_edit.text(),
            "code": self.code_edit.text(),
            "land_requirement": self.land_req_edit.text(),
        }
        print("保存内容:", data)
        
    def done(self, result):
        #   # 关闭对话框并返回 Accepted
        if result == self.accept():
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
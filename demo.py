from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from qfluentwidgets import (
    MessageBoxBase,
    SubtitleLabel,
    LineEdit,
    PrimaryPushButton,
    CaptionLabel,
    PushButton
)
import logging
logging.basicConfig(filename='app.log', level=logging.INFO)

class SubsidyTypeMessageBox(MessageBoxBase):
    def __init__(self, parent=None, subsidy_id=None):
        super().__init__(parent)

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
        self.setup_ui()

        # 设置窗口大小
        self.resize(700, 600)

        # 设置标题
        title = "编辑补贴类型" if subsidy_id else "新建补贴类型"
        self.titleLabel.setText(title)

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.titleLabel.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.titleLabel)

        main_layout.addWidget(QLabel("名称*:"))
        main_layout.addWidget(self.name_edit)

        main_layout.addWidget(QLabel("编码*:"))
        main_layout.addWidget(self.code_edit)

        main_layout.addWidget(QLabel("土地要求:"))
        main_layout.addWidget(self.land_req_edit)

        main_layout.addWidget(self.error_label)

        self.viewLayout.addLayout(main_layout)

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
        logging.warning("onSaveClicked 被调用了！")
        logging.getLogger().handlers[0].flush()  # 强制刷新缓冲
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

        self.accept()  # 关闭对话框并返回 Accepted


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("补贴管理系统")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        btn = QPushButton("打开补贴配置窗口")
        btn.clicked.connect(self.open_dialog)
        layout.addWidget(btn)

        self.setLayout(layout)

    def open_dialog(self):
        dialog = SubsidyTypeMessageBox(self)
        if dialog.exec():
            print("✅ 用户点击了【保存】并成功提交数据")
            
        else:
            print("❌ 用户取消操作或关闭窗口")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
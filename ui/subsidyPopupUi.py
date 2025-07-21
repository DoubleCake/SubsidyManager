import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QPushButton, QFrame, QLineEdit, QSpinBox, QDoubleSpinBox,
                              QCheckBox, QDateEdit, QComboBox)
from PySide6.QtCore import Qt, QDate, QPoint
from PySide6.QtGui import QFont, QMouseEvent, QColor, QPainter, QPen, QBrush
from qfluentwidgets import (PrimaryPushButton, setTheme, Theme, BodyLabel, TitleLabel,
                           InfoBar, InfoBarPosition)

from services import SubsidyService

class DraggableWidget(QWidget):
    """可拖动的自定义窗口部件"""
    def __init__(self, title="弹出窗口", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(500, 600)
        
        # 设置窗口标志
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 存储鼠标位置用于拖动
        self.drag_position = QPoint()
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)
        
        # 创建内容区域（带圆角和阴影）
        self.content_widget = QWidget()
        self.content_widget.setObjectName("contentWidget")
        self.content_widget.setStyleSheet("""
            #contentWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(self.content_widget)
        
        # 创建内容布局
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # 创建标题栏
        self.create_title_bar()
        
        # 设置主题
        setTheme(Theme.LIGHT)
    
    def create_title_bar(self):
        """创建自定义标题栏"""
        # 标题栏部件
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            #titleBar {
                background-color: #2b579a;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 0 15px;
            }
            QLabel#titleLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        # 标题栏布局
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)
        
        # 标题文本
        title_label = QLabel(self.windowTitle())
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        
        # 添加弹性空间
        title_layout.addStretch(1)
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 20px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e81123;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)
        
        # 将标题栏添加到内容布局
        self.content_layout.addWidget(title_bar)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件 - 开始拖动"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件 - 拖动窗口"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def paintEvent(self, event):
        """绘制阴影效果"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制阴影
        pen = QPen(QColor(0, 0, 0, 50))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # 绘制圆角矩形阴影
        painter.setBrush(QBrush(QColor(0, 0, 0, 20)))
        painter.drawRoundedRect(5, 5, self.width()-10, self.height()-10, 8, 8)
        
        # 绘制内容区域
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(10, 10, self.width()-20, self.height()-20, 8, 8)
        
        painter.end()


class SubsidyPopup(DraggableWidget):
    """补贴类型管理弹出窗口"""
    def __init__(self, parent=None):
        super().__init__("创建新的补贴", parent)
        self.setup_ui()
        self.service = SubsidyService()
    
    def setup_ui(self):
        # 创建表单布局
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加标题
        title_label = TitleLabel("补贴类型详细信息")
        title_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title_label)
        
        # 添加分隔线
        form_layout.addWidget(self.create_h_line())
        
        # 1. 基本信息部分
        form_layout.addWidget(BodyLabel("基本信息", self))
        
        # 名称
        form_layout.addWidget(QLabel("名称*:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入补贴名称")
        form_layout.addWidget(self.name_edit)
        
        # 2. 金额设置部分
        form_layout.addWidget(self.create_h_line())
        form_layout.addWidget(BodyLabel("金额设置", self))
        
 
        # 金额输入
        amount_layout = QHBoxLayout()
        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("输入金额，例如：1000")
        amount_layout.addWidget(self.amount_edit)
        self.sub_danwei = QComboBox()
        self.sub_danwei.addItems(["元/亩", "固定金额", "元/单位"])
        amount_layout.addWidget(self.sub_danwei)
        amount_layout.addStretch()
        form_layout.addLayout(amount_layout)

        # 3. 规则设置部分
        form_layout.addWidget(self.create_h_line())
        form_layout.addWidget(BodyLabel("规则设置", self))
        # 互斥设置
        self.mutual_exclusive_check = QCheckBox("与其他补贴互斥")
        form_layout.addWidget(self.mutual_exclusive_check)

        # 土地要求
        form_layout.addWidget(QLabel("种植用地的属性:"))
        self.land_com = QComboBox()
        self.land_com.addItems(["承包地", "自留地","林地","耕地"])
        form_layout.addWidget(self.land_com)

        # 4. 时间设置部分
        form_layout.addWidget(self.create_h_line())
        form_layout.addWidget(BodyLabel("补贴针对的时间区域", self))
        # 日期范围
        date_layout = QHBoxLayout()
        date_layout.setSpacing(10)
        date_layout.addWidget(QLabel("开始日期:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(self.start_date_edit)
        
        date_layout.addWidget(QLabel("结束日期:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate().addMonths(3))
        date_layout.addWidget(self.end_date_edit)
        
        form_layout.addLayout(date_layout)
        
        # 5. 状态设置
        form_layout.addWidget(self.create_h_line())
        self.active_check = QCheckBox("激活此补贴")
        self.active_check.setChecked(True)
        form_layout.addWidget(self.active_check)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 20, 0, 0)
        button_layout.setSpacing(15)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setStyleSheet("""
            #cancelButton {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            #cancelButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch(1)
        
        self.save_btn = PrimaryPushButton("保存补贴")
        self.save_btn.clicked.connect(self.save_subsidy)
        button_layout.addWidget(self.save_btn)
        
        form_layout.addLayout(button_layout)
        
        # 将表单添加到内容布局
        self.content_layout.addLayout(form_layout)
    
    def create_h_line(self):
        """创建水平分隔线"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #e0e0e0;")
        line.setFixedHeight(1)
        return line
    
    def save_subsidy(self):
        """保存补贴类型数据"""
        # 验证必填字段
        if not self.name_edit.text().strip():
            self.show_message("错误", "补贴名称不能为空", "error")
            return

        # 收集数据
        data = {
            "name": self.name_edit.text().strip(),
            "year": self.year_spinbox.value(),
            "amount_type": 1 if self.amount_type_combo.currentText() == "按亩发放" else 0,
            "unit_amount": self.amount_edit.value(),
            "is_mutual_exclusive": self.mutual_exclusive_check.isChecked(),
            "allow_multiple": self.allow_multiple_check.isChecked(),
            "land_requirement": self.land_req_edit.text(),
            "start_date": self.start_date_edit.date(),
            "end_date": self.end_date_edit.date(),
            "is_active": self.active_check.isChecked(),
            # 添加缺失的字段
            "code": self.generate_code(),  # 需要实现生成代码的方法
            "conflict_id": self.get_selected_conflict_id()  # 需要实现获取冲突ID的方法
        }
        
        try:
            # 根据是新增还是编辑调用不同方法
            if self.is_editing:  # 假设有标识是否编辑的状态
                result = service.update_subsidy_type(self.current_subsidy_id, data)
            else:
                result = service.create_subsidy_type(data)
                
            if result:
                self.show_message("成功", "补贴类型已保存", "success")
                self.subsidy_saved.emit()  # 发送保存成功的信号
                self.close()
        except Exception as e:
            self.show_message("错误", f"保存失败: {str(e)}", "error")

    def show_message(self, title, content, type="info"):
        """显示消息提示"""
        if type == "success":
            InfoBar.success(title, content, parent=self, duration=2000, position=InfoBarPosition.TOP)
        elif type == "error":
            InfoBar.error(title, content, parent=self, duration=3000, position=InfoBarPosition.TOP)
        else:
            InfoBar.info(title, content, parent=self, duration=1500, position=InfoBarPosition.TOP)

# class MainWindow(QMainWindow):
#     """主应用程序窗口"""
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("补贴管理系统")
#         self.resize(800, 600)
        
#         # 设置主题
#         setTheme(Theme.LIGHT)
        
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
#         self.popup = SubsidyPopup(self)
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 使用Fusion样式确保跨平台一致性
    
    # 设置应用程序字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
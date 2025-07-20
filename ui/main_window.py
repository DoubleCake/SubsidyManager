import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QLineEdit, QPushButton, QFrame, QStackedWidget)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap
from qfluentwidgets import (MSFluentWindow, NavigationItemPosition, setTheme, Theme,
                           PrimaryPushButton, LineEdit, InfoBar, InfoBarPosition,
                           BodyLabel, TitleLabel, FluentIcon, setThemeColor)
class SimpleCardWidget(CardWidget):
    """ Simple card widget """

    def __init__(self, parent=None):
        super().__init__(parent)

    def _normalBackgroundColor(self):
        return QColor(255, 255, 255, 13 if isDarkTheme() else 170)

    def _hoverBackgroundColor(self):
        return self._normalBackgroundColor()

    def _pressedBackgroundColor(self):
        return self._normalBackgroundColor()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setBrush(self.backgroundColor)

        if isDarkTheme():
            painter.setPen(QColor(0, 0, 0, 48))
        else:
            painter.setPen(QColor(0, 0, 0, 12))

        r = self.borderRadius
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), r, r)


class MainWindow(MSFluentWindow):
    """主应用程序窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("补贴管理系统")
        self.resize(1200, 800)
        
        # 设置主题
        setTheme(Theme.LIGHT)
        setThemeColor("#2b579a")  # 设置主题色为蓝色
        
        # 创建子界面
        self.home_interface = self.create_home_interface()
        self.subsidy_interface = self.create_subsidy_interface()
        self.family_interface = self.create_family_interface()
        # self.report_interface = self.create_report_interface()
        # self.setting_interface = self.create_setting_interface()
        
        # 添加导航项
        self.addSubInterface(self.home_interface, FluentIcon.HOME, "首页")
        self.addSubInterface(self.subsidy_interface, FluentIcon.TAG, "补贴管理")
        self.addSubInterface(self.family_interface, FluentIcon.PEOPLE, "家庭管理")
        # self.addSubInterface(self.report_interface, FluentIcon.CHART, "报表统计")
        
        # 添加设置界面到导航栏底部
        # self.addSubInterface(self.setting_interface, FluentIcon.SETTING, "系统设置", NavigationItemPosition.BOTTOM)
        
        # 设置初始页面
        self.switchTo(self.home_interface)
        
        # 添加导航栏标题
        self.navigationInterface.setObjectName("navigationInterface")
        self.setStyleSheet("#navigationInterface { border-right: 1px solid #e0e0e0; }")
    
    def create_home_interface(self):
        """创建首页界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)
        widget.setObjectName("homeInterface")
        
        # 添加欢迎标题
        welcome_label = TitleLabel("欢迎使用补贴管理系统")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)
        
        # 添加系统概览
        overview_frame = QFrame()
        overview_frame.setObjectName("overviewFrame")
        overview_frame.setStyleSheet("""
            #overviewFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        overview_layout = QVBoxLayout(overview_frame)
        overview_layout.setContentsMargins(20, 20, 20, 20)
        overview_layout.setSpacing(20)
        
        # 概览标题
        overview_title = BodyLabel("系统概览")
        overview_title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        overview_layout.addWidget(overview_title)
        
        # 统计卡片
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # 补贴类型卡片
        subsidy_card = self.create_stat_card("补贴类型", "28", FluentIcon.TAG, "#2b579a")
        stats_layout.addWidget(subsidy_card)
        
        # 家庭数量卡片
        family_card = self.create_stat_card("家庭数量", "156", FluentIcon.PEOPLE, "#e76c24")
        stats_layout.addWidget(family_card)
        
        # 待审核申请卡片
        pending_card = self.create_stat_card("待审核申请", "12", FluentIcon.CALENDAR, "#d13438")
        stats_layout.addWidget(pending_card)
        
        overview_layout.addLayout(stats_layout)
        
        layout.addWidget(overview_frame)
        
        # 添加快速操作
        quick_frame = QFrame()
        quick_frame.setObjectName("quickFrame")
        quick_frame.setStyleSheet("""
            #quickFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        quick_layout = QVBoxLayout(quick_frame)
        quick_layout.setContentsMargins(20, 20, 20, 20)
        quick_layout.setSpacing(20)
        
        # 快速操作标题
        quick_title = BodyLabel("快速操作")
        quick_title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        quick_layout.addWidget(quick_title)
        
        # 操作按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        # 创建补贴按钮
        create_subsidy_btn = PrimaryPushButton("创建补贴类型")
        create_subsidy_btn.setIcon(FluentIcon.ADD)
        create_subsidy_btn.setFixedHeight(50)
        buttons_layout.addWidget(create_subsidy_btn)
        
        # 添加家庭按钮
        add_family_btn = PrimaryPushButton("添加家庭")
        add_family_btn.setIcon(FluentIcon.PEOPLE)
        add_family_btn.setFixedHeight(50)
        buttons_layout.addWidget(add_family_btn)
        
        # 申请补贴按钮
        apply_subsidy_btn = PrimaryPushButton("申请补贴")
        apply_subsidy_btn.setIcon(FluentIcon.SEND)
        apply_subsidy_btn.setFixedHeight(50)
        buttons_layout.addWidget(apply_subsidy_btn)
        
        quick_layout.addLayout(buttons_layout)
        
        layout.addWidget(quick_frame)
        
        return widget
    
    def create_stat_card(self, title, value, icon, color):
        """创建统计卡片"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setStyleSheet(f"""
            #statCard {{
                background-color: {color}10;
                border-radius: 8px;
                border: 1px solid {color}30;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # 图标
        icon_label = QLabel()
        # icon_label.setPixmap(icon.pixmap(QSize(24, 24)))
        icon_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(icon_label)
        
        # 数值
        value_label = QLabel(value)
        value_label.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # 标题
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 10))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        return card
    
    def create_subsidy_interface(self):
        """创建补贴管理界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        widget.setObjectName("subsidyInterface")
        # 标题
        title_label = TitleLabel("补贴管理")
        layout.addWidget(title_label)
        
        # 添加内容
        content = QLabel("补贴管理界面内容...")
        content.setFont(QFont("Microsoft YaHei", 14))
        layout.addWidget(content)
        
        return widget
    
    def create_family_interface(self):
        """创建家庭管理界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        widget.setObjectName("familyInterface")
        # 标题
        title_label = TitleLabel("家庭管理")
        layout.addWidget(title_label)
        
        # 添加内容
        content = QLabel("家庭管理界面内容...")
        content.setFont(QFont("Microsoft YaHei", 14))
        layout.addWidget(content)
        
        return widget
    
    def create_report_interface(self):
        """创建报表统计界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 标题
        title_label = TitleLabel("报表统计")
        layout.addWidget(title_label)
        
        # 添加内容
        content = QLabel("报表统计界面内容...")
        content.setFont(QFont("Microsoft YaHei", 14))
        layout.addWidget(content)
        
        return widget
    
    def create_setting_interface(self):
        """创建系统设置界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 标题
        title_label = TitleLabel("系统设置")
        layout.addWidget(title_label)
        
        # 添加内容
        content = QLabel("系统设置界面内容...")
        content.setFont(QFont("Microsoft YaHei", 14))
        layout.addWidget(content)
        
        return widget

import sys
from PySide6.QtCore import Qt, QSize, QUrl, QPoint
from PySide6.QtGui import QIcon, QDesktopServices, QColor, QFont
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QApplication, QFrame, QStackedWidget,QMainWindow

from qfluentwidgets import (NavigationItemPosition, MessageBox, MSFluentTitleBar, MSFluentWindow,
                            TabBar, SubtitleLabel, setFont, TabCloseButtonDisplayMode, IconWidget,
                            TransparentDropDownToolButton, TransparentToolButton, setTheme, Theme, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF

from ui import FamilyManageUI

class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))



class SubWindow(QFrame):
    """右侧子窗口内容模板"""
    def __init__(self, title, description, icon=None, parent=None):
        super().__init__(parent)
        self.setObjectName("subWindow")
        self.setStyleSheet("""
            #subWindow {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 标题区域
        title_layout = QHBoxLayout()
        # if icon:
        #     title_layout.addWidget(icon)
        title_label = TitleLabel(title)
        setFont(title_label, 18)
        title_layout.addWidget(title_label)
        title_layout.addStretch(1)
        
        # 描述区域
        desc_label = CaptionLabel(description)
        setFont(desc_label, 12)
        desc_label.setWordWrap(True)
        
        # 内容区域（示例内容）
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)
        
        # 示例内容项
        for i in range(1, 6):
            item_layout = QHBoxLayout()
            item_layout.addWidget(QLabel(f"项目 {i}"))
            item_layout.addStretch(1)
            btn = PrimaryPushButton(f"操作 {i}")
            btn.setFixedWidth(120)
            item_layout.addWidget(btn)
            content_layout.addLayout(item_layout)
        
        layout.addLayout(title_layout)
        layout.addWidget(desc_label)
        layout.addSpacing(20)
        layout.addLayout(content_layout)
        layout.addStretch(1)
        
class PersonManageUI(SubWindow):
    """人员管理子窗口"""
    def __init__(self, parent=None):
        super().__init__("人员管理", "管理个人资料和相关信息", FluentIcon.CONNECT, parent)
        
class FinanceManageUI(SubWindow):
    """财务管理子窗口"""
    def __init__(self, parent=None):
        super().__init__("财务管理", "管理补贴发放和财务记录", FluentIcon.MORE, parent)
        
class ReportUI(SubWindow):
    """报表统计子窗口"""
    def __init__(self, parent=None):
        super().__init__("报表统计", "生成各类统计报表", FluentIcon.CHAT, parent)
        
class SettingsUI(SubWindow):
    """系统设置子窗口"""
    def __init__(self, parent=None):
        super().__init__("系统设置", "配置系统参数和用户设置", FluentIcon.SETTING, parent)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("补贴管理系统")
        self.resize(1200, 700)
        
        # 设置应用主题
        setTheme(Theme.LIGHT)
        
        # 创建主布局
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 左侧导航栏
        self.nav_bar = NavigationBar(self)
        self.nav_bar.setFixedWidth(120)
        
        # 添加导航项
        self.nav_items = {
            "family": self.nav_bar.addItem(
                routeKey="family",
                icon=FluentIcon.HOME,
                text="家庭管理",
                onClick=lambda: self.switch_page(0)),
            "person": self.nav_bar.addItem(
                routeKey="person",
                icon=FluentIcon.PEOPLE,
                text="人员管理",
                onClick=lambda: self.switch_page(1)),
            "finance": self.nav_bar.addItem(
                routeKey="finance",
                icon=FluentIcon.CAFE,
                text="财务管理",
                onClick=lambda: self.switch_page(2)),
            "report": self.nav_bar.addItem(
                routeKey="report",
                icon=FluentIcon.CHAT,
                text="报表统计",
                onClick=lambda: self.switch_page(3),
                position=NavigationItemPosition.BOTTOM),
            "settings": self.nav_bar.addItem(
                routeKey="setting",
                icon=FluentIcon.SETTING,
                text="系统设置",
                onClick=lambda: self.switch_page(4),
                position=NavigationItemPosition.BOTTOM)
        }
        
        # 右侧内容区域
        right_widget = QFrame()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 顶部标题栏
        header = QFrame()
        header.setFixedHeight(18)
        header.setStyleSheet("background-color: #f5f5f5; border-bottom: 1px solid #e0e0e0;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)
        self.title_label = QLabel("xx镇数据工具")
        setFont(self.title_label, 16)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)
        
        # 用户信息
        user_widget = QWidget()
        user_layout = QHBoxLayout(user_widget)
        user_layout.setSpacing(10)
        user_layout.addWidget(QLabel("管理员"))
        
        header_layout.addWidget(user_widget)
        
        # 创建堆叠窗口
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(FamilyManageUI('Family managerui', self))
        self.stacked_widget.addWidget(PersonManageUI())
        self.stacked_widget.addWidget(FinanceManageUI())
        self.stacked_widget.addWidget(ReportUI())
        self.stacked_widget.addWidget(SettingsUI())
        
        # 添加部件到右侧布局
        right_layout.addWidget(header)
        right_layout.addWidget(self.stacked_widget)
        
        # 添加导航栏和内容区域到主布局
        main_layout.addWidget(self.nav_bar)
        main_layout.addWidget(right_widget, 1)  # 右侧区域占据剩余空间
        
        # 设置中心窗口
        self.setCentralWidget(main_widget)
        
        # 初始化选中项
        self.nav_bar.setCurrentItem("family")
        self.switch_page(0)
        
        # 应用样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f7;
            }
            QLabel {
                color: #333333;
            }
            NavigationBar {
                background-color: white;
                border-right: 1px solid #e0e0e0;
            }
        """)
    
    def switch_page(self, index):
        """切换页面"""
        self.stacked_widget.setCurrentIndex(index)
        
        # 更新标题
        titles = ["家庭管理", "人员管理", "财务管理", "报表统计", "系统设置"]
        # self.title_label.setText(titles[index])


class CustomTitleBar(MSFluentTitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)

        # add buttons
        self.toolButtonLayout = QHBoxLayout()
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(96, 96, 96)
        self.searchButton = TransparentToolButton(FIF.SEARCH_MIRROR.icon(color=color), self)
        self.forwardButton = TransparentToolButton(FIF.RIGHT_ARROW.icon(color=color), self)
        self.backButton = TransparentToolButton(FIF.LEFT_ARROW.icon(color=color), self)

        self.forwardButton.setDisabled(True)
        self.toolButtonLayout.setContentsMargins(20, 0, 20, 0)
        self.toolButtonLayout.setSpacing(15)
        self.toolButtonLayout.addWidget(self.searchButton)
        self.toolButtonLayout.addWidget(self.backButton)
        self.toolButtonLayout.addWidget(self.forwardButton)
        self.hBoxLayout.insertLayout(4, self.toolButtonLayout)

        # add tab bar
        self.tabBar = TabBar(self)

        self.tabBar.setMovable(True)
        self.tabBar.setTabMaximumWidth(220)
        self.tabBar.setTabShadowEnabled(False)
        self.tabBar.setTabSelectedBackgroundColor(QColor(255, 255, 255, 125), QColor(255, 255, 255, 50))
        # self.tabBar.setScrollable(True)
        # self.tabBar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ON_HOVER)

        self.tabBar.tabCloseRequested.connect(self.tabBar.removeTab)
        self.tabBar.currentChanged.connect(lambda i: print(self.tabBar.tabText(i)))

        self.hBoxLayout.insertWidget(5, self.tabBar, 1)
        self.hBoxLayout.setStretch(6, 0)

        # add avatar
        self.avatar = TransparentDropDownToolButton('resource/shoko.png', self)
        self.avatar.setIconSize(QSize(26, 26))
        self.avatar.setFixedHeight(30)
        self.hBoxLayout.insertWidget(7, self.avatar, 0, Qt.AlignRight)
        self.hBoxLayout.insertSpacing(8, 20)

    def canDrag(self, pos: QPoint):
        if not super().canDrag(pos):
            return False

        pos.setX(pos.x() - self.tabBar.x())
        return not self.tabBar.tabRegion().contains(pos)
    
class Window(MSFluentWindow):

    def __init__(self):
        self.isMicaEnabled = False

        super().__init__()
        self.setTitleBar(CustomTitleBar(self))
        self.tabBar = self.titleBar.tabBar  # type: TabBar

        # create sub interface
        self.homeInterface = QStackedWidget(self, objectName='homeInterface')
        self.appInterface = Widget('Application Interface', self)
        self.videoInterface = Widget('Video Interface', self)
        self.libraryInterface = Widget('library Interface', self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', FIF.HOME_FILL)
        self.addSubInterface(self.appInterface, FIF.APPLICATION, '应用')
        self.addSubInterface(self.videoInterface, FIF.VIDEO, '视频')

        self.addSubInterface(self.libraryInterface, FIF.BOOK_SHELF,
                             '库', FIF.LIBRARY_FILL, NavigationItemPosition.BOTTOM)
        self.navigationInterface.addItem(
            routeKey='Help',
            icon=FIF.HELP,
            text='帮助',
            onClick=self.showMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setCurrentItem(
            self.homeInterface.objectName())

        # add tab
        self.addTab('Heart', 'As long as you love me', icon='resource/Heart.png')

        self.tabBar.currentChanged.connect(self.onTabChanged)
        self.tabBar.tabAddRequested.connect(self.onTabAddRequested)

    def initWindow(self):
        self.resize(1100, 750)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('PyQt-Fluent-Widgets')

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def showMessageBox(self):
        w = MessageBox(
            '支持作者🥰',
            '个人开发不易，如果这个项目帮助到了您，可以考虑请作者喝一瓶快乐水🥤。您的支持就是作者开发和维护项目的动力🚀',
            self
        )
        w.yesButton.setText('来啦老弟')
        w.cancelButton.setText('下次一定')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://afdian.net/a/zhiyiYo"))

    def onTabChanged(self, index: int):
        objectName = self.tabBar.currentTab().routeKey()
        self.homeInterface.setCurrentWidget(self.findChild(TabInterface, objectName))
        self.stackedWidget.setCurrentWidget(self.homeInterface)

    def onTabAddRequested(self):
        text = f'硝子酱一级棒卡哇伊×{self.tabBar.count()}'
        self.addTab(text, text, 'resource/Smiling_with_heart.png')

    def addTab(self, routeKey, text, icon):
        self.tabBar.addTab(routeKey, text, icon)
        self.homeInterface.addWidget(TabInterface(text, icon, routeKey, self))


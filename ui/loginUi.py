import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QLineEdit, QPushButton, QFrame, QStackedWidget,)
from PySide6.QtCore import Qt, QSize,QSettings
from PySide6.QtGui import QFont, QIcon, QPixmap,QKeyEvent
from qfluentwidgets import (MSFluentWindow, NavigationItemPosition, setTheme, Theme,
                           PrimaryPushButton, LineEdit, InfoBar, InfoBarPosition,
                           BodyLabel, TitleLabel, FluentIcon, setThemeColor,CheckBox)
from . import MainWindow

class LoginWindow(QMainWindow):
    """登录窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("补贴管理系统 - 登录")
        self.resize(500, 400)
        
        # 设置主题
        setTheme(Theme.LIGHT)
        setThemeColor("#2b579a")  # 设置主题色为蓝色
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(50, 30, 50, 50)
        
        # 添加系统图标
        icon_label = QLabel()
        icon_pixmap = QPixmap(":/images/logo.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if icon_pixmap.isNull():
            # 如果没有资源文件，创建一个简单的图标
            icon_label.setText("🌾")
            icon_label.setStyleSheet("font-size: 80px;")
        else:
            icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(icon_label)
        
        # 添加系统标题
        title = QLabel("补贴管理系统")
        title.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        title.setStyleSheet("color: #2b579a;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # 添加登录表单
        form_frame = QFrame()
        form_frame.setObjectName("loginForm")
        form_frame.setStyleSheet("""
            #loginForm {
                background-color: #f9f9f9;
                border-radius: 8px;
                padding: 20px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # 用户名输入
        form_layout.addWidget(BodyLabel("用户名", form_frame))
        self.username_edit = LineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        self.username_edit.setClearButtonEnabled(True)
        form_layout.addWidget(self.username_edit)
        
        # 密码输入
        form_layout.addWidget(BodyLabel("密码", form_frame))
        self.password_edit = LineEdit()
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setClearButtonEnabled(True)
        form_layout.addWidget(self.password_edit)
        
        # 记住我选项
        # 记住我选项
        self.remember_check = CheckBox("记住我")
        self.remember_check.setChecked(True)  # 默认勾选
        form_layout.addWidget(self.remember_check)
        
        # 错误信息标签
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(self.error_label)
        
        # 登录按钮
        self.login_btn = PrimaryPushButton("登录")
        self.login_btn.setFixedHeight(40)
        self.login_btn.clicked.connect(self.attempt_login)
        form_layout.addWidget(self.login_btn)
        
        main_layout.addWidget(form_frame)
        
        # 添加底部信息
        footer = QLabel("© 2025 补贴管理系统 | 版本 1.0.0")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: gray; font-size: 12px;")
        main_layout.addWidget(footer)
            # 加载保存的登录信息

        self.load_saved_credentials()

        # 设置回车键登录
        self.username_edit.returnPressed.connect(self.attempt_login)
        self.password_edit.returnPressed.connect(self.attempt_login)

    def load_saved_credentials(self):
            """加载保存的登录信息"""
            settings = QSettings("MyCompany", "SubsidySystem")
            remember = settings.value("remember_me", False, type=bool)
            if remember:
                username = settings.value("username", "")
                password = settings.value("password", "")
                self.username_edit.setText(username)
                self.password_edit.setText(password)
                self.remember_check.setChecked(True)
                
                # 如果记住密码，自动聚焦到密码输入框
                if username:
                    self.password_edit.setFocus()
    def save_credentials(self, username, password):
        """保存登录信息"""
        settings = QSettings("MyCompany", "SubsidySystem")
        if self.remember_check.isChecked():
            settings.setValue("username", username)
            settings.setValue("password", password)
            settings.setValue("remember_me", True)
        else:
            # 如果不记住密码，清除保存的信息
            settings.remove("username")
            settings.remove("password")
            settings.setValue("remember_me", False)

    def attempt_login(self):
        """尝试登录"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        if not username or not password:
            self.error_label.setText("用户名和密码不能为空")
            return
        
        # 简单验证 - 实际应用中应该连接数据库验证
        if username == "admin" and password == "admin123":
            # 保存登录信息
            self.save_credentials(username, password)
            
            self.error_label.setText("")
            self.login_success()
        else:
            self.error_label.setText("用户名或密码错误")
    
    def login_success(self):
        """登录成功"""
        # 创建主窗口
        self.main_window = MainWindow()
        self.main_window.show()
        
        # 关闭登录窗口
        self.close()

    def keyPressEvent(self, event: QKeyEvent):
        """重写键盘事件"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.attempt_login()
        else:
            super().keyPressEvent(event)





if __name__ == "__main__":
    # 创建应用
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 使用Fusion样式确保跨平台一致性
    # 设置应用程序字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    # 创建登录窗口
    login_window = LoginWindow()
    login_window.show()
    
    # 运行应用
    sys.exit(app.exec())
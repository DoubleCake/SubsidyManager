# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'submangeui.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QSizePolicy,
    QTableWidgetItem, QVBoxLayout, QWidget)

from qfluentwidgets import ComboBox, LineEdit, PushButton, TableWidget,SubtitleLabel,CardWidget
from services import SubsidyService 

class SubsidyManageUI(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        # self.label = SubtitleLabel(text, self)
        self.setObjectName(text.replace(' ', '-'))
        self.service = SubsidyService()
        self.setupUi()


    def setupUi(self):

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        # 标题区域
        title_card = CardWidget()
        title_layout = QHBoxLayout()
        self.titleLabel = SubtitleLabel("补贴管理")
        title_layout.addWidget(self.titleLabel, alignment=Qt.AlignLeft)
        title_card.setLayout(title_layout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.comboBox = ComboBox()
        self.comboBox.setObjectName(u"comboBox")

        self.horizontalLayout.addWidget(self.comboBox)

        self.lineEdit = LineEdit()
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)

        self.addSubBtn_2 = PushButton("搜索")
        self.horizontalLayout.addWidget(self.addSubBtn_2)
        self.tableWidget = TableWidget()
        if (self.tableWidget.columnCount() < 3):
            self.tableWidget.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.addSubBtn = PushButton("创建新的补贴")

        self.verticalLayout.addWidget(title_card)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.tableWidget)
        # self.addSubBtn.setObjectName(u"pushButton")
        self.verticalLayout.addWidget(self.addSubBtn)
        self.addSubBtn.clicked.connect(self.open_type_edit_dialog)

    def open_type_edit_dialog(self, subsidy_id=None):
        """打开补贴类型编辑窗口"""
        from .components.subsidy_type_edit_window import SubsidyTypeEditWindow
        
        self.edit_window = SubsidyTypeEditWindow(self.service, subsidy_id, self)
        self.edit_window.data_saved.connect(self.handle_subsidy_saved)
        self.edit_window.show()

    def handle_subsidy_created(self, subsidy_data):
        # 处理新创建的补贴类型
        print(f"新补贴类型创建成功: {subsidy_data['name']}")
        # 刷新表格等操作
        
    def handle_subsidy_updated(self, subsidy_data):
        # 处理更新的补贴类型
        print(f"补贴类型更新成功: {subsidy_data['name']}")
        # 刷新表格等操作
    #     QMetaObject.connectSlotsByName(subsidy_manage_ui)
    # # setupUi
    def handle_subsidy_saved(self ):
        # 处理更新的补贴类型
        print(f"补贴类型更新成功:")
    # def retranslateUi(self, subsidy_manage_ui):
    #     subsidy_manage_ui.setWindowTitle(QCoreApplication.translate("subsidy_manage_ui", u"Form", None))
    #     self.addSubBtn_2.setText(QCoreApplication.translate("subsidy_manage_ui", u"\u641c\u7d22", None))
    #     ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
    #     ___qtablewidgetitem.setText(QCoreApplication.translate("subsidy_manage_ui", u"\u5e74\u4efd", None));
    #     ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
    #     ___qtablewidgetitem1.setText(QCoreApplication.translate("subsidy_manage_ui", u"\u65b0\u5efa\u5217", None));
    #     ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
    #     ___qtablewidgetitem2.setText(QCoreApplication.translate("subsidy_manage_ui", u"\u8865\u8d34\u6807\u51c6", None));
    #     self.addSubBtn.setText(QCoreApplication.translate("subsidy_manage_ui", u"\u521b\u5efa\u65b0\u7684\u8865\u8d34", None))
    # # retranslateUi


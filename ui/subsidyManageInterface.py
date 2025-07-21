import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QPushButton, QFrame, QStackedWidget, QTableWidget,
                              QTableWidgetItem, QHeaderView, QAbstractItemView, QToolBar,
                              QStatusBar, QSizePolicy, QComboBox, QLineEdit, QMessageBox,QSplitter,QGridLayout,QGroupBox,QFormLayout,QFileDialog)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QFont, QIcon, QAction, QColor,QPainter
from qfluentwidgets import (MSFluentWindow, NavigationItemPosition, setTheme, Theme,
                           PrimaryPushButton, LineEdit, InfoBar, InfoBarPosition,
                           BodyLabel, TitleLabel, FluentIcon, setThemeColor, 
                           ToolButton, RoundMenu, FlowLayout, CardWidget,isDarkTheme,
                           StateToolTip, ProgressBar, SearchLineEdit, MessageBox)
from PySide6.QtCore import QTimer
import os,sys,shutil

from .subsidyPopupUi import SubsidyPopup

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

class ProgressDetailSection(QGroupBox):
    """进度详情部分 - 包含阶段划分和材料管理按钮"""
    def __init__(self, parent=None):
        super().__init__("进度详情", parent)
        self.subsidy_data = None
        self.stage_buttons = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 阶段进度指示器与进度条合并
        self.stage_progress_widget = QWidget()
        stage_progress_layout = QHBoxLayout(self.stage_progress_widget)
        stage_progress_layout.setContentsMargins(0, 0, 0, 0)
        stage_progress_layout.setSpacing(0)
        # 阶段定义
        self.stages = [
            {"name": "材料准备", "color": "#9e9e9e", "threshold": 0},
            {"name": "初审", "color": "#2196f3", "threshold": 20},
            {"name": "实地核查", "color": "#4caf50", "threshold": 40},
            {"name": "复核", "color": "#ff9800", "threshold": 60},
            {"name": "资金发放", "color": "#9c27b0", "threshold": 80},
            {"name": "归档", "color": "#607d8b", "threshold": 100}
        ]
        for i, stage in enumerate(self.stages):
            stage_widget = QWidget()
            stage_widget.setObjectName(f"stage_{i}")
            stage_widget.setStyleSheet(f"""
                #stage_{i} {{
                    background-color: {stage['color']}30;
                    border-radius: 4px;
                    flex-grow: 1; /* 允许增长 */
                    min-height: 10px;
                }}
            """)
            stage_progress_layout.addWidget(stage_widget)
        layout.addWidget(self.stage_progress_widget)

        # 进度状态描述
        self.progress_desc = QLabel("请从上方列表中选择一个补贴查看详情")
        self.progress_desc.setWordWrap(True)
        self.progress_desc.setStyleSheet("font-size: 14px; color: #555; font-weight: bold;")
        layout.addWidget(self.progress_desc)

        # 阶段标签和按钮
        self.stage_container = QWidget()
        stage_btn_layout = QHBoxLayout(self.stage_container)
        stage_btn_layout.setContentsMargins(0, 10, 0, 0)
        stage_btn_layout.setSpacing(10)
        for stage in self.stages:
            # 阶段标签
            stage_label = QLabel(stage["name"])
            stage_label.setAlignment(Qt.AlignCenter)
            stage_label.setStyleSheet(f"color: {stage['color']}; font-weight: bold; font-size: 12px;")
            stage_label.setFixedWidth(80)
            stage_btn_layout.addWidget(stage_label)
            # 材料按钮
            btn = ToolButton(FluentIcon.FOLDER)
            btn.setIconSize(QSize(18, 18))
            btn.setToolTip(f"打开{stage['name']}材料文件夹")
            btn.setFixedSize(35, 35)
            btn.setStyleSheet(f"""
                ToolButton {{
                    background-color: {stage['color']}30;
                    border-radius: 6px;
                }}
                ToolButton:hover {{
                    background-color: {stage['color']}50;
                }}
            """)
            btn.clicked.connect(lambda _, s=stage: self.handle_stage_materials(s))
            self.stage_buttons[stage["name"]] = btn
            stage_btn_layout.addWidget(btn)
            stage_btn_layout.addSpacing(20)  # 增加间隔
        stage_btn_layout.addStretch(1)
        layout.addWidget(self.stage_container)

        # 初始禁用所有按钮
        self.disable_all_buttons()

    def disable_all_buttons(self):
        """禁用所有阶段按钮"""
        for btn in self.stage_buttons.values():
            btn.setEnabled(False)
    def update_progress(self, subsidy_data):
            """更新进度信息"""
            self.subsidy_data = subsidy_data
            progress = subsidy_data["progress"]
            status = subsidy_data["status"]
            # 更新进度描述
            self.progress_desc.setText(subsidy_data["progress_desc"])
            # 更新阶段指示器颜色
            for i, stage in enumerate(self.stages):
                stage_widget = self.stage_progress_widget.findChild(QWidget, f"stage_{i}")
                if stage_widget:
                    if progress >= stage["threshold"]:
                        stage_widget.setStyleSheet(f"""
                            #stage_{i} {{
                                background-color: {stage['color']}60; /* 完成的颜色更深 */
                                border-radius: 4px;
                            }}
                        """)
                    else:
                        stage_widget.setStyleSheet(f"""
                            #stage_{i} {{
                                background-color: #e0e0e0; /* 尚未达到进度的部分使用浅灰色 */
                                border-radius: 4px;
                            }}
                        """)
            # 启用相关按钮
            self.update_stage_buttons(progress)

    def update_stage_buttons(self, progress):
        """更新阶段按钮状态"""
        # 先禁用所有按钮
        self.disable_all_buttons()
        # 启用已完成和当前阶段的按钮
        for stage in self.stages:
            btn = self.stage_buttons[stage["name"]]
            if progress >= stage["threshold"]:
                btn.setEnabled(True)
            """处理阶段材料按钮点击"""
    def handle_stage_materials(self, stage):
        """处理阶段材料按钮点击"""
        if not self.subsidy_data:
            return

        subsidy_name = self.subsidy_data["name"]
        year = self.subsidy_data["year"]
        stage_name = stage["name"]

        # 构建目标路径
        base_dir = os.path.abspath(os.path.dirname(__file__))
        target_dir = os.path.join(base_dir, "补贴管理", year, subsidy_name, stage_name)

        # 如果目标路径不存在，弹出文件夹选择对话框
        if not os.path.exists(target_dir):
            # 提示用户选择一个现有文件夹来复制内容
            selected_dir = QFileDialog.getExistingDirectory(
                self,
                f"选择 '{stage_name}' 阶段的材料文件夹",
                os.path.expanduser("~")
            )
            if not selected_dir:
                InfoBar.warning(
                    title="操作取消",
                    content="未选择文件夹，操作已取消。",
                    parent=self,
                    position=InfoBarPosition.TOP,
                    duration=3000
                )
                return

            # 创建目标文件夹
            os.makedirs(target_dir, exist_ok=True)

            # 复制选中文件夹中的内容到目标路径
            try:
                for item in os.listdir(selected_dir):
                    src_path = os.path.join(selected_dir, item)
                    dst_path = os.path.join(target_dir, item)
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dst_path)
                    else:
                        shutil.copy2(src_path, dst_path)
                InfoBar.success(
                    title="材料已复制",
                    content=f"已从 '{selected_dir}' 复制材料到 '{target_dir}'",
                    parent=self,
                    position=InfoBarPosition.TOP,
                    duration=3000
                )
            except Exception as e:
                InfoBar.error(
                    title="复制失败",
                    content=f"复制材料时出错：{str(e)}",
                    parent=self,
                    position=InfoBarPosition.TOP,
                    duration=5000
                )
                return

        # 打开目标文件夹
        self.open_folder(target_dir)

    def copy_initial_materials(self, target_dir, stage_name):
        """复制初始材料到目标文件夹"""
        # 基础材料路径（实际应用中应该有一个预设的材料目录）
        base_materials = os.path.abspath(os.path.join(os.path.dirname(__file__), "初始材料"))
        # 阶段特定材料映射
        stage_materials = {
            "材料准备": ["补贴申请表模板.docx", "材料清单.xlsx"],
            "初审": ["初审标准.pdf", "初审记录表.xlsx"],
            "实地核查": ["实地核查指南.pdf", "核查记录表.docx"],
            "复核": ["复核流程.docx", "复核意见表.xlsx"],
            "资金发放": ["发放名单模板.xlsx", "发放流程说明.pdf"],
            "归档": ["归档清单.xlsx", "归档说明.docx"]
        }
        # 复制材料
        if os.path.exists(base_materials) and stage_name in stage_materials:
            for file_name in stage_materials[stage_name]:
                src_path = os.path.join(base_materials, file_name)
                dst_path = os.path.join(target_dir, file_name)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dst_path)
                else:
                    # 如果文件不存在，创建一个空文件作为占位符
                    with open(dst_path, 'w') as f:
                        f.write(f"这是 {stage_name} 阶段的 {file_name} 文件占位符")

    def open_folder(self, path):
        """打开指定文件夹"""
        if os.path.exists(path):
            # 跨平台打开文件夹
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":  # macOS
                os.system(f'open "{path}"')
            else:  # Linux
                os.system(f'xdg-open "{path}"')
        else:
            InfoBar.warning(
                title="文件夹不存在",
                content=f"无法找到路径: {path}",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=3000
            )

    def clear(self):
        """清除显示"""
        self.subsidy_data = None
        self.progress_desc.setText("请从上方列表中选择一个补贴查看详情")
        # 重置阶段指示器
        for i in range(len(self.stages)):
            stage_widget = self.stage_progress_widget.findChild(QWidget, f"stage_{i}")
            if stage_widget:
                stage_widget.setStyleSheet(f"""
                    #stage_{i} {{
                        background-color: {self.stages[i]['color']}30;
                        border-radius: 4px;
                    }}
                """)
        # 禁用所有按钮
        self.disable_all_buttons()

class SubsidyManagementInterface(QWidget):
    """补贴管理界面 - 列表/看板视图在上方，详细信息在下方"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("subsidy_interface") 
        self.current_subsidy = None
        self.setup_ui()
    
    def setup_ui(self):
        # 主布局 - 垂直布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建垂直分割器
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # 上部容器（列表/看板）
        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # 顶部工具栏
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)
        
        # 创建补贴按钮
        self.create_btn = PrimaryPushButton("创建补贴")
        self.create_btn.setIcon(FluentIcon.ADD)
        self.create_btn.setFixedHeight(36)
        toolbar_layout.addWidget(self.create_btn)
        
        # 搜索框
        self.search_box = SearchLineEdit()
        self.search_box.setPlaceholderText("搜索补贴名称或编码")
        self.search_box.setFixedWidth(300)
        toolbar_layout.addWidget(self.search_box)
        
        # 状态筛选
        toolbar_layout.addWidget(QLabel("状态:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["全部", "草稿", "审核中", "发放中", "已完成", "已归档"])
        self.status_combo.setFixedWidth(120)
        toolbar_layout.addWidget(self.status_combo)
        
        # 年份筛选
        toolbar_layout.addWidget(QLabel("年份:"))
        self.year_combo = QComboBox()
        self.year_combo.addItems(["全部", "2023", "2024", "2025"])
        self.year_combo.setCurrentText(str(QDate.currentDate().year()))
        self.year_combo.setFixedWidth(100)
        toolbar_layout.addWidget(self.year_combo)
        
        toolbar_layout.addStretch(1)
        
        # 视图切换按钮
        self.view_toggle = ToolButton(FluentIcon.LAYOUT)
        self.view_toggle.setToolTip("切换视图")
        self.view_toggle.setFixedSize(36, 36)
        toolbar_layout.addWidget(self.view_toggle)
        
        # 添加工具栏
        top_layout.addLayout(toolbar_layout)
        
        # 视图切换区域
        self.view_stack = QStackedWidget()
        
        # 1. 列表视图
        self.list_view = self.create_list_view()
        self.view_stack.addWidget(self.list_view)
        
        # 2. 看板视图
        self.kanban_view = self.create_kanban_view()
        self.view_stack.addWidget(self.kanban_view)
        
        top_layout.addWidget(self.view_stack)
        
        # 默认显示列表视图
        self.view_stack.setCurrentIndex(0)
        
        # 下部详细信息面板
        self.detail_panel = self.create_detail_panel()
        
        # 添加到分割器
        splitter.addWidget(top_container)
        splitter.addWidget(self.detail_panel)
        splitter.setSizes([400, 200])  # 设置上下比例
        
        # 连接信号
        self.view_toggle.clicked.connect(self.toggle_view)
        self.create_btn.clicked.connect(self.create_subsidy)
        self.status_combo.currentIndexChanged.connect(self.filter_subsidies)
        self.year_combo.currentIndexChanged.connect(self.filter_subsidies)
        self.search_box.textChanged.connect(self.filter_subsidies)
    
    def create_list_view(self):
        """创建列表视图"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["补贴名称", "补贴编码", "年份", "状态", "当前进度", "创建时间", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # 设置每页显示10条
        self.table.setRowCount(10)
        
        # 设置样式
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # 添加示例数据
        self.load_sample_data()
        
        # 连接选中信号
        self.table.itemSelectionChanged.connect(self.on_subsidy_selected)
        
        layout.addWidget(self.table)
        
        # 添加分页控件
        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(0, 10, 0, 0)
        
        self.prev_btn = QPushButton("上一页")
        self.prev_btn.setFixedWidth(80)
        pagination_layout.addWidget(self.prev_btn)
        
        self.page_label = QLabel("1/5")
        pagination_layout.addWidget(self.page_label)
        
        self.next_btn = QPushButton("下一页")
        self.next_btn.setFixedWidth(80)
        pagination_layout.addWidget(self.next_btn)
        
        pagination_layout.addStretch(1)
        
        layout.addLayout(pagination_layout)
        
        return widget
    
    def create_detail_panel(self):
        """创建下方详细信息面板"""
        panel = SimpleCardWidget()
        panel.setObjectName("detailPanel")
        panel.setStyleSheet("""
            #detailPanel {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # 标题
        self.detail_title = TitleLabel("补贴详情")
        self.detail_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.detail_title)
        
        # 使用网格布局展示详细信息
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        # 第一列：基本信息
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(8)
        
        self.name_label = QLabel()
        self.code_label = QLabel()
        self.year_label = QLabel()
        self.amount_label = QLabel()
        self.created_label = QLabel()
        self.status_label = QLabel()
        
        info_layout.addRow("名称:", self.name_label)
        info_layout.addRow("编码:", self.code_label)
        info_layout.addRow("年份:", self.year_label)
        info_layout.addRow("金额:", self.amount_label)
        info_layout.addRow("创建时间:", self.created_label)
        info_layout.addRow("状态:", self.status_label)
        
        grid_layout.addWidget(info_group, 0, 0)
        
        # 第二列：统计信息
        stats_group = QGroupBox("统计信息")
        stats_layout = QFormLayout(stats_group)
        stats_layout.setSpacing(8)
        
        self.families_label = QLabel()
        self.area_label = QLabel()
        self.amount_total_label = QLabel()
        self.issues_label = QLabel()
        self.progress_label = QLabel()
        
        stats_layout.addRow("受益家庭:", self.families_label)
        stats_layout.addRow("补贴面积:", self.area_label)
        stats_layout.addRow("发放金额:", self.amount_total_label)
        stats_layout.addRow("异常情况:", self.issues_label)
        stats_layout.addRow("当前进度:", self.progress_label)
        
        grid_layout.addWidget(stats_group, 0, 1)
        
        # 第三列：进度详情（使用新的组件）
        self.progress_detail = ProgressDetailSection()
        grid_layout.addWidget(self.progress_detail, 0, 2)
        
        # 添加到主布局
        layout.addLayout(grid_layout)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.view_detail_btn = PrimaryPushButton("查看详情")
        self.view_detail_btn.setIcon(FluentIcon.VIEW)
        btn_layout.addWidget(self.view_detail_btn)
        
        self.edit_btn = PrimaryPushButton("编辑")
        self.edit_btn.setIcon(FluentIcon.EDIT)
        btn_layout.addWidget(self.edit_btn)
        
        self.process_btn = PrimaryPushButton("处理异常")
        self.process_btn.setIcon(FluentIcon.SETTING)
        btn_layout.addWidget(self.process_btn)
        
        btn_layout.addStretch(1)
        
        layout.addLayout(btn_layout)
        
        # 初始状态 - 无选中补贴
        self.clear_detail_panel()
        
        return panel
        
    
    def clear_detail_panel(self):
        """清空详细信息面板"""
        self.current_subsidy = None
        self.detail_title.setText("补贴详情")
        
        # 基本信息
        self.name_label.setText("未选择补贴")
        self.code_label.setText("")
        self.year_label.setText("")
        self.amount_label.setText("")
        self.created_label.setText("")
        self.status_label.setText("")
        
        # 统计信息
        self.families_label.setText("0")
        self.area_label.setText("0 亩")
        self.amount_total_label.setText("¥0")
        self.issues_label.setText("无异常")
        self.progress_label.setText("0%")
        
        # 进度详情
        self.progress_detail.clear()
        
        # 禁用操作按钮
        self.view_detail_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        self.process_btn.setEnabled(False)
    
    def on_subsidy_selected(self):
        """当补贴被选中时更新详情面板"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.clear_detail_panel()
            return
        
        # 获取选中行的第一列（补贴名称）
        row = selected_items[0].row()
        subsidy_name = self.table.item(row, 0).text()
        
        # 在实际应用中，这里会从数据库获取详细信息
        # 这里使用模拟数据
        self.current_subsidy = {
            "name": subsidy_name,
            "code": self.table.item(row, 1).text(),
            "year": self.table.item(row, 2).text(),
            "status": self.table.item(row, 3).text(),
            "progress": int(self.table.item(row, 4).text().replace("%", "")),
            "created": self.table.item(row, 5).text(),
            "amount": "¥150/亩",
            "families": "128户",
            "area": "1,250亩",
            "amount_total": "¥187,500",
            "issues": "2户面积异常，1户资格不符",
            "progress_desc": "当前处于审核阶段，已完成材料初审，等待实地核查"
        }
        
        self.update_detail_panel()
    
    def update_detail_panel(self):
        """更新详情面板显示当前选中的补贴信息"""
        if not self.current_subsidy:
            return
        
        # 更新基本信息
        self.name_label.setText(self.current_subsidy["name"])
        self.code_label.setText(self.current_subsidy["code"])
        self.year_label.setText(self.current_subsidy["year"])
        self.amount_label.setText(self.current_subsidy["amount"])
        self.created_label.setText(self.current_subsidy["created"])
        
        # 更新状态标签
        status = self.current_subsidy["status"]
        self.status_label.setText(status)
        # 更新状态标签
        status = self.current_subsidy["status"]
        self.status_label.setText(status)
        if status == "草稿":
            self.status_label.setStyleSheet("color: #9e9e9e; font-weight: bold;")
        elif status == "审核中":
            self.status_label.setStyleSheet("color: #2196f3; font-weight: bold;")
        elif status == "发放中":
            self.status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        elif status == "已完成":
            self.status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        elif status == "已归档":
            self.status_label.setStyleSheet("color: #607d8b; font-weight: bold;")
        
        # 更新统计信息
        self.families_label.setText(self.current_subsidy["families"])
        self.area_label.setText(self.current_subsidy["area"])
        self.amount_total_label.setText(self.current_subsidy["amount_total"])
        self.issues_label.setText(self.current_subsidy["issues"])
        self.progress_label.setText(f"{self.current_subsidy['progress']}%")
        
        # 更新进度详情
        self.progress_detail.update_progress(self.current_subsidy)
        
        # 启用操作按钮
        self.view_detail_btn.setEnabled(True)
        self.edit_btn.setEnabled(True)
        self.process_btn.setEnabled("异常" in self.current_subsidy["issues"])

    def create_subsidy(self):
        """创建新补贴"""
        # 在实际应用中，这里会打开创建补贴的对话框
        self.popup = SubsidyPopup(self)
        self.popup.show()
        # 居中显示
        main_geo = self.geometry()
        main_center = main_geo.center()
        # 计算弹出窗口位置
        popup_geo = self.popup.geometry()
        popup_geo.moveCenter(main_center)
        self.popup.move(popup_geo.topLeft())
        # # 显示创建状态提示
        # self.state_tooltip = StateToolTip("正在创建补贴", "请稍候...", self.window())
        # self.state_tooltip.move(self.state_tooltip.getSuitablePos())
        # self.state_tooltip.show()
        # # 模拟创建过程
        # QTimer.singleShot(2000, self.creation_completed)

    def filter_subsidies(self):
        """根据筛选条件过滤补贴"""
        # 在实际应用中，这里会连接数据库进行筛选
        print(f"筛选条件: 状态={self.status_combo.currentText()}, 年份={self.year_combo.currentText()}, 搜索={self.search_box.text()}")
       
    def create_kanban_column(self, title, color):
        """创建看板列"""
        column = QWidget()
        column.setObjectName("kanbanColumn")
        column.setStyleSheet(f"""
            #kanbanColumn {{
                background-color: #f5f5f5;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(column)
        layout.setSpacing(10)
        
        # 列标题
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-weight: bold;
            font-size: 14px;
            color: {color};
            padding: 5px;
            border-bottom: 2px solid {color};
        """)
        layout.addWidget(title_label)
        
        # 卡片容器
        card_container = QWidget()
        card_layout = QVBoxLayout(card_container)
        card_layout.setSpacing(10)
        card_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加示例卡片
        if title == "草稿":
            card_layout.addWidget(self.create_kanban_card("农业种植补贴", "AGRI-2023", "草稿", 0))
            card_layout.addWidget(self.create_kanban_card("渔业发展补贴", "FISH-2023", "草稿", 0))
        elif title == "审核中":
            card_layout.addWidget(self.create_kanban_card("林业保护补贴", "FOREST-2023", "审核中", 30))
            card_layout.addWidget(self.create_kanban_card("农机购置补贴", "MACHINE-2023", "审核中", 45))
        elif title == "发放中":
            card_layout.addWidget(self.create_kanban_card("畜牧养殖补贴", "ANIMAL-2023", "发放中", 70))
            card_layout.addWidget(self.create_kanban_card("粮食生产补贴", "GRAIN-2023", "发放中", 85))
        elif title == "已完成":
            card_layout.addWidget(self.create_kanban_card("有机农业补贴", "ORGANIC-2023", "已完成", 100))
        elif title == "已归档":
            card_layout.addWidget(self.create_kanban_card("节水灌溉补贴", "WATER-2022", "已归档", 100))
        
        # 添加弹性空间和添加按钮
        card_layout.addStretch(1)
        
        # 滚动区域
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.addWidget(card_container)
        scroll_layout.addStretch(1)
        
        layout.addWidget(scroll_widget)
        
        return column
    
    def create_kanban_card(self, name, code, status, progress):
        """创建看板卡片"""
        card = CardWidget()
        card.setFixedHeight(150)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 补贴名称
        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # 补贴编码和年份
        meta_layout = QHBoxLayout()
        meta_layout.addWidget(QLabel(f"编码: {code}"))
        meta_layout.addStretch()
        meta_layout.addWidget(QLabel(f"2023"))
        layout.addLayout(meta_layout)
        
        # 进度条
        progress_bar = ProgressBar()
        progress_bar.setValue(progress)
        progress_bar.setTextVisible(True)
        progress_bar.setAlignment(Qt.AlignCenter)
        progress_bar.setFormat(f"{progress}%")
        
        # 根据状态设置颜色
        if status == "草稿":
            progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #9e9e9e; }")
        elif status == "审核中":
            progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #2196f3; }")
        elif status == "发放中":
            progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff9800; }")
        elif status == "已完成" or status == "已归档":
            progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #4caf50; }")
        
        layout.addWidget(progress_bar)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        view_btn = ToolButton(FluentIcon.VIEW)
        view_btn.setToolTip("查看详情")
        view_btn.setFixedSize(30, 30)
        btn_layout.addWidget(view_btn)
        
        edit_btn = ToolButton(FluentIcon.EDIT)
        edit_btn.setToolTip("编辑")
        edit_btn.setFixedSize(30, 30)
        btn_layout.addWidget(edit_btn)
        
        delete_btn = ToolButton(FluentIcon.DELETE)
        delete_btn.setToolTip("删除")
        delete_btn.setFixedSize(30, 30)
        delete_btn.setEnabled(status in ["草稿", "审核中"])  # 只有特定状态可删除
        delete_btn.clicked.connect(lambda: self.confirm_delete_subsidy(name, code))
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch(1)
        
        # 状态标签
        status_label = QLabel(status)
        if status == "草稿":
            status_label.setStyleSheet("color: #9e9e9e; font-weight: bold;")
        elif status == "审核中":
            status_label.setStyleSheet("color: #2196f3; font-weight: bold;")
        elif status == "发放中":
            status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        elif status == "已完成":
            status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        elif status == "已归档":
            status_label.setStyleSheet("color: #607d8b; font-weight: bold;")
        btn_layout.addWidget(status_label)
        
        layout.addLayout(btn_layout)
        
        return card
    
    def create_kanban_view(self):
        """创建看板视图"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # 状态列
        statuses = [
            {"name": "草稿", "color": "#9e9e9e"},
            {"name": "审核中", "color": "#2196f3"},
            {"name": "发放中", "color": "#ff9800"},
            {"name": "已完成", "color": "#4caf50"},
            {"name": "已归档", "color": "#607d8b"}
        ]
        
        for status in statuses:
            column = self.create_kanban_column(status["name"], status["color"])
            layout.addWidget(column)
        
        return widget
    
    def load_sample_data(self):
        """加载示例数据到表格"""
        # 示例数据
        subsidies = [
            {"name": "农业种植补贴", "code": "AGRI-2023", "year": "2023", "status": "草稿", "progress": 0, "created": "2023-01-15"},
            {"name": "渔业发展补贴", "code": "FISH-2023", "year": "2023", "status": "草稿", "progress": 0, "created": "2023-02-20"},
            {"name": "林业保护补贴", "code": "FOREST-2023", "year": "2023", "status": "审核中", "progress": 30, "created": "2023-03-10"},
            {"name": "农机购置补贴", "code": "MACHINE-2023", "year": "2023", "status": "审核中", "progress": 45, "created": "2023-04-05"},
            {"name": "畜牧养殖补贴", "code": "ANIMAL-2023", "year": "2023", "status": "发放中", "progress": 70, "created": "2023-05-12"},
            {"name": "粮食生产补贴", "code": "GRAIN-2023", "year": "2023", "status": "发放中", "progress": 85, "created": "2023-06-18"},
            {"name": "有机农业补贴", "code": "ORGANIC-2023", "year": "2023", "status": "已完成", "progress": 100, "created": "2023-07-22"},
            {"name": "节水灌溉补贴", "code": "WATER-2022", "year": "2022", "status": "已归档", "progress": 100, "created": "2022-11-30"},
        ]
        
        self.table.setRowCount(len(subsidies))
        
        for row, subsidy in enumerate(subsidies):
            # 补贴名称
            name_item = QTableWidgetItem(subsidy["name"])
            self.table.setItem(row, 0, name_item)
            
            # 补贴编码
            code_item = QTableWidgetItem(subsidy["code"])
            self.table.setItem(row, 1, code_item)
            
            # 年份
            year_item = QTableWidgetItem(subsidy["year"])
            self.table.setItem(row, 2, year_item)
            
            # 状态
            status_item = QTableWidgetItem(subsidy["status"])
            if subsidy["status"] == "草稿":
                status_item.setForeground(QColor("#9e9e9e"))
            elif subsidy["status"] == "审核中":
                status_item.setForeground(QColor("#2196f3"))
            elif subsidy["status"] == "发放中":
                status_item.setForeground(QColor("#ff9800"))
            elif subsidy["status"] == "已完成":
                status_item.setForeground(QColor("#4caf50"))
            elif subsidy["status"] == "已归档":
                status_item.setForeground(QColor("#607d8b"))
            self.table.setItem(row, 3, status_item)
            
            # 当前进度
            progress_item = QTableWidgetItem(f"{subsidy['progress']}%")
            self.table.setItem(row, 4, progress_item)
            
            # 创建时间
            created_item = QTableWidgetItem(subsidy["created"])
            self.table.setItem(row, 5, created_item)
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(5)
            
            view_btn = ToolButton(FluentIcon.VIEW)
            view_btn.setFixedSize(30, 30)
            view_btn.setToolTip("查看详情")
            btn_layout.addWidget(view_btn)
            
            edit_btn = ToolButton(FluentIcon.EDIT)
            edit_btn.setFixedSize(30, 30)
            edit_btn.setToolTip("编辑")
            btn_layout.addWidget(edit_btn)
            
            delete_btn = ToolButton(FluentIcon.DELETE)
            delete_btn.setFixedSize(30, 30)
            delete_btn.setToolTip("删除")
            delete_btn.setEnabled(subsidy["status"] in ["草稿", "审核中"])  # 只有特定状态可删除
            delete_btn.clicked.connect(lambda _, name=subsidy["name"], code=subsidy["code"]: 
                                      self.confirm_delete_subsidy(name, code))
            btn_layout.addWidget(delete_btn)
            
            btn_layout.addStretch(1)
            self.table.setCellWidget(row, 6, btn_widget)
    def toggle_view(self):
        """切换列表和看板视图"""
        current_index = self.view_stack.currentIndex()
        new_index = 1 if current_index == 0 else 0
        self.view_stack.setCurrentIndex(new_index)
        
        # 更新按钮图标
        icon = FluentIcon.LIST if new_index == 0 else FluentIcon.LAYOUT
        self.view_toggle.setIcon(icon)
    
    
    def filter_subsidies(self):
        """根据筛选条件过滤补贴"""
        # 在实际应用中，这里会连接数据库进行筛选
        print(f"筛选条件: 状态={self.status_combo.currentText()}, 年份={self.year_combo.currentText()}, 搜索={self.search_box.text()}")
    
    def create_subsidy(self):
        """创建新补贴"""
        # # 在实际应用中，这里会打开创建补贴的对话框
        print("打开创建补贴对话框")
        # 在实际应用中，这里会打开创建补贴的对话框
        self.popup = SubsidyPopup(self)
        self.popup.show()
        # 居中显示
        main_geo = self.geometry()
        main_center = main_geo.center()
        # 计算弹出窗口位置
        popup_geo = self.popup.geometry()
        popup_geo.moveCenter(main_center)
        # self.popup.move(popup_geo.topLeft())
        # # 显示创建状态提示
        # self.state_tooltip = StateToolTip("正在创建补贴", "请稍候...", self.window())
        # self.state_tooltip.move(self.state_tooltip.getSuitablePos())
        # self.state_tooltip.show()
        
        # # 模拟创建过程
        # QTimer.singleShot(2000, self.creation_completed)
    
    def creation_completed(self):
        """补贴创建完成"""
        self.state_tooltip.setContent("创建成功 ✓")
        self.state_tooltip.setState(True)
        
        # 关闭提示
        QTimer.singleShot(1000, self.state_tooltip.close)
        
        # 刷新数据
        QTimer.singleShot(1200, self.load_sample_data)
    
    def confirm_delete_subsidy(self, name, code):
        """确认删除补贴"""
        result = MessageBox.warning(
            self,
            "确认删除补贴",
            f"确定要永久删除补贴 '{name}' ({code}) 吗?\n此操作不可撤销!",
            parent=self,
            buttons=MessageBox.Yes | MessageBox.No
        )
        
        if result == MessageBox.Yes:
            # 在实际应用中，这里会执行删除操作
            print(f"删除补贴: {name} ({code})")
            
            # 显示删除成功提示
            InfoBar.success(
                title="删除成功",
                content=f"补贴 '{name}' 已删除",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=3000
            )

# class MainWindow(MSFluentWindow):
#     """主应用程序窗口"""
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("补贴管理系统")
#         self.resize(1400, 900)
        
#         # 设置主题
#         setTheme(Theme.LIGHT)
#         setThemeColor("#2b579a")  # 设置主题色为蓝色
        
#         # 创建子界面
#         self.home_interface = self.create_home_interface()
#         self.home_interface.setObjectName("home_interface") 

#         self.subsidy_interface = SubsidyManagementInterface()
#         self.subsidy_interface.setObjectName("subsidy_interface") 
#         self.family_interface = self.create_family_interface()
#         self.family_interface.setObjectName("family_interface") 

#         self.report_interface = self.create_report_interface()
#         self.report_interface.setObjectName("report_interface") 

#         self.setting_interface = self.create_setting_interface()
#         self.setting_interface.setObjectName("setting_interface") 

        
#         # 添加导航项
#         self.addSubInterface(self.home_interface, FluentIcon.HOME, "首页")
#         self.addSubInterface(self.subsidy_interface, FluentIcon.TAG, "补贴管理")
#         self.addSubInterface(self.family_interface, FluentIcon.PEOPLE, "家庭管理")
#         self.addSubInterface(self.report_interface, FluentIcon.CHAT, "报表统计")
        
#         # 添加设置界面到导航栏底部
#         self.addSubInterface(self.setting_interface, FluentIcon.SETTING, "系统设置", NavigationItemPosition.BOTTOM)
        
#         # 设置初始页面
#         self.switchTo(self.home_interface)
        
#         # 添加导航栏标题
#         self.navigationInterface.setObjectName("navigationInterface")
#         self.setStyleSheet("#navigationInterface { border-right: 1px solid #e0e0e0; }")
    
#     def create_home_interface(self):
#         """创建首页界面"""
#         # 简化实现，实际应用中与之前相同
#         widget = QWidget()
#         layout = QVBoxLayout(widget)
#         layout.addWidget(QLabel("首页内容"))
#         return widget
    
#     def create_family_interface(self):
#         """创建家庭管理界面"""
#         widget = QWidget()
#         layout = QVBoxLayout(widget)
#         layout.addWidget(QLabel("家庭管理内容"))
#         return widget
    
#     def create_report_interface(self):
#         """创建报表统计界面"""
#         widget = QWidget()
#         layout = QVBoxLayout(widget)
#         layout.addWidget(QLabel("报表统计内容"))
#         return widget
    
#     def create_setting_interface(self):
#         """创建系统设置界面"""
#         widget = QWidget()
#         layout = QVBoxLayout(widget)
#         layout.addWidget(QLabel("系统设置内容"))
#         return widget

if __name__ == "__main__":
    # 创建应用
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 使用Fusion样式确保跨平台一致性
    
    # 设置应用程序字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())
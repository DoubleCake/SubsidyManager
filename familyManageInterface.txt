import sys
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, 
                              QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
                              QSplitter, QGroupBox, QFormLayout, QLabel, QPushButton, 
                              QTabWidget, QFrame, QToolButton,QGridLayout)
from PySide6.QtGui import QIcon
from qfluentwidgets import (CardWidget, FluentIcon, PrimaryPushButton, ToolButton, 
                           TitleLabel, BodyLabel, SearchLineEdit, ComboBox, MessageBox,
                           InfoBar, InfoBarPosition)

class FamilyManagementInterface(QWidget):
    """家庭管理界面 - 左侧树状结构，右侧上部分家庭列表，下部分家庭详情"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("family_interface")
        self.current_family = None
        self.table = None  # 先声明table属性
        self.setup_ui()
        self.load_sample_tree_data()
        self.load_sample_family_data()
        self.clear_detail_panel()
    
    def setup_ui(self):
        # 主布局 - 水平布局
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建水平分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧树状结构 (占20%)
        self.tree_container = self.create_tree_structure()
        splitter.addWidget(self.tree_container)
        
        # 右侧容器 (占80%)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # 右侧上部 - 家庭列表 (占60%)
        self.family_list_container = self.create_family_list()
        right_layout.addWidget(self.family_list_container, 6)  # 6份高度
        
        # 右侧下部 - 家庭详情 (占40%)
        self.detail_panel = self.create_family_detail_panel()
        right_layout.addWidget(self.detail_panel, 4)  # 4份高度
        
        splitter.addWidget(right_container)
        
        # 设置分割器初始比例
        splitter.setSizes([200, 600])
    
    def create_tree_structure(self):
        """创建左侧树状结构容器"""
        container = CardWidget()
        container.setMinimumWidth(200)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题
        title = TitleLabel("行政区域")
        layout.addWidget(title)
        
        # 搜索框
        self.tree_search = SearchLineEdit()
        self.tree_search.setPlaceholderText("搜索村镇名称...")
        layout.addWidget(self.tree_search)
        
        # 树状结构
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(15)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
            QTreeWidget::item {
                height: 32px;
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        
        # 连接选择信号
        self.tree.itemSelectionChanged.connect(self.on_location_selected)
        layout.addWidget(self.tree, 1)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.add_village_btn = ToolButton(FluentIcon.ADD)
        self.add_village_btn.setToolTip("添加行政村")
        btn_layout.addWidget(self.add_village_btn)
        
        self.add_group_btn = ToolButton(FluentIcon.ADD)
        self.add_group_btn.setToolTip("添加村民小组")
        btn_layout.addWidget(self.add_group_btn)
        
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)
        
        return container
    
    def create_family_list(self):
        """创建右侧上部家庭列表容器"""
        container = CardWidget()
        
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题和操作按钮
        header_layout = QHBoxLayout()
        title = TitleLabel("家庭列表")
        header_layout.addWidget(title)
        
        header_layout.addStretch(1)
        
        self.add_family_btn = PrimaryPushButton("添加家庭")
        self.add_family_btn.setIcon(FluentIcon.ADD)
        header_layout.addWidget(self.add_family_btn)
        layout.addLayout(header_layout)
        
        # 筛选工具栏
        filter_layout = QHBoxLayout()
        self.family_search = SearchLineEdit()
        self.family_search.setPlaceholderText("搜索户主姓名或身份证号")
        filter_layout.addWidget(self.family_search)
        
        filter_layout.addWidget(QLabel("状态:"))
        self.status_combo = ComboBox()
        self.status_combo.addItems(["全部", "正常", "迁出", "注销", "特殊家庭"])
        filter_layout.addWidget(self.status_combo)
        
        filter_layout.addStretch(1)
        layout.addLayout(filter_layout)
        
        # 家庭表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["户主", "身份证号", "家庭人口", "联系电话", "家庭地址", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # 连接选中信号
        self.table.itemSelectionChanged.connect(self.on_family_selected)
        layout.addWidget(self.table, 1)
        
        return container
    
    def create_family_detail_panel(self):
        """创建右侧下部家庭详情面板"""
        panel = CardWidget()
        panel.setMinimumHeight(300)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题和操作按钮
        header_layout = QHBoxLayout()
        self.detail_title = TitleLabel("家庭详情")
        header_layout.addWidget(self.detail_title)
        
        header_layout.addStretch(1)
        
        # 操作按钮
        self.edit_btn = PrimaryPushButton("编辑")
        self.edit_btn.setIcon(FluentIcon.EDIT)
        self.edit_btn.setFixedHeight(36)
        header_layout.addWidget(self.edit_btn)
        
        self.add_member_btn = PrimaryPushButton("添加成员")
        self.add_member_btn.setIcon(FluentIcon.PEOPLE)
        self.add_member_btn.setFixedHeight(36)
        header_layout.addWidget(self.add_member_btn)
        
        self.add_land_btn = PrimaryPushButton("添加土地")
        self.add_land_btn.setIcon(FluentIcon.CERTIFICATE)
        self.add_land_btn.setFixedHeight(36)
        header_layout.addWidget(self.add_land_btn)
        
        layout.addLayout(header_layout)
        
        # 使用标签页展示不同类型的信息
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setStyleSheet("""
            QTabBar::tab {
                height: 36px;
                padding: 0 20px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background-color: #e3f2fd;
                border-bottom: 3px solid #1976d2;
            }
        """)
        
        # 1. 基本信息标签页
        self.basic_info_tab = self.create_basic_info_tab()
        self.tab_widget.addTab(self.basic_info_tab, "基本信息")
        
        # 2. 家庭成员标签页
        self.member_tab = self.create_member_tab()
        self.tab_widget.addTab(self.member_tab, "家庭成员")
        
        # 3. 土地信息标签页
        self.land_tab = self.create_land_tab()
        self.tab_widget.addTab(self.land_tab, "土地信息")
        
        # 4. 补贴信息标签页
        self.subsidy_tab = self.create_subsidy_tab()
        self.tab_widget.addTab(self.subsidy_tab, "补贴信息")
        
        layout.addWidget(self.tab_widget)
        
        return panel

    def create_basic_info_tab(self):
        """创建基本信息标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # 基本信息组
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(10)
        info_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
        
        self.family_id_label = BodyLabel()
        self.householder_label = BodyLabel()
        self.id_card_label = BodyLabel()
        self.phone_label = BodyLabel()
        self.address_label = BodyLabel()
        self.register_date_label = BodyLabel()
        self.status_label = BodyLabel()
        
        info_layout.addRow("家庭编号:", self.family_id_label)
        info_layout.addRow("户主姓名:", self.householder_label)
        info_layout.addRow("身份证号:", self.id_card_label)
        info_layout.addRow("联系电话:", self.phone_label)
        info_layout.addRow("家庭地址:", self.address_label)
        info_layout.addRow("登记日期:", self.register_date_label)
        info_layout.addRow("家庭状态:", self.status_label)
        
        layout.addWidget(info_group)
        
        # 统计信息组
        stats_group = QGroupBox("统计信息")
        stats_layout = QGridLayout(stats_group)
        stats_layout.setSpacing(15)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        
        # 第一行统计卡片
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        
        # 家庭成员卡片
        member_card = self.create_stat_card("家庭成员", "0人", FluentIcon.PEOPLE)
        row1_layout.addWidget(member_card)
        
        # 劳动力卡片
        labor_card = self.create_stat_card("劳动力", "0人", FluentIcon.BASKETBALL)
        row1_layout.addWidget(labor_card)
        
        # 老人卡片
        elder_card = self.create_stat_card("老人", "0人", FluentIcon.HEART)
        row1_layout.addWidget(elder_card)
        
        # 儿童卡片
        child_card = self.create_stat_card("儿童", "0人")
        # child_card = self.create_stat_card("儿童", "0人", FluentIcon.EMOJI)

        row1_layout.addWidget(child_card)
        
        stats_layout.addLayout(row1_layout, 0, 0)
        
        # 第二行统计卡片
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)
        
        # 土地面积卡片
        land_card = self.create_stat_card("土地面积", "0亩", FluentIcon.CERTIFICATE)
        row2_layout.addWidget(land_card)
        
        # 耕地卡片
        farmland_card = self.create_stat_card("耕地", "0亩")
        row2_layout.addWidget(farmland_card)
        
        # 林地卡片
        forest_card = self.create_stat_card("林地", "0亩")
        row2_layout.addWidget(forest_card)
        
        # 补贴金额卡片
        subsidy_card = self.create_stat_card("补贴总额", "¥0" )
        row2_layout.addWidget(subsidy_card)
        
        stats_layout.addLayout(row2_layout, 1, 0)
        
        layout.addWidget(stats_group)
        
        return widget

    def create_stat_card(self, title, value, icon=None):
        """创建统计卡片"""
        card = CardWidget()
        card.setFixedHeight(100)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题和图标
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel()
        # icon_label.setPixmap(icon.pixmap(24, 24))
        title_layout.addWidget(icon_label)
        
        title_label = BodyLabel(title)
        title_label.setStyleSheet("font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch(1)
        
        layout.addLayout(title_layout)
        
        # 数值
        value_label = TitleLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("font-size: 20px; color: #1976d2;")
        layout.addWidget(value_label, 1)
        
        return card

    def create_member_tab(self):
        """创建家庭成员标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # 成员列表表格
        self.member_table = QTableWidget()
        self.member_table.setColumnCount(7)
        self.member_table.setHorizontalHeaderLabels(["姓名", "与户主关系", "性别", "出生日期", "身份证号", "健康状况", "操作"])
        self.member_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.member_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.member_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.member_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.member_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.member_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.member_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.member_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.member_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # 设置样式
        self.member_table.setStyleSheet("""
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
        
        layout.addWidget(self.member_table)
        
        return widget

    def create_land_tab(self):
        """创建土地信息标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # 土地列表表格
        self.land_table = QTableWidget()
        self.land_table.setColumnCount(6)
        self.land_table.setHorizontalHeaderLabels(["地块编号", "土地类型", "面积(亩)", "位置", "确权状态", "操作"])
        self.land_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.land_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.land_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.land_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.land_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.land_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.land_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.land_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
    # 设置样式
        self.land_table.setStyleSheet("""
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
        
        layout.addWidget(self.land_table)
        
        return widget

    def create_subsidy_tab(self):
        """创建补贴信息标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # 补贴列表表格
        self.subsidy_table = QTableWidget()
        self.subsidy_table.setColumnCount(6)
        self.subsidy_table.setHorizontalHeaderLabels(["补贴名称", "补贴年份", "补贴标准", "发放金额", "发放状态", "操作"])
        self.subsidy_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.subsidy_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.subsidy_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.subsidy_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.subsidy_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.subsidy_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.subsidy_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.subsidy_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # 设置样式
        self.subsidy_table.setStyleSheet("""
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
        
        layout.addWidget(self.subsidy_table)
        
        return widget

    def update_detail_panel(self, family_data):
        """更新详情面板显示当前选中的家庭信息"""
        if not family_data:
            return
        # 更新基本信息
        self.family_id_label.setText(family_data.get("id", ""))
        self.householder_label.setText(family_data.get("householder", ""))
        self.id_card_label.setText(family_data.get("id_card", ""))
        self.phone_label.setText(family_data.get("phone", ""))
        self.address_label.setText(family_data.get("address", ""))
        self.register_date_label.setText(family_data.get("register_date", ""))
        
        # 更新状态标签
        status = family_data.get("status", "")
        self.status_label.setText(status)
        if status == "正常":
            self.status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        elif status == "迁出":
            self.status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        elif status == "注销":
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        elif status == "特殊家庭":
            self.status_label.setStyleSheet("color: #9c27b0; font-weight: bold;")
        
        # 更新成员表格
        members = family_data.get("members", [])
        self.member_table.setRowCount(len(members))
        for row, member in enumerate(members):
            self.member_table.setItem(row, 0, QTableWidgetItem(member.get("name", "")))
            self.member_table.setItem(row, 1, QTableWidgetItem(member.get("relation", "")))
            self.member_table.setItem(row, 2, QTableWidgetItem(member.get("gender", "")))
            self.member_table.setItem(row, 3, QTableWidgetItem(member.get("birth", "")))
            self.member_table.setItem(row, 4, QTableWidgetItem(member.get("id_card", "")))
            self.member_table.setItem(row, 5, QTableWidgetItem(member.get("health", "")))
        
        # 更新土地表格
        lands = family_data.get("lands", [])
        self.land_table.setRowCount(len(lands))
        for row, land in enumerate(lands):
            self.land_table.setItem(row, 0, QTableWidgetItem(land.get("id", "")))
            self.land_table.setItem(row, 1, QTableWidgetItem(land.get("type", "")))
            self.land_table.setItem(row, 2, QTableWidgetItem(str(land.get("area", 0)) + "亩"))
            self.land_table.setItem(row, 3, QTableWidgetItem(land.get("location", "")))
            self.land_table.setItem(row, 4, QTableWidgetItem(land.get("status", "")))
        
        # 更新补贴表格
        subsidies = family_data.get("subsidies", [])
        self.subsidy_table.setRowCount(len(subsidies))
        for row, subsidy in enumerate(subsidies):
            self.subsidy_table.setItem(row, 0, QTableWidgetItem(subsidy.get("name", "")))
            self.subsidy_table.setItem(row, 1, QTableWidgetItem(subsidy.get("year", "")))
            self.subsidy_table.setItem(row, 2, QTableWidgetItem(subsidy.get("standard", "")))
            self.subsidy_table.setItem(row, 3, QTableWidgetItem(subsidy.get("amount", "")))
            self.subsidy_table.setItem(row, 4, QTableWidgetItem(subsidy.get("status", "")))
        
    def load_sample_tree_data(self):
        """加载示例树状数据"""
        self.tree.clear()
        
        # 添加镇级节点
        town1 = QTreeWidgetItem(["青阳镇"])
        town1.setIcon(0, QIcon(FluentIcon.HOME.icon()))
        
        # 添加村级节点
        village1 = QTreeWidgetItem(["青阳村"])
        village1.setIcon(0, QIcon(FluentIcon.TAG.icon()))
        
        village2 = QTreeWidgetItem(["向阳村"])
        village2.setIcon(0, QIcon(FluentIcon.TAG.icon()))
        
        # 添加组级节点
        group1 = QTreeWidgetItem(["一组"])
        group1.setIcon(0, QIcon(FluentIcon.PEOPLE.icon()))
        
        group2 = QTreeWidgetItem(["二组"])
        group2.setIcon(0, QIcon(FluentIcon.PEOPLE.icon()))
        
        # 构建树状结构
        town1.addChild(village1)
        town1.addChild(village2)
        village1.addChild(group1)
        village1.addChild(group2)
        
        self.tree.addTopLevelItem(town1)
        self.tree.expandAll()
    
    def load_sample_family_data(self):
        """加载示例家庭数据"""
        if not hasattr(self, 'table') or self.table is None:
            return
            
        families = [
            {
                "householder": "张三", "id_card": "320523198503124512",
                "members": "4人", "phone": "13800138000",
                "address": "青阳镇青阳村一组", "status": "正常"
            },
            {
                "householder": "李四", "id_card": "320523197812054215",
                "members": "3人", "phone": "13900139000",
                "address": "青阳镇青阳村一组", "status": "正常"
            }
        ]
        
        self.table.setRowCount(len(families))
        
        for row, family in enumerate(families):
            self.table.setItem(row, 0, QTableWidgetItem(family["householder"]))
            self.table.setItem(row, 1, QTableWidgetItem(family["id_card"]))
            self.table.setItem(row, 2, QTableWidgetItem(family["members"]))
            self.table.setItem(row, 3, QTableWidgetItem(family["phone"]))
            self.table.setItem(row, 4, QTableWidgetItem(family["address"]))
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            view_btn = ToolButton(FluentIcon.VIEW)
            btn_layout.addWidget(view_btn)
            
            edit_btn = ToolButton(FluentIcon.EDIT)
            btn_layout.addWidget(edit_btn)
            
            self.table.setCellWidget(row, 5, btn_widget)
    
    def on_location_selected(self):
        """当选择树状结构中的位置时"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            print(f"选择了: {selected_items[0].text(0)}")
            # 这里应该根据选择的位置筛选家庭列表
            self.load_sample_family_data()
    
    def on_family_selected(self):
        """当家庭被选中时更新详情面板"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.clear_detail_panel()
            return
        
        # 获取选中行的第一列（户主姓名）
        row = selected_items[0].row()
        householder = self.table.item(row, 0).text()
        
        # 构造家庭数据字典
        family_data = {
            "id": "F2023" + str(row+1).zfill(3),
            "householder": householder,
            "id_card": self.table.item(row, 1).text(),
            "phone": self.table.item(row, 3).text(),
            "address": self.table.item(row, 4).text(),
            "register_date": "2023-01-15",  # 示例数据
            "status": self.table.item(row, 2).text().replace("人", ""),  # 从"3人"中提取状态
            "members": [
                {"name": householder, "relation": "户主", "gender": "男", 
                "birth": "1985-03-12", "id_card": self.table.item(row, 1).text(), "health": "健康"},
                {"name": "张妻", "relation": "配偶", "gender": "女", 
                "birth": "1987-05-23", "id_card": "320523198705234512", "health": "健康"}
            ],
            "lands": [
                {"id": "L001", "type": "耕地", "area": 5.2, 
                "location": "青阳村一组东区", "status": "已确权"}
            ],
            "subsidies": [
                {"name": "粮食直补", "year": "2023", "standard": "¥150/亩", 
                "amount": "¥780", "status": "已发放"}
            ]
        }
        
        # 调用更新方法
        self.update_detail_panel(family_data)

    def clear_detail_panel(self):
        """清空详情面板"""
        self.detail_title.setText("家庭详情")
        self.family_id_label.setText("")
        self.householder_label.setText("")
        self.member_table.setRowCount(0)



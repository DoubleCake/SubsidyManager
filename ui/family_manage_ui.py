# ui/family_manage_ui.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLabel,QFrame,QFormLayout
from PySide6.QtCore import Qt
from qfluentwidgets import LineEdit, CardWidget, PrimaryPushButton, SubtitleLabel, MessageBox,Dialog,setFont, LineEdit, PushButton, TableWidget
from services.family_service import FamilyService



class FamilyManageUI(QFrame):
    PAGE_SIZE = 10  # 每页显示的数据条数
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        # self.label = SubtitleLabel(text, self)
        self.setObjectName(text.replace(' ', '-'))
        self.service = FamilyService()
        self.current_page = 1
        self.total_pages = 1
        self.col_names = ["家庭ID","户主名称","身份证号","联系方式","总承包面积(亩)","村","组","家庭人数"]
        self.init_ui()
        self.load_data()


    def init_ui(self):
        layout = QVBoxLayout(self)

        # 标题区域
        title_card = CardWidget()
        title_layout = QHBoxLayout()
        self.titleLabel = SubtitleLabel("家庭信息管理")
        self.refreshButton = PushButton("刷新")
        self.refreshButton.clicked.connect(self.load_data)
        title_layout.addWidget(self.titleLabel, alignment=Qt.AlignLeft)
        title_layout.addWidget(self.refreshButton, alignment=Qt.AlignRight)
        title_card.setLayout(title_layout)

        # 搜索栏
        search_card = CardWidget()
        search_layout = QHBoxLayout()
        self.searchInput = LineEdit()
        self.searchInput.setPlaceholderText("请输入户主ID或土地ID进行搜索...")
        self.searchButton = PrimaryPushButton("搜索")
        self.searchButton.clicked.connect(self.search_family)
        search_layout.addWidget(QLabel("搜索："))
        search_layout.addWidget(self.searchInput, stretch=3)
        search_layout.addWidget(self.searchButton, stretch=1)
        search_card.setLayout(search_layout)

        # 表格区域
        table_card = CardWidget()
        table_layout = QVBoxLayout()
        self.table = TableWidget()
        self.table.setColumnCount(len(self.col_names))
        self.table.setHorizontalHeaderLabels(self.col_names)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        # 特定列设置
        for i in range(self.table.columnCount()):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)  # 所有列统一宽度

        table_layout.addWidget(self.table)
        table_card.setLayout(table_layout)

        # 分页和新增按钮
        footer_card = CardWidget()
        footer_layout = QHBoxLayout()
        self.prevButton = QPushButton("上一页")
        self.pageLabel = QLabel("第 1 页")
        self.nextButton = QPushButton("下一页")
        self.addButton = PrimaryPushButton("新增家庭")

        self.prevButton.clicked.connect(self.prev_page)
        self.nextButton.clicked.connect(self.next_page)
        self.addButton.clicked.connect(self.open_add_dialog)

        footer_layout.addWidget(self.prevButton)
        footer_layout.addWidget(self.pageLabel)
        footer_layout.addWidget(self.nextButton)
        footer_layout.addWidget(self.addButton, alignment=Qt.AlignRight)
        footer_card.setLayout(footer_layout)

        # 组装整体布局
        layout.addWidget(title_card)
        layout.addWidget(search_card)
        layout.addWidget(table_card)
        layout.addWidget(footer_card)

    def load_data(self, page=1):
        self.current_page = page
        data = self.service.get_all_families_paginated(page, self.PAGE_SIZE)
        self.total_pages = (len(data) + self.PAGE_SIZE - 1) // self.PAGE_SIZE+1  # 简单计算总页数（实际应由后端返回）
        print(f"total_pages: {self.total_pages},data:f{len(data)}")
        self.table.setRowCount(len(data))
        for row, family in enumerate(data):

            self.table.setItem(row, 0, QTableWidgetItem(str(family["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(str(family["head_name"])))
            self.table.setItem(row, 2, QTableWidgetItem(str(family["head_idcard"])))
            self.table.setItem(row, 3, QTableWidgetItem(str(family["head_phone"])))
            self.table.setItem(row, 4, QTableWidgetItem(str(family["land_area"])))
            self.table.setItem(row, 5, QTableWidgetItem(str(family["village_name"])))
            self.table.setItem(row, 6, QTableWidgetItem(str(family["group_number"])))
            self.table.setItem(row, 7, QTableWidgetItem(str(family["member_count"])))

            # 操作按钮
            # action_layout = QHBoxLayout()
            # edit_btn = QPushButton("编辑")
            # delete_btn = QPushButton("删除")
            # edit_btn.clicked.connect(lambda _, fid=family["id"]: self.edit_family(fid))
            # delete_btn.clicked.connect(lambda _, fid=family["id"]: self.delete_family(fid))

            # action_widget = QWidget()
            # action_layout.addWidget(edit_btn)
            # action_layout.addWidget(delete_btn)
            # action_layout.setContentsMargins(0, 0, 0, 0)
            # action_widget.setLayout(action_layout)
            # self.table.setCellWidget(row, 4, action_widget)

        self.update_page_label()

    def update_page_label(self):
        self.pageLabel.setText(f"第 {self.current_page} 页 / 共 {self.total_pages} 页")

    def prev_page(self):
        if self.current_page > 1:
            self.load_data(self.current_page - 1)

    def next_page(self):
        if self.current_page < self.total_pages:
            self.load_data(self.current_page + 1)

    def search_family(self):
        keyword = self.searchInput.text()
        results = self.service.search_family(keyword)
        self.display_search_results(results)

    def display_search_results(self, results):
        self.table.setRowCount(len(results))
        for row, family in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(str(family["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(str(family["land_id"])))
            self.table.setItem(row, 2, QTableWidgetItem(str(family["head_id"])))
            member_count = len(family.get("members", []))
            self.table.setItem(row, 3, QTableWidgetItem(str(member_count)))

            # 操作按钮
            action_layout = QHBoxLayout()
            edit_btn = QPushButton("编辑")
            delete_btn = QPushButton("删除")
            edit_btn.clicked.connect(lambda _, fid=family["id"]: self.edit_family(fid))
            delete_btn.clicked.connect(lambda _, fid=family["id"]: self.delete_family(fid))

            action_widget = QWidget()
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row, 4, action_widget)

    def open_add_dialog(self):
        dialog = FamilyEditDialog(service=self.service, parent=self)
        if dialog.exec_():
            self.load_data(self.current_page)

    def edit_family(self, family_id):
        dialog = FamilyEditDialog(service=self.service, family_id=family_id, parent=self)
        if dialog.exec_():
            self.load_data(self.current_page)

    def delete_family(self, family_id):
        w = MessageBox("确认删除", f"确定要删除 ID 为 {family_id} 的家庭吗？", self)
        if w.exec_():
            self.service.delete_family(family_id)
            self.load_data(self.current_page)


class FamilyEditDialog(Dialog):
    def __init__(self, service, family_id=None, parent=None):
        title = "新增家庭" if family_id is None else "编辑家庭"
        super().__init__(title, "", parent)
        self.service = service
        self.family_id = family_id

        self.init_ui()
        if family_id:
            self.load_data(family_id)

    def init_ui(self):
        card = CardWidget()
        card.setTitle("家庭信息")
        form_layout = QFormLayout(card)

        self.land_id_input = LineEdit()
        self.head_id_input = LineEdit()
        self.member_ids_input = LineEdit()
        self.land_ids_input = LineEdit()

        form_layout.addRow("主土地ID：", self.land_id_input)
        form_layout.addRow("户主ID：", self.head_id_input)
        form_layout.addRow("成员ID列表（逗号分隔）：", self.member_ids_input)
        form_layout.addRow("所有土地ID列表（逗号分隔）：", self.land_ids_input)

        self.viewLayout.addWidget(card)

        self.yesButton.setText("保存")
        self.cancelButton.setText("取消")

    def load_data(self, family_id):
        family = self.service.get_family(family_id)
        if family:
            self.land_id_input.setText(str(family["land_id"]))
            self.head_id_input.setText(str(family["head_id"]))
            self.member_ids_input.setText(",".join(map(str, family["members"])))
            self.land_ids_input.setText(",".join(map(str, [family["land_id"]] + family.get("lands", []))))

    def done(self, result):
        if result == Dialog.Accepted:
            land_id = int(self.land_id_input.text())
            head_id = int(self.head_id_input.text())
            member_ids = list(map(int, self.member_ids_input.text().split(',')))
            land_ids = list(map(int, self.land_ids_input.text().split(',')))

            try:
                if self.family_id:
                    self.service.update_family(self.family_id, land_id, head_id, member_ids, land_ids)
                else:
                    self.service.create_family(land_id, head_id, member_ids, land_ids)
                super().done(result)
            except Exception as e:
                MessageBox("错误", str(e), self).exec_()
        else:
            super().done(result)
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox, 
                              QLineEdit, QSpinBox, QDateEdit, QCheckBox, 
                              QTextEdit, QGroupBox, QHBoxLayout, 
                              QApplication, QSizePolicy, QLabel)
from qfluentwidgets import (InfoBar, InfoBarPosition, CheckBox, TitleLabel, 
                           setFont, MessageBox, CardWidget, PrimaryPushButton,PushButton,
                           BodyLabel, DoubleSpinBox, FluentIcon)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QCloseEvent
from services.subsidy_service import SubsidyService

class SubsidyTypeEditWindow(QWidget):
    """补贴类型创建/编辑窗口"""
    data_saved = Signal(dict)  # 数据保存信号
    
    def __init__(self, service: SubsidyService, subsidy_id=None, parent=None):
        """
        初始化补贴类型编辑窗口
        
        参数:
            service: 补贴服务对象
            subsidy_id: 要编辑的补贴类型ID，None表示新建
            parent: 父窗口
        """
        super().__init__(parent)
        self.service = service
        self.subsidy_id = subsidy_id
        
        self.setWindowTitle("创建补贴类型" if subsidy_id is None else "编辑补贴类型")
        self.setMinimumSize(600, 700)
        self.setWindowModality(Qt.ApplicationModal)  # 设置为模态窗口
        
        self.init_ui()
        
        if subsidy_id:
            self.load_data(subsidy_id)
    
    def init_ui(self):
        """初始化UI界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题区域
        title_layout = QHBoxLayout()
        title_label = TitleLabel(self.windowTitle())
        setFont(title_label, 16)
        
        title_layout.addWidget(QLabel())
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)
        
        # 创建表单卡片
        form_card = self.create_form()
        main_layout.addWidget(form_card, 1)  # 1 表示占据剩余空间
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.save_button = PrimaryPushButton(FluentIcon.SAVE, "保存")
        self.cancel_button = PushButton(FluentIcon.CLOSE, "取消")
        
        button_layout.addStretch(1)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        
        # 连接信号
        self.save_button.clicked.connect(self.validate_and_save)
        self.cancel_button.clicked.connect(self.close)
    
    def create_form(self):
        """创建表单内容"""
        form_card = CardWidget()
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        # 基本信息部分
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(10)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入补贴名称（如：农业补贴）")
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("输入补贴代码（如：AGRI-2024）")
        
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(QDate.currentDate().year())
        
        info_layout.addRow("补贴名称:", self.name_input)
        info_layout.addRow("补贴代码:", self.code_input)
        info_layout.addRow("适用年份:", self.year_spin)
        
        # 金额设置部分
        amount_group = QGroupBox("补贴金额设置")
        amount_layout = QFormLayout(amount_group)
        amount_layout.setSpacing(10)
        
        self.amount_type_combo = QComboBox()
        self.amount_type_combo.addItems(["固定金额", "按面积计算", "按人数计算"])
        self.amount_type_combo.currentIndexChanged.connect(self.update_amount_fields)
        
        self.amount_spin = DoubleSpinBox()
        self.amount_spin.setPrefix("¥ ")
        self.amount_spin.setRange(0, 100000)
        self.amount_spin.setValue(0)
        
        self.unit_amount_spin = DoubleSpinBox()
        self.unit_amount_spin.setPrefix("¥ ")
        self.unit_amount_spin.setRange(0, 1000)
        self.unit_amount_spin.setValue(100)
        self.unit_amount_spin.setVisible(False)
        
        self.unit_label = BodyLabel("元/亩")
        self.unit_label.setVisible(False)
        
        amount_layout.addRow("金额类型:", self.amount_type_combo)
        amount_layout.addRow("固定金额:", self.amount_spin)
        amount_layout.addRow("单位金额:", self.unit_amount_spin)
        amount_layout.addRow("单位说明:", self.unit_label)
        
        # 规则设置部分
        rule_group = QGroupBox("补贴规则设置")
        rule_layout = QVBoxLayout(rule_group)
        rule_layout.setSpacing(10)
        
        rule_form = QFormLayout()
        rule_form.setSpacing(10)
        
        self.mutual_exclusive_cb = CheckBox("是否互斥")
        self.allow_multiple_cb = CheckBox("允许多次申请")
        self.active_cb = CheckBox("是否激活")
        self.active_cb.setChecked(True)
        
        # 互斥规则选择
        self.conflict_combo = QComboBox()
        self.conflict_combo.addItem("无互斥规则", None)
        self.conflict_combo.setVisible(False)
        
        # 申请条件
        self.condition_input = QTextEdit()
        self.condition_input.setPlaceholderText("输入申请条件（如：需拥有至少5亩耕地）")
        self.condition_input.setMaximumHeight(80)
        
        rule_form.addRow("互斥规则:", self.mutual_exclusive_cb)
        rule_form.addRow("冲突补贴:", self.conflict_combo)
        rule_form.addRow("多次申请:", self.allow_multiple_cb)
        rule_form.addRow("激活状态:", self.active_cb)
        
        rule_layout.addLayout(rule_form)
        rule_layout.addWidget(QLabel("申请条件:"))
        rule_layout.addWidget(self.condition_input)
        
        # 有效期设置
        validity_group = QGroupBox("有效期设置")
        validity_layout = QFormLayout(validity_group)
        validity_layout.setSpacing(10)
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setDate(QDate.currentDate())
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setDate(QDate.currentDate().addYears(1))
        
        validity_layout.addRow("开始日期:", self.start_date_edit)
        validity_layout.addRow("结束日期:", self.end_date_edit)
        
        # 添加到主表单
        form_layout.addWidget(info_group)
        form_layout.addWidget(amount_group)
        form_layout.addWidget(rule_group)
        form_layout.addWidget(validity_group)
        
        # 连接信号
        self.mutual_exclusive_cb.stateChanged.connect(
            lambda state: self.conflict_combo.setVisible(state == Qt.Checked)
        )
        
        return form_card
    
    def update_amount_fields(self, index):
        """根据金额类型更新显示字段"""
        # 0=固定金额, 1=按面积计算, 2=按人数计算
        if index == 0:  # 固定金额
            self.amount_spin.setVisible(True)
            self.unit_amount_spin.setVisible(False)
            self.unit_label.setVisible(False)
        else:  # 按面积或人数计算
            self.amount_spin.setVisible(False)
            self.unit_amount_spin.setVisible(True)
            self.unit_label.setVisible(True)
            self.unit_label.setText("元/亩" if index == 1 else "元/人")
    
    def load_data(self, subsidy_id):
        """加载补贴类型数据"""
        data = self.service.get_subsidy_type(subsidy_id)
        if not data:
            MessageBox("错误", f"找不到ID为{subsidy_id}的补贴类型", self).exec_()
            self.close()
            return
        
        # 填充表单数据
        self.name_input.setText(data.get("name", ""))
        self.code_input.setText(data.get("code", ""))
        self.year_spin.setValue(data.get("year", QDate.currentDate().year()))
        
        # 金额设置
        amount_type = data.get("amount_type", 0)
        self.amount_type_combo.setCurrentIndex(amount_type)
        if amount_type == 0:
            self.amount_spin.setValue(data.get("amount", 0))
        else:
            self.unit_amount_spin.setValue(data.get("unit_amount", 100))
        
        # 规则设置
        self.mutual_exclusive_cb.setChecked(data.get("is_mutual_exclusive", False))
        self.allow_multiple_cb.setChecked(data.get("allow_multiple", False))
        self.active_cb.setChecked(data.get("is_active", True))
        self.condition_input.setText(data.get("conditions", ""))
        
        # 有效期
        start_date = data.get("start_date", QDate.currentDate())
        end_date = data.get("end_date", QDate.currentDate().addYears(1))
        self.start_date_edit.setDate(start_date)
        self.end_date_edit.setDate(end_date)
        
        # 加载互斥规则选项
        self.load_conflict_options(data.get("conflict_id"))
    
    def load_conflict_options(self, selected_id=None):
        """加载互斥规则选项"""
        self.conflict_combo.clear()
        self.conflict_combo.addItem("无互斥规则", None)
        
        # 获取所有补贴类型（排除当前编辑的）
        subsidy_types = self.service.get_all_subsidy_types()
        for st in subsidy_types:
            if self.subsidy_id and st["id"] == self.subsidy_id:
                continue
            self.conflict_combo.addItem(f"{st['name']} ({st['code']})", st["id"])
        
        # 设置选中的项目
        if selected_id:
            for i in range(self.conflict_combo.count()):
                if self.conflict_combo.itemData(i) == selected_id:
                    self.conflict_combo.setCurrentIndex(i)
                    break
    
    def get_form_data(self):
        """从表单获取数据"""
        data = {
            "name": self.name_input.text().strip(),
            "code": self.code_input.text().strip(),
            "year": self.year_spin.value(),
            "amount_type": self.amount_type_combo.currentIndex(),
            "amount": self.amount_spin.value(),
            "unit_amount": self.unit_amount_spin.value(),
            "is_mutual_exclusive": self.mutual_exclusive_cb.isChecked(),
            "conflict_id": self.conflict_combo.currentData(),
            "allow_multiple": self.allow_multiple_cb.isChecked(),
            "is_active": self.active_cb.isChecked(),
            "conditions": self.condition_input.toPlainText().strip(),
            "start_date": self.start_date_edit.date(),
            "end_date": self.end_date_edit.date()
        }
        return data
    
    def validate_and_save(self):
        """验证并保存数据"""
        data = self.get_form_data()
        
        # 验证数据
        if not data["name"]:
            self.show_error("错误", "补贴名称不能为空")
            return
            
        if not data["code"]:
            self.show_error("错误", "补贴代码不能为空")
            return
            
        if data["start_date"] > data["end_date"]:
            self.show_error("错误", "开始日期不能晚于结束日期")
            return
            
        if data["amount_type"] == 0 and data["amount"] <= 0:
            self.show_error("错误", "固定金额必须大于0")
            return
            
        if data["amount_type"] > 0 and data["unit_amount"] <= 0:
            unit = "亩" if data["amount_type"] == 1 else "人"
            self.show_error("错误", f"单位金额（元/{unit}）必须大于0")
            return
        
        # 保存数据
        try:
            if self.subsidy_id:
                result = self.service.update_subsidy_type(self.subsidy_id, data)
                self.show_success("成功", "补贴类型更新成功")
            else:
                result = self.service.create_subsidy_type(data)
                self.show_success("成功", "补贴类型创建成功")
                self.subsidy_id = result["id"]
            
            # 发送保存信号
            self.data_saved.emit(result)
            
            # 关闭窗口
            self.close()
            
        except Exception as e:
            self.show_error("错误", f"保存失败: {str(e)}")
    
    def show_error(self, title, content):
        """显示错误信息"""
        InfoBar.error(
            title, content,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
    
    def show_success(self, title, content):
        """显示成功信息"""
        InfoBar.success(
            title, content,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
    
    def closeEvent(self, event: QCloseEvent):
        """关闭窗口事件"""
        # 可以在这里添加关闭前的确认逻辑
        super().closeEvent(event)
# ui/rule_manage_window.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                               QPushButton, QLabel, QCheckBox, QGroupBox)
from qfluentwidgets import (FluentWindow, TitleLabel, PrimaryPushButton, MessageBox)
import json
from pathlib import Path

class RuleManageWindow(QWidget):
    """补贴规则管理窗口（内嵌在 SubsidyTypeEditWindow 中）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 400)
        self.init_ui()
        self.load_rules()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 补贴列表
        self.subsidy_list = QListWidget()
        self.subsidy_list.itemChanged.connect(self.on_checkbox_changed)
        
        # 规则表
        self.rule_table = QListWidget()
        
        # 按钮
        btn_layout = QHBoxLayout()
        add_btn = PrimaryPushButton("＋ 新增规则")
        del_btn = PrimaryPushButton("－ 删除规则")
        save_btn = PrimaryPushButton("保存并热加载")
        
        add_btn.clicked.connect(self.add_rule)
        del_btn.clicked.connect(self.del_rule)
        save_btn.clicked.connect(self.save_and_reload)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        
        layout.addWidget(QLabel("补贴列表："))
        layout.addWidget(self.subsidy_list)
        layout.addWidget(QLabel("冲突/叠加规则："))
        layout.addWidget(self.rule_table)
        layout.addLayout(btn_layout)
    
    def load_rules(self):
        """从 JSON 加载规则"""
        rules_file = Path("config/subsidy_rules.json")
        if rules_file.exists():
            self.rules = json.loads(rules_file.read_text(encoding="utf-8"))
        else:
            self.rules = []
        
        self.refresh_subsidy_list()
        self.refresh_rule_table()
    
    def refresh_subsidy_list(self):
        self.subsidy_list.clear()
        for r in self.rules:
            item = QListWidgetItem(r["name"])
            item.setCheckState(Qt.Checked if r["is_activate"] else Qt.Unchecked)
            item.setData(Qt.UserRole, r)
            self.subsidy_list.addItem(item)
    
    def refresh_rule_table(self):
        self.rule_table.clear()
        for r in self.rules:
            if r.get("exclusive_group"):
                for ex in r["exclusive_group"]:
                    self.rule_table.addItem(f"{r['name']} ❌ {self._find_name(ex)}")
            if r.get("stack_group"):
                for st in r["stack_group"]:
                    self.rule_table.addItem(f"{r['name']} 🔄 {self._find_name(st)}")
    
    def on_checkbox_changed(self, item):
        rule = item.data(Qt.UserRole)
        rule["is_activate"] = item.checkState() == Qt.Checked
    
    def add_rule(self):
        """弹窗新增/编辑规则"""
        # 简化：直接弹出一个 QMessageBox 输入
        name, ok = MessageBox().getText(self, "新增规则", "规则描述：")
        if ok and name:
            self.rules.append({
                "id": f"RULE_{len(self.rules)+1}",
                "name": name,
                "amount": 0,
                "unit": "亩",
                "allow_multiple": False,
                "exclusive_group": [],
                "stack_group": []
            })
            self.refresh_subsidy_list()
    
    def del_rule(self):
        """删除选中的规则"""
        row = self.rule_table.currentRow()
        if row < 0:
            return
        self.rule_table.takeItem(row)
        # 实际删除逻辑：根据描述解析出左右补贴并移除
        # （这里用简化示例）
    
    def save_and_reload(self):
        """保存 JSON 并热加载"""
        Path("config").mkdir(exist_ok=True)
        Path("config/subsidy_rules.json").write_text(
            json.dumps(self.rules, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        # 热加载：通知 RuleLoader
        from engine.rule_loader import RuleLoader
        RuleLoader.reload()
        
        MessageBox.info(self, "成功", "规则已保存并立即生效！")
    
    def _find_name(self, rule_id):
        return next((r["name"] for r in self.rules if r["id"] == rule_id), rule_id)
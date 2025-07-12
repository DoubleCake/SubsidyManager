from services.family_service import FamilyService
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
                             QDateEdit, QMessageBox, QHeaderView, QFormLayout, QGroupBox, QSplitter)
from PyQt5.QtCore import Qt, QDate

class FamilyController:
    def __init__(self, view):
        self.view = view
        self.service = FamilyService()

    def add_family(self):
        try:
            data = self.view.get_family_form_data()
            success = self.service.add_family(**data)
            if success:
                self.view.show_success("家庭添加成功")
                self.view.clear_form(
                    self.view.family_id_input,
                    self.view.family_address_input,
                    self.view.family_income_input,
                    self.view.family_members_input
                )
                self.view.load_families()
            else:
                self.view.show_warning("添加失败，请检查数据是否重复")
        except Exception as e:
            self.view.show_error(f"发生错误：{str(e)}")

    def update_family(self):
        selected_row = self.view.family_table.currentRow()
        if selected_row < 0:
            self.view.show_warning("请先选择一个家庭进行更新")
            return

        try:
            data = self.view.get_family_form_data()
            success = self.service.update_family(**data)
            if success:
                self.view.show_success("家庭信息更新成功")
                self.view.clear_form(
                    self.view.family_id_input,
                    self.view.family_address_input,
                    self.view.family_income_input,
                    self.view.family_members_input
                )
                self.view.load_families()
            else:
                self.view.show_warning("更新失败，请重试")
        except Exception as e:
            self.view.show_error(f"发生错误：{str(e)}")

    def delete_family(self):
        selected_row = self.view.family_table.currentRow()
        if selected_row < 0:
            self.view.show_warning("请先选择一个家庭进行删除")
            return

        family_id = self.view.family_table.item(selected_row, 0).text()
        confirm = QMessageBox.question(self.view, "确认删除", f"确定要删除家庭 {family_id} 吗？",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                success = self.service.delete_family(family_id)
                if success:
                    self.view.show_success("家庭删除成功")
                    self.view.load_families()
                else:
                    self.view.show_warning("删除失败，请重试")
            except Exception as e:
                self.view.show_error(f"发生错误：{str(e)}")
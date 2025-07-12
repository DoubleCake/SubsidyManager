from services.subsidy_service import SubsidyService


class SubsidyController:
    def __init__(self, view):
        self.view = view
        self.service = SubsidyService()

    def add_subsidy(self):
        try:
            data = self.view.get_subsidy_form_data()
            success = self.service.add_subsidy(**data)
            if success:
                self.view.show_success("补贴发放成功")
                self.view.clear_form(
                    self.view.subsidy_amount_input,
                    self.view.subsidy_issue_date
                )
                self.view.load_subsidies()
            else:
                self.view.show_warning("发放失败，请检查数据是否重复")
        except Exception as e:
            self.view.show_error(f"发生错误：{str(e)}")

    def update_subsidy(self):
        selected_row = self.view.subsidy_table.currentRow()
        if selected_row < 0:
            self.view.show_warning("请先选择一条补贴记录进行更新")
            return

        subsidy_id = self.view.subsidy_table.item(selected_row, 0).text()
        try:
            data = self.view.get_subsidy_form_data()
            success = self.service.update_subsidy(subsidy_id=subsidy_id, **data)
            if success:
                self.view.show_success("补贴信息更新成功")
                self.view.load_subsidies()
            else:
                self.view.show_warning("更新失败，请重试")
        except Exception as e:
            self.view.show_error(f"发生错误：{str(e)}")
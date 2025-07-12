from services.report_service import PersonService

class PersonController:
    def __init__(self, view):
        self.view = view
        self.service = PersonService()

    def add_person(self):
        data = self.view.get_person_form_data()
        if not self._validate_person_data(data):
            return False

        try:
            success = self.service.add_person(**data)
            if success:
                self.view.show_success("人员添加成功")
                self.view.clear_person_form()
                self.view.load_persons()
            else:
                self.view.show_warning("添加失败，请检查数据是否重复")
            return success
        except Exception as e:
            self.view.show_error(f"发生错误：{str(e)}")
            return False

    def update_person(self):
        selected_person_id = self.view.get_selected_person_id()
        if not selected_person_id:
            self.view.show_warning("请先选择一个人员进行更新")
            return False

        data = self.view.get_person_form_data()
        try:
            success = self.service.update_person(person_id=selected_person_id, **data)
            if success:
                self.view.show_success("人员信息更新成功")
                self.view.clear_person_form()
                self.view.load_persons()
            else:
                self.view.show_warning("更新失败，请重试")
            return success
        except Exception as e:
            self.view.show_error(f"发生错误：{str(e)}")
            return False

    def _validate_person_data(self, data):
        if not all([data['family_id'], data['person_id'], data['name']]):
            self.view.show_warning("家庭ID、身份证号和姓名为必填项")
            return False
        return True
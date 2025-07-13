# services/subsidy_service.py

from models.subsidy_model import SubsidyDAO


class SubsidyService:
    def __init__(self):
        self.dao = SubsidyDAO()

    def get_all_subsidies(self):
        """
        获取所有补贴类型
        :return: 字典列表
        """
        return self.dao.get_all_subsidies()

    def search_subsidies(self, name=""):
        """
        按名称搜索补贴类型
        :param name: 名称关键字
        :return: 字典列表
        """
        return self.dao.search_subsidies(name)

    def add_subsidy(self, name, amount=0.0, year=None, description="", land_type="", is_mutual_exclusive=False):
        """
        添加新的补贴类型
        :param name: 补贴名称
        :param amount: 补贴金额
        :param year: 年份
        :param description: 描述
        :param land_type: 土地属性
        :param is_mutual_exclusive: 是否互斥
        :return: 成功与否
        """
        return self.dao.add_subsidy(name, amount, year, description, land_type, is_mutual_exclusive)

    def update_subsidy(self, subsidy_id, **kwargs):
        """
        更新补贴信息
        :param subsidy_id: 补贴ID
        :param kwargs: 可变参数（name, amount, year, description, land_type, is_mutual_exclusive）
        :return: 成功与否
        """
        return self.dao.update_subsidy(subsidy_id, **kwargs)

    def delete_subsidy(self, subsidy_id):
        """
        删除指定ID的补贴
        :param subsidy_id: 补贴ID
        :return: 成功与否
        """
        return self.dao.delete_subsidy(subsidy_id)
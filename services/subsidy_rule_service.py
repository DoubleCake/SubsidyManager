from models.subsidy_rule_dao import SubsidyRuleDAO


class SubsidyRuleService:
    def __init__(self):
        self.dao = SubsidyRuleDAO()

    def add_rule(self, name, a_id, b_id, relation, desc=""):
        return self.dao.add_rule(name, a_id, b_id, relation, desc)

    def delete_rule(self, rule_id):
        return self.dao.delete_rule(rule_id)

    def update_rule(self, rule_id, **kwargs):
        return self.dao.update_rule(rule_id, **kwargs)

    def list_rules(self, **filters):
        return self.dao.search_rules(**filters)
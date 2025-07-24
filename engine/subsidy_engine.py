# engine/subsidy_engine.py
from engine.rule_loader import RuleLoader

class SubsidyEngine:
    @staticmethod
    def eligible(person, land_area):
        """返回该人可享补贴列表"""
        rules = RuleLoader.subsidy_rules()
        ok = []
        for r in rules:
            if r.age_min and person.age < r.age_min:
                continue
            if r.land_require and person.land_type != r.land_require:
                continue
            ok.append(r)
        return ok

    @staticmethod
    def conflicts(subsidy_ids):
        """检查给定补贴是否有冲突"""
        conflicts = RuleLoader.conflict_rules()
        for c in conflicts:
            if c.left in subsidy_ids and c.right in subsidy_ids:
                return c
        return None
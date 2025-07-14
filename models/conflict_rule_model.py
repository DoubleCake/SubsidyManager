# models/conflict_rule.py
from database import execute_query

class ConflictRuleDAO:
    def __init__(self, db_path='family_subsidies.db'):
        self.db_path = db_path
    
    def add_conflict_rule(self, subsidy_id, conflicting_subsidy_id, description=None):
        """添加冲突规则"""
        # 检查补贴类型是否存在
        subsidy_exists = execute_query(
            self.db_path,
            "SELECT 1 FROM subsidy_type WHERE subsidy_id = ?",
            (subsidy_id,),
            fetch=True
        )
        conflicting_exists = execute_query(
            self.db_path,
            "SELECT 1 FROM subsidy_type WHERE subsidy_id = ?",
            (conflicting_subsidy_id,),
            fetch=True
        )
        
        if not subsidy_exists or not conflicting_exists:
            raise ValueError("补贴类型不存在")
        
        return execute_query(
            self.db_path,
            '''INSERT INTO conflict_rule 
            (subsidy_id, conflicting_subsidy_id, description)
            VALUES (?, ?, ?)''',
            (subsidy_id, conflicting_subsidy_id, description)
        )
    
    def get_conflict_rules(self, subsidy_id=None):
        """获取冲突规则"""
        query = "SELECT * FROM conflict_rule"
        params = []
        
        if subsidy_id:
            query += " WHERE subsidy_id = ?"
            params.append(subsidy_id)
        
        results = execute_query(self.db_path, query, params, fetch=True)
        rules = []
        for row in results:
            rules.append({
                "rule_id": row[0],
                "subsidy_id": row[1],
                "conflicting_subsidy_id": row[2],
                "description": row[3]
            })
        return rules
    
    def delete_conflict_rule(self, rule_id):
        """删除冲突规则"""
        return execute_query(
            self.db_path,
            "DELETE FROM conflict_rule WHERE rule_id = ?",
            (rule_id,)
        )
    
    def check_conflict(self, person_id, subsidy_id, year):
        """检查补贴冲突"""
        # 获取该补贴的所有冲突规则
        conflict_rules = self.get_conflict_rules(subsidy_id)
        if not conflict_rules:
            return True  # 没有冲突规则
        
        # 获取冲突补贴ID列表
        conflicting_ids = [rule["conflicting_subsidy_id"] for rule in conflict_rules]
        
        # 检查人员是否已领取冲突补贴
        existing_conflicts = execute_query(
            self.db_path,
            f'''SELECT 1 FROM subsidy_record 
            WHERE person_id = ? AND year = ?
            AND subsidy_id IN ({','.join(['?']*len(conflicting_ids))})''',
            [person_id, year] + conflicting_ids,
            fetch=True
        )
        
        return not bool(existing_conflicts)
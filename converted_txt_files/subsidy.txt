

# models/subsidy.py
from database import execute_query

class SubsidyTypeDAO:
    def __init__(self, db_path='family_subsidies.db'):
        self.db_path = db_path
    
    def add_subsidy_type(self, subsidy_id, name, amount_per_unit, description=None,
                        land_requirement=None, is_mutual_exclusive=False, allow_multiple=False):
        """添加补贴类型"""
        return execute_query(
            self.db_path,
            '''INSERT INTO subsidy_type 
            (subsidy_id, name, description, land_requirement, 
             is_mutual_exclusive, allow_multiple, amount_per_unit)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (subsidy_id, name, description, land_requirement,
             int(is_mutual_exclusive), int(allow_multiple), amount_per_unit)
        )
    
    def get_subsidy_type(self, subsidy_id):
        """获取单个补贴类型信息"""
        result = execute_query(
            self.db_path,
            "SELECT * FROM subsidy_type WHERE subsidy_id = ?",
            (subsidy_id,),
            fetch=True
        )
        if result:
            return {
                "subsidy_id": result[0][0],
                "name": result[0][1],
                "description": result[0][2],
                "land_requirement": result[0][3],
                "is_mutual_exclusive": bool(result[0][4]),
                "allow_multiple": bool(result[0][5]),
                "amount_per_unit": result[0][6]
            }
        return None
    
    def get_subsidy_types(self):
        """获取所有补贴类型"""
        results = execute_query(
            self.db_path,
            "SELECT * FROM subsidy_type",
            fetch=True
        )
        types = []
        for row in results:
            types.append({
                "subsidy_id": row[0],
                "name": row[1],
                "description": row[2],
                "land_requirement": row[3],
                "is_mutual_exclusive": bool(row[4]),
                "allow_multiple": bool(row[5]),
                "amount_per_unit": row[6]
            })
        return types
    
    def update_subsidy_type(self, subsidy_id, **kwargs):
        """更新补贴类型信息"""
        # 获取当前补贴类型信息
        subsidy = self.get_subsidy_type(subsidy_id)
        if not subsidy:
            raise ValueError(f"补贴类型 {subsidy_id} 不存在")
        
        # 构建更新字段和参数
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field == "name":
                updates.append("name = ?")
                params.append(value)
            elif field == "description":
                updates.append("description = ?")
                params.append(value)
            elif field == "land_requirement":
                updates.append("land_requirement = ?")
                params.append(value)
            elif field == "is_mutual_exclusive":
                updates.append("is_mutual_exclusive = ?")
                params.append(int(value))
            elif field == "allow_multiple":
                updates.append("allow_multiple = ?")
                params.append(int(value))
            elif field == "amount_per_unit":
                updates.append("amount_per_unit = ?")
                params.append(value)
        
        # 如果没有更新字段，直接返回
        if not updates:
            return False
        
        # 添加WHERE条件
        params.append(subsidy_id)
        query = f"UPDATE subsidy_type SET {', '.join(updates)} WHERE subsidy_id = ?"
        
        return execute_query(self.db_path, query, params)
    
    def delete_subsidy_type(self, subsidy_id):
        """删除补贴类型"""
        # 检查补贴类型是否被补贴记录引用
        subsidy_ref = execute_query(
            self.db_path,
            "SELECT 1 FROM subsidy_record WHERE subsidy_id = ?",
            (subsidy_id,),
            fetch=True
        )
        if subsidy_ref:
            raise ValueError("该补贴类型已被补贴记录引用，无法删除")
        
        return execute_query(
            self.db_path,
            "DELETE FROM subsidy_type WHERE subsidy_id = ?",
            (subsidy_id,)
        )

class SubsidyRecordDAO:
    def __init__(self, db_path='family_subsidies.db'):
        self.db_path = db_path
    
    def add_subsidy_record(self, person_id, subsidy_id, applied_area, land_id, year, 
                          payment_method=None):
        """添加补贴记录"""
        # 检查人员是否存在
        person_exists = execute_query(
            self.db_path,
            "SELECT 1 FROM person WHERE person_id = ?",
            (person_id,),
            fetch=True
        )
        if not person_exists:
            raise ValueError(f"人员 {person_id} 不存在")
        
        # 检查补贴类型是否存在
        subsidy_type = execute_query(
            self.db_path,
            "SELECT * FROM subsidy_type WHERE subsidy_id = ?",
            (subsidy_id,),
            fetch=True
        )
        if not subsidy_type:
            raise ValueError(f"补贴类型 {subsidy_id} 不存在")
        
        # 检查用地是否存在
        land_exists = execute_query(
            self.db_path,
            "SELECT 1 FROM land WHERE land_id = ?",
            (land_id,),
            fetch=True
        )
        if not land_exists:
            raise ValueError(f"用地 {land_id} 不存在")
        
        # 检查互斥规则
        if subsidy_type[0][4]:  # is_mutual_exclusive
            conflicting = execute_query(
                self.db_path,
                '''SELECT c.conflicting_subsidy_id 
                FROM conflict_rule c
                WHERE c.subsidy_id = ?''',
                (subsidy_id,),
                fetch=True
            )
            
            if conflicting:
                conflict_ids = [c[0] for c in conflicting]
                conflict_check = execute_query(
                    self.db_path,
                    f'''SELECT 1 FROM subsidy_record 
                    WHERE person_id = ? AND year = ?
                    AND subsidy_id IN ({','.join(['?']*len(conflict_ids))})''',
                    [person_id, year] + conflict_ids,
                    fetch=True
                )
                
                if conflict_check:
                    raise ValueError(f"补贴冲突: {subsidy_type[0][1]} 与其他补贴互斥")
        
        # 检查多次领取
        if not subsidy_type[0][5]:  # allow_multiple
            existing = execute_query(
                self.db_path,
                '''SELECT 1 FROM subsidy_record 
                WHERE person_id = ? AND subsidy_id = ? AND year = ?''',
                (person_id, subsidy_id, year),
                fetch=True
            )
            if existing:
                raise ValueError("该补贴类型不可多次领取")
        
        # 计算总金额
        total_amount = applied_area * subsidy_type[0][6]  # amount_per_unit
        
        # 添加记录
        return execute_query(
            self.db_path,
            '''INSERT INTO subsidy_record 
            (person_id, subsidy_id, year, grant_date, applied_area, total_amount, payment_method, land_id)
            VALUES (?, ?, ?, DATE('now'), ?, ?, ?, ?)''',
            (person_id, subsidy_id, year, applied_area, total_amount, payment_method, land_id)
        )
    
    def get_subsidy_record(self, record_id):
        """获取单个补贴记录"""
        result = execute_query(
            self.db_path,
            """SELECT r.*, p.name AS person_name, s.name AS subsidy_name, l.land_type
            FROM subsidy_record r
            JOIN person p ON r.person_id = p.person_id
            JOIN subsidy_type s ON r.subsidy_id = s.subsidy_id
            JOIN land l ON r.land_id = l.land_id
            WHERE r.record_id = ?""",
            (record_id,),
            fetch=True
        )
        if result:
            return {
                "record_id": result[0][0],
                "person_id": result[0][1],
                "subsidy_id": result[0][2],
                "year": result[0][3],
                "grant_date": result[0][4],
                "applied_area": result[0][5],
                "total_amount": result[0][6],
                "payment_method": result[0][7],
                "land_id": result[0][8],
                "person_name": result[0][9],
                "subsidy_name": result[0][10],
                "land_type": result[0][11]
            }
        return None
    
    def get_subsidy_records(self, person_id=None, family_id=None, year=None):
        """获取补贴记录"""
        query = """
        SELECT r.*, p.name AS person_name, s.name AS subsidy_name, l.land_type
        FROM subsidy_record r
        JOIN person p ON r.person_id = p.person_id
        JOIN subsidy_type s ON r.subsidy_id = s.subsidy_id
        JOIN land l ON r.land_id = l.land_id
        """
        params = []
        conditions = []
        
        if person_id:
            conditions.append("r.person_id = ?")
            params.append(person_id)
        
        if family_id:
            conditions.append("p.family_id = ?")
            params.append(family_id)
        
        if year:
            conditions.append("r.year = ?")
            params.append(year)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        results = execute_query(self.db_path, query, params, fetch=True)
        records = []
        for row in results:
            records.append({
                "record_id": row[0],
                "person_id": row[1],
                "subsidy_id": row[2],
                "year": row[3],
                "grant_date": row[4],
                "applied_area": row[5],
                "total_amount": row[6],
                "payment_method": row[7],
                "land_id": row[8],
                "person_name": row[9],
                "subsidy_name": row[10],
                "land_type": row[11]
            })
        return records
    
    def update_subsidy_record(self, record_id, **kwargs):
        """更新补贴记录"""
        # 获取当前记录信息
        record = self.get_subsidy_record(record_id)
        if not record:
            raise ValueError(f"补贴记录 {record_id} 不存在")
        
        # 构建更新字段和参数
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field == "applied_area":
                # 重新计算总金额
                subsidy_type = execute_query(
                    self.db_path,
                    "SELECT amount_per_unit FROM subsidy_type WHERE subsidy_id = ?",
                    (record["subsidy_id"],),
                    fetch=True
                )
                if not subsidy_type:
                    raise ValueError("关联的补贴类型不存在")
                
                amount_per_unit = subsidy_type[0][0]
                total_amount = value * amount_per_unit
                
                updates.append("applied_area = ?")
                params.append(value)
                updates.append("total_amount = ?")
                params.append(total_amount)
            elif field == "payment_method":
                updates.append("payment_method = ?")
                params.append(value)
            elif field == "land_id":
                # 检查新用地是否存在
                land_exists = execute_query(
                    self.db_path,
                    "SELECT 1 FROM land WHERE land_id = ?",
                    (value,),
                    fetch=True
                )
                if not land_exists:
                    raise ValueError(f"用地 {value} 不存在")
                
                updates.append("land_id = ?")
                params.append(value)
        
        # 如果没有更新字段，直接返回
        if not updates:
            return False
        
        # 添加WHERE条件
        params.append(record_id)
        query = f"UPDATE subsidy_record SET {', '.join(updates)} WHERE record_id = ?"
        
        return execute_query(self.db_path, query, params)
    
    def delete_subsidy_record(self, record_id):
        """删除补贴记录"""
        return execute_query(
            self.db_path,
            "DELETE FROM subsidy_record WHERE record_id = ?",
            (record_id,)
        )
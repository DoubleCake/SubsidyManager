# models/person.py
from database import execute_query
from datetime import date

class PersonDAO:
    def __init__(self, db_path='family_subsidies.db'):
        self.db_path = db_path
    
    def add_person(self, person_id, family_id, name, phone=None, 
                  has_social_card=False, is_head=False):
        """添加新人员"""
        # 检查家庭是否存在
        family_exists = execute_query(
            self.db_path,
            "SELECT 1 FROM family WHERE family_id = ?",
            (family_id,),
            fetch=True
        )
        if not family_exists:
            raise ValueError(f"家庭 {family_id} 不存在")
        
        # 如果是户主，检查该家庭是否已有户主
        if is_head:
            existing_head = execute_query(
                self.db_path,
                "SELECT 1 FROM person WHERE family_id = ? AND is_head = 1",
                (family_id,),
                fetch=True
            )
            if existing_head:
                raise ValueError(f"家庭 {family_id} 已有户主")
        
        # 添加人员
        return execute_query(
            self.db_path,
            '''INSERT INTO person 
            (person_id, family_id, name, phone, has_social_card, is_head)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (person_id, family_id, name, phone, 
             int(has_social_card), int(is_head))
        )
    
    def get_person(self, person_id):
        """获取单个人员信息"""
        result = execute_query(
            self.db_path,
            "SELECT * FROM person WHERE person_id = ?",
            (person_id,),
            fetch=True
        )
        if result:
            return {
                "person_id": result[0][0],
                "family_id": result[0][1],
                "name": result[0][2],
                "phone": result[0][3],
                "has_social_card": bool(result[0][4]),
                "is_head": bool(result[0][5])
            }
        return None
    
    def get_persons(self, family_id=None, is_head=None):
        """获取人员列表"""
        query = "SELECT * FROM person"
        params = []
        
        conditions = []
        if family_id:
            conditions.append("family_id = ?")
            params.append(family_id)
        if is_head is not None:
            conditions.append("is_head = ?")
            params.append(int(is_head))
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        results = execute_query(self.db_path, query, params, fetch=True)
        persons = []
        for row in results:
            persons.append({
                "person_id": row[0],
                "family_id": row[1],
                "name": row[2],
                "phone": row[3],
                "has_social_card": bool(row[4]),
                "is_head": bool(row[5])
            })
        return persons
    
    def update_person(self, person_id, name=None, phone=None, 
                     has_social_card=None, is_head=None):
        """更新人员信息"""
        # 获取当前人员信息
        current_person = self.get_person(person_id)
        if not current_person:
            raise ValueError(f"人员 {person_id} 不存在")
        
        # 构建更新字段和参数
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if phone is not None:
            updates.append("phone = ?")
            params.append(phone)
        
        if has_social_card is not None:
            updates.append("has_social_card = ?")
            params.append(int(has_social_card))
        
        # 处理户主状态变更
        if is_head is not None:
            if is_head and not current_person["is_head"]:
                # 设置为户主
                # 检查该家庭是否已有户主
                existing_head = execute_query(
                    self.db_path,
                    "SELECT person_id FROM person WHERE family_id = ? AND is_head = 1",
                    (current_person["family_id"],),
                    fetch=True
                )
                if existing_head and existing_head[0][0] != person_id:
                    raise ValueError(f"家庭 {current_person['family_id']} 已有户主")
                
                updates.append("is_head = ?")
                params.append(1)
            
            elif not is_head and current_person["is_head"]:
                # 取消户主身份
                updates.append("is_head = ?")
                params.append(0)
        
        # 如果没有更新字段，直接返回
        if not updates:
            return False
        
        # 添加WHERE条件
        params.append(person_id)
        query = f"UPDATE person SET {', '.join(updates)} WHERE person_id = ?"
        
        return execute_query(self.db_path, query, params)
    
    def set_as_head(self, person_id):
        """设置人员为户主"""
        # 获取当前人员信息
        person = self.get_person(person_id)
        if not person:
            raise ValueError(f"人员 {person_id} 不存在")
        
        # 如果已经是户主，无需操作
        if person["is_head"]:
            return True
        
        # 检查该家庭是否已有户主
        existing_head = execute_query(
            self.db_path,
            "SELECT person_id FROM person WHERE family_id = ? AND is_head = 1",
            (person["family_id"],),
            fetch=True
        )
        
        if existing_head:
            # 取消原有户主
            execute_query(
                self.db_path,
                "UPDATE person SET is_head = 0 WHERE person_id = ?",
                (existing_head[0][0],)
            )
        
        # 设置新户主
        return execute_query(
            self.db_path,
            "UPDATE person SET is_head = 1 WHERE person_id = ?",
            (person_id,)
        )
    
    def remove_head_status(self, person_id):
        """取消户主身份"""
        # 获取当前人员信息
        person = self.get_person(person_id)
        if not person:
            raise ValueError(f"人员 {person_id} 不存在")
        
        # 如果不是户主，无需操作
        if not person["is_head"]:
            return True
        
        return execute_query(
            self.db_path,
            "UPDATE person SET is_head = 0 WHERE person_id = ?",
            (person_id,)
        )
    
    def delete_person(self, person_id):
        """删除人员"""
        # 获取当前人员信息
        person = self.get_person(person_id)
        if not person:
            return False
        
        # 如果是户主，先取消户主身份
        if person["is_head"]:
            self.remove_head_status(person_id)
        
        # 删除人员
        return execute_query(
            self.db_path,
            "DELETE FROM person WHERE person_id = ?",
            (person_id,)
        )
    
    def search_persons(self, name=None, family_id=None, phone=None):
        """搜索人员"""
        query = "SELECT * FROM person WHERE 1=1"
        params = []
        
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        
        if family_id:
            query += " AND family_id = ?"
            params.append(family_id)
        
        if phone:
            query += " AND phone LIKE ?"
            params.append(f"%{phone}%")
        
        results = execute_query(self.db_path, query, params, fetch=True)
        persons = []
        for row in results:
            persons.append({
                "person_id": row[0],
                "family_id": row[1],
                "name": row[2],
                "phone": row[3],
                "has_social_card": bool(row[4]),
                "is_head": bool(row[5])
            })
        return persons
    
    def get_family_head(self, family_id):
        """获取家庭的户主"""
        result = execute_query(
            self.db_path,
            "SELECT * FROM person WHERE family_id = ? AND is_head = 1",
            (family_id,),
            fetch=True
        )
        if result:
            return {
                "person_id": result[0][0],
                "family_id": result[0][1],
                "name": result[0][2],
                "phone": result[0][3],
                "has_social_card": bool(result[0][4]),
                "is_head": True
            }
        return None
    
    def transfer_head_to(self, family_id, new_head_id):
        """转移户主身份"""
        # 检查新成员是否存在且属于该家庭
        new_member = execute_query(
            self.db_path,
            "SELECT 1 FROM person WHERE person_id = ? AND family_id = ?",
            (new_head_id, family_id),
            fetch=True
        )
        if not new_member:
            raise ValueError(f"成员 {new_head_id} 不属于家庭 {family_id}")
        
        # 获取当前户主
        current_head = self.get_family_head(family_id)
        
        # 如果当前户主就是新户主，无需操作
        if current_head and current_head["person_id"] == new_head_id:
            return True
        
        # 开始事务
        try:
            # 取消当前户主
            if current_head:
                self.remove_head_status(current_head["person_id"])
            
            # 设置新户主
            self.set_as_head(new_head_id)
            return True
        except Exception as e:
            # 在实际应用中，这里应该有事务回滚
            raise e
    
    def get_persons_with_subsidies(self, family_id=None, year=None):
        """获取人员及其补贴信息"""
        query = """
        SELECT p.person_id, p.name, p.phone, p.has_social_card, p.is_head,
               s.subsidy_id, st.name AS subsidy_name, s.year, s.applied_area, 
               s.total_amount, s.payment_method
        FROM person p
        LEFT JOIN subsidy_record s ON p.person_id = s.person_id
        LEFT JOIN subsidy_type st ON s.subsidy_id = st.subsidy_id
        """
        
        conditions = []
        params = []
        
        if family_id:
            conditions.append("p.family_id = ?")
            params.append(family_id)
        
        if year is not None:
            conditions.append("s.year = ?")
            params.append(year)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        results = execute_query(self.db_path, query, params, fetch=True)
        
        # 组织数据结构
        persons_map = {}
        for row in results:
            person_id = row[0]
            if person_id not in persons_map:
                persons_map[person_id] = {
                    "person_id": person_id,
                    "name": row[1],
                    "phone": row[2],
                    "has_social_card": bool(row[3]),
                    "is_head": bool(row[4]),
                    "subsidies": []
                }
            
            # 如果有补贴信息
            if row[5]:
                persons_map[person_id]["subsidies"].append({
                    "subsidy_id": row[5],
                    "subsidy_name": row[6],
                    "year": row[7],
                    "applied_area": row[8],
                    "total_amount": row[9],
                    "payment_method": row[10]
                })
        
        return list(persons_map.values())
class FamilyDAO:
    def __init__(self, db_manager):
        self.db = db_manager.get_connection()
    
    def create_family(self, landarea, villageid, groupid, address=None):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO family (landarea, villageid, groupid, address) VALUES (?, ?, ?, ?)",
            (landarea, villageid, groupid, address)
        )
        self.db.commit()
        return cursor.lastrowid
    
    def get_family_by_id(self, family_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM family WHERE id = ?", (family_id,))
        return cursor.fetchone()
    
    def get_all_families(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM family")
        return cursor.fetchall()
    
    def update_family(self, family_id, landarea=None, villageid=None, groupid=None, address=None, name=None):
        updates = []
        params = []
        
        if landarea is not None:
            updates.append("landarea = ?")
            params.append(landarea)
        if villageid is not None:
            updates.append("villageid = ?")
            params.append(villageid)
        if groupid is not None:
            updates.append("groupid = ?")
            params.append(groupid)
        if address is not None:
            updates.append("address = ?")
            params.append(address)
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if not updates:
            return False
        
        params.append(family_id)
        query = f"UPDATE family SET {', '.join(updates)} WHERE id = ?"
        
        cursor = self.db.cursor()
        cursor.execute(query, tuple(params))
        self.db.commit()
        return cursor.rowcount > 0
    
    def delete_family(self, family_id):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM family WHERE id = ?", (family_id,))
        self.db.commit()
        return cursor.rowcount > 0
    
    def search_families(self, village_id=None, group_id=None, name=None):
        conditions = []
        params = []
        
        if village_id is not None:
            conditions.append("villageid = ?")
            params.append(village_id)
        if group_id is not None:
            conditions.append("groupid = ?")
            params.append(group_id)
        if name is not None:
            conditions.append("name LIKE ?")
            params.append(f"%{name}%")
        
        query = "SELECT * FROM family"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        cursor = self.db.cursor()
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    
    def update_family_name(self, family_id, head_name):
        """更新家庭名称为户主名称+家"""
        new_name = f"{head_name}家"
        return self.update_family(family_id, name=new_name)
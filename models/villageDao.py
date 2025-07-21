class VillageDAO:
    def __init__(self, db_manager):
        self.db = db_manager.get_connection()
    
    def create_village(self, name, town):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO village (name, town) VALUES (?, ?)",
            (name, town)
        )
        self.db.commit()
        return cursor.lastrowid
    
    def get_village_by_id(self, village_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM village WHERE id = ?", (village_id,))
        return cursor.fetchone()
    
    def get_all_villages(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM village")
        return cursor.fetchall()
    
    def update_village(self, village_id, name, town):
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE village SET name = ?, town = ? WHERE id = ?",
            (name, town, village_id)
        )
        self.db.commit()
        return cursor.rowcount > 0
    
    def delete_village(self, village_id):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM village WHERE id = ?", (village_id,))
        self.db.commit()
        return cursor.rowcount > 0
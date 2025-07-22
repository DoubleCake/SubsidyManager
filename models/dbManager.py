import sqlite3

class DatabaseManager:
    _instance = None

    def __new__(cls, db_path='family_subsidies.db'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = sqlite3.connect(db_path)
            cls._instance.connection.row_factory = sqlite3.Row
            cls._instance._create_tables()
        return cls._instance
    
    def _create_tables(self):
        cursor = self.connection.cursor()

        # 创建村庄表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS village (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                town TEXT NOT NULL
            )
        ''')
        
        # 创建家庭表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS family (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                landarea REAL NOT NULL,
                villageid INTEGER NOT NULL,
                groupid INTEGER NOT NULL,
                address TEXT,
                name TEXT DEFAULT '家庭户名',
                FOREIGN KEY (villageid) REFERENCES village(id)
            )
        ''')
        
        # 创建人员表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS person (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                familyid INTEGER NOT NULL,
                name TEXT NOT NULL,
                gender TEXT,
                age INTEGER,
                idcard TEXT UNIQUE,
                relation TEXT NOT NULL,
                is_head BOOLEAN DEFAULT 0,
                FOREIGN KEY (familyid) REFERENCES family(id)
            )
        ''')
        
        self.connection.commit()
    
    def get_connection(self):
        return self.connection
    
    def close(self):
        if self.connection:
            self.connection.close()
            self._instance = None


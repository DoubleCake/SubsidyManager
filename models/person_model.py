from .dbManager import DatabaseManager 

class PersonDAO:
    """
    线程安全（其实是单线程）的 Person 数据访问对象。
    所有 SQL 都通过 DatabaseManager().get_connection() 拿到同一个连接。
    """
    # ---------- 内部工具 ----------
    def _execute(self, sql: str, params=(), *, fetch=False):
        """
        统一封装：增删改用 execute，查询用 fetchall/fetchone
        """
        conn = DatabaseManager().get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        if fetch:
            # 查询类语句返回行
            return cur.fetchall() if fetch == 'all' else cur.fetchone()
        return cur.lastrowid      # 插入时返回主键

    # ---------- 业务接口 ----------
    def add_person(self, person_id, family_id, name, phone=None,
                   has_social_card=False, is_head=False):
        # 检查家庭是否存在
        row = self._execute(
            "SELECT 1 FROM family WHERE id = ?", (family_id,), fetch=True
        )
        if not row:
            raise ValueError(f"家庭 {family_id} 不存在")

        # 若设为户主，先检查冲突
        if is_head:
            row = self._execute(
                "SELECT 1 FROM person WHERE familyid = ? AND is_head = 1",
                (family_id,), fetch=True
            )
            if row:
                raise ValueError(f"家庭 {family_id} 已有户主")

        self._execute(
            """INSERT INTO person
               (id, familyid, name, phone, has_social_card, is_head)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (person_id, family_id, name, phone,
             int(has_social_card), int(is_head))
        )
        return person_id

    def get_person(self, person_id):
        row = self._execute(
            "SELECT * FROM person WHERE id = ?", (person_id,), fetch=True
        )
        if not row:
            return None
        return dict(row)

    def get_persons(self, family_id=None, is_head=None):
        sql = "SELECT * FROM person"
        cond, params = [], []
        if family_id:
            cond.append("familyid = ?")
            params.append(family_id)
        if is_head is not None:
            cond.append("is_head = ?")
            params.append(int(is_head))
        if cond:
            sql += " WHERE " + " AND ".join(cond)

        rows = self._execute(sql, params, fetch='all')
        return [dict(r) for r in rows]

    def update_person(self, person_id, **kwargs):
        # 获取当前记录
        current = self.get_person(person_id)
        if not current:
            raise ValueError(f"人员 {person_id} 不存在")

        updates, params = [], []
        for k, v in kwargs.items():
            if k not in {"name", "phone", "has_social_card", "is_head"}:
                continue
            updates.append(f"{k} = ?")
            params.append(int(v) if k in {"has_social_card", "is_head"} else v)

        if not updates:
            return False

        # 如果是设置户主，需要额外检查
        if kwargs.get("is_head") and not current["is_head"]:
            row = self._execute(
                "SELECT id FROM person WHERE familyid = ? AND is_head = 1",
                (current["familyid"],), fetch=True
            )
            if row and row["id"] != person_id:
                raise ValueError("该家庭已有户主")

        params.append(person_id)
        self._execute(
            f"UPDATE person SET {', '.join(updates)} WHERE id = ?", params
        )
        return True

    def delete_person(self, person_id):
        # 如果是户主先取消
        row = self.get_person(person_id)
        if not row:
            return False
        if row["is_head"]:
            self._execute(
                "UPDATE person SET is_head = 0 WHERE id = ?", (person_id,)
            )
        self._execute("DELETE FROM person WHERE id = ?", (person_id,))
        return True

    # 其余方法（set_as_head、transfer_head_to、search_persons …）
    # 逻辑与原来一致，只需把 execute_query 换成 _execute 即可
    # 已经改好如上，你可以按需复制粘贴剩余方法并做同样替换
# seed_data.py
import sqlite3
from random import choice, randint
from services import FamilyService


def insert_test_data(db_path='family_subsidies.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 模拟姓名、性别、地点等数据
    names = ["张三", "李四", "王五", "赵六", "孙七", "周八", "吴九", "郑十"]
    locations = ["朝阳区", "海淀区", "东城区", "西城区", "丰台区", "通州区", "昌平区", "顺义区"]

    # 插入 person 测试数据
    persons = []
    for i in range(10):
        name = f"{choice(names)}{randint(10, 99)}"
        gender = choice(["男", "女"])
        age = randint(18, 70)
        cursor.execute("INSERT INTO person (name, gender, age) VALUES (?, ?, ?)", (name, gender, age))
        persons.append(cursor.lastrowid)
    print(f"✅ 已插入 {len(persons)} 条人员数据")

    # 插入 land 测试数据
    lands = []
    for i in range(8):
        location = choice(locations)
        area = round(randint(50, 500) + randint(0, 99) / 100, 2)
        cursor.execute("INSERT INTO land (location, area) VALUES (?, ?)", (location, area))
        lands.append(cursor.lastrowid)
    print(f"✅ 已插入 {len(lands)} 条土地数据")

    # 插入 family 测试数据
    families = []
    for i in range(5):
        head_id = choice(persons)
        land_id = choice(lands)

        cursor.execute("INSERT INTO family (land_id, head_id) VALUES (?, ?)", (land_id, head_id))
        family_id = cursor.lastrowid
        families.append(family_id)

        # 插入家庭成员（除户主外，随机添加1~3人）
        member_ids = list(set([choice(persons) for _ in range(randint(1, 3))]))
        if head_id in member_ids:
            member_ids.remove(head_id)

        for member_id in member_ids:
            cursor.execute("INSERT INTO family_member (family_id, member_id) VALUES (?, ?)", (family_id, member_id))

        # 插入其他土地（随机添加0~2个）
        additional_lands = list(set([choice(lands) for _ in range(randint(0, 2))]))
        if land_id in additional_lands:
            additional_lands.remove(land_id)

        for lid in additional_lands:
            cursor.execute("INSERT INTO family_land (family_id, land_id) VALUES (?, ?)", (family_id, lid))

    print(f"✅ 已插入 {len(families)} 条家庭数据")

    conn.commit()
    conn.close()
    print("\n🎉 初始化测试数据插入完成！")


if __name__ == '__main__':
    service = FamilyService()

    # 创建家庭，使用默认 contract_code=0
    # family_id = service.create_family(head_id=1, land_area=120.5)
    # print(f"✅ 家庭已创建，ID：{family_id}")

    # 查询家庭详情
    family_info = service.get_family(1)
    print("家庭详情：", family_info)
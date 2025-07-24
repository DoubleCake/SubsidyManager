import pandas as pd
from datetime import datetime
import os

def create_sample_excel_template(excel_path):
    """创建Excel模板示例"""
    
    # 基础数据结构
    sample_data = {
        '村庄名称': ['张村', '李村', '王村', '赵村'],
        '归档状态': ['已归档', '未归档', '部分归档', '未归档'],
        '文件数量': [15, 0, 8, 0],
        '归档时间': [
            '2024-01-15 14:30:25',
            '',
            '2024-01-16 09:15:30',
            ''
        ],
        '必需材料': [
            '合同,照片,证明,申请表',
            '合同,照片,证明,申请表',
            '合同,照片',
            '合同,照片,证明,申请表'
        ],
        '已收材料': [
            '合同,照片,证明,申请表',
            '',
            '合同,照片',
            ''
        ],
        '缺少材料': [
            '',
            '合同,照片,证明,申请表',
            '证明,申请表',
            '合同,照片,证明,申请表'
        ],
        '负责人': ['张三', '李四', '王五', '赵六'],
        '备注': [
            '已完成',
            '紧急催收',
            '缺少关键证明',
            '新发现村庄'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_excel(excel_path, index=False)
    
    print(f"Excel模板已创建: {excel_path}")
    return df

# 如果你想查看数据结构，可以运行这个函数
if __name__ == "__main__":
    # 创建示例模板
    create_sample_excel_template("归档管理模板.xlsx")
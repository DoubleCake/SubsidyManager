import pandas as pd
from datetime import datetime
import pandas as pd
import os
import re
from datetime import datetime

def excel_to_md_with_images(input_excel, output_md, image_folder='./asset'):
    """
    将Excel数据转换为Markdown格式，包含时间加粗、正文内容和匹配的图片
    支持根据第三列ID精确匹配多张图片
    
    参数:
    input_excel: 输入Excel文件路径
    output_md: 输出Markdown文件路径
    image_folder: 图片文件夹路径 (默认'./asset')
    """
    # 读取Excel文件
    df = pd.read_excel(input_excel)
    # 确保列名正确（根据实际情况调整）
    time_col = df.columns[8]  # 第一列：时间
    content_col = df.columns[2]  # 第二列：正文
    id_col = df.columns[0] if len(df.columns) > 2 else None  # 第三列：图片ID
    
    # 转换时间列为datetime格式并排序
    df['sort_time'] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.dropna(subset=['sort_time']).sort_values('sort_time')
    
    # 获取图片文件夹中的所有文件
    image_files = [f for f in os.listdir(image_folder) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        # 创建ID到图片列表的映射字典
    id_to_images = {}
    
    # 预处理：将所有图片按ID分组
    for img in image_files:
        # 提取ID部分（两种格式：YYYYMMDDT_ID.jpg 或 YYYYMMDDT_ID_序号.jpg）
        id_match = re.search(r'^\d{8}T_(\d+)(?:_\d+)?\.', img)
        if id_match:
            img_id = id_match.group(1)
            if img_id not in id_to_images:
                id_to_images[img_id] = []
            id_to_images[img_id].append(img)


    # 生成Markdown内容
    md_content = "# 时间记录与图片\n\n"
    
    for _, row in df.iterrows():
        # 提取时间值（原始格式）
        time_value = row[time_col]
        
        # 加粗处理时间列
        md_content += f"**{time_value}**  \n"
        
        # 添加正文内容
        md_content += f"{row[content_col]}\n\n"
        
        # 获取当前行的ID
        row_id = str(row[id_col])
        
        # 获取匹配的图片
        matching_images = id_to_images.get(row_id, [])
        
        # 按序号排序图片
        def get_img_number(img_name):
            # 尝试提取序号部分
            seq_match = re.search(r'_(\d+)\.', img_name)
            return int(seq_match.group(1)) if seq_match else 0
        
        matching_images.sort(key=get_img_number)
        
        # 添加匹配的图片
        if matching_images:
            md_content += "### 相关图片\n"
            for img in matching_images:
                img_path = os.path.join(image_folder, img).replace('\\', '/')
                seq_num = get_img_number(img)
                alt_text = f"图片 {seq_num}" if seq_num > 0 else "主图"
                md_content += f"![{alt_text}]({img_path})\n\n"
        else:
            md_content += "> 无匹配图片\n\n"
        
        # 添加分割线
        md_content += "---\n\n"
    
    # 保存到Markdown文件
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    total_images = sum(len(imgs) for imgs in id_to_images.values())
    matched_images = sum(len(imgs) for id_val, imgs in id_to_images.items() 
                        if id_val in df[id_col].astype(str).values)
    
    print(f"Markdown文件已生成: {output_md}")
    print(f"共处理 {len(df)} 条记录，匹配 {matched_images}/{total_images} 张图片")

# 使用示例
if __name__ == "__main__":
    excel_to_md_with_images(
        input_excel='./1002568141.xlsx',  # 输入Excel文件名
        output_md='俊哥2.md',      # 输出Markdown文件名
        image_folder='./assets/俊哥'     # 图片文件夹路径
    )
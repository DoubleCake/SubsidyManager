# services/subsidy_service.py
from datetime import datetime
from typing import List, Dict, Optional, Union
from models.subsidy_model import SubsidyDAO
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, Border, Side

class SubsidyService:
    """
    补贴管理服务层
    处理补贴相关的业务逻辑，协调多个DAO操作
    """
    
    def __init__(self, db_path: str = 'family_subsidies.db'):
        self.dao = SubsidyDAO(db_path)
    
    def create_subsidy_type(self, form_data: Dict) -> Dict:
        """
        创建新的补贴类型（业务逻辑）
        
        :param form_data: 表单数据字典，包含以下字段:
            - name: 补贴名称
            - amount: 补贴金额
            - year: 补贴年份
            - description: 补贴描述
            - land_type: 适用土地类型
            - is_mutual_exclusive: 是否互斥
            - conflict_ids: 冲突补贴ID列表（可选）
        
        :return: 创建的补贴信息字典
        """
        # 1. 数据验证
        if not self._validate_subsidy_form(form_data):
            raise ValueError("补贴数据验证失败")
        
        # 2. 准备数据库数据
        subsidy_data = {
            "name": form_data["name"],
            "amount": form_data["amount"],
            "year": form_data["year"],
            "description": form_data.get("description", ""),
            "land_type": form_data.get("land_type", ""),
            "is_mutual_exclusive": int(form_data.get("is_mutual_exclusive", False)),
            "is_activate": 1  # 默认激活
        }
        
        # 3. 创建补贴类型
        subsidy_id = self.dao.create_subsidy_type(subsidy_data)
        if not subsidy_id:
            raise RuntimeError("创建补贴类型失败")
        
        # 4. 处理互斥规则
        conflict_ids = form_data.get("conflict_ids", [])
        if subsidy_data["is_mutual_exclusive"] and conflict_ids:
            for conflict_id in conflict_ids:
                description = f"{form_data['name']}与{self._get_subsidy_name(conflict_id)}互斥"
                self.dao.create_conflict_rule(subsidy_id, conflict_id, description)
        
        # 5. 返回创建结果
        return self.get_subsidy_type(subsidy_id)
    
    def update_subsidy_type(self, subsidy_id: int, form_data: Dict) -> Dict:
        """
        更新补贴类型信息
        
        :param subsidy_id: 要更新的补贴ID
        :param form_data: 更新数据字典
        :return: 更新后的补贴信息字典
        """
        # 1. 验证补贴存在
        if not self.dao.get_subsidy_by_id(subsidy_id):
            raise ValueError(f"补贴ID {subsidy_id} 不存在")
        
        # 2. 准备更新数据
        update_data = {
            "name": form_data.get("name"),
            "amount": form_data.get("amount"),
            "year": form_data.get("year"),
            "description": form_data.get("description", ""),
            "land_type": form_data.get("land_type", ""),
            "is_mutual_exclusive": int(form_data.get("is_mutual_exclusive", False)),
            "is_activate": int(form_data.get("is_activate", True))
        }
        
        # 移除None值
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        # 3. 更新补贴类型
        if not self.dao.update_subsidy(subsidy_id, update_data):
            raise RuntimeError("更新补贴类型失败")
        
        # 4. 更新互斥规则
        conflict_ids = form_data.get("conflict_ids", [])
        
        # 删除旧规则
        self.dao.delete_conflict_rules(subsidy_id)
        
        # 添加新规则
        if update_data.get("is_mutual_exclusive") and conflict_ids:
            for conflict_id in conflict_ids:
                description = f"{form_data['name']}与{self._get_subsidy_name(conflict_id)}互斥"
                self.dao.create_conflict_rule(subsidy_id, conflict_id, description)
        
        # 5. 返回更新结果
        return self.get_subsidy_type(subsidy_id)
    
    def get_subsidy_type(self, subsidy_id: int) -> Dict:
        """
        获取单个补贴类型的完整信息（包括冲突规则）
        
        :param subsidy_id: 补贴ID
        :return: 补贴详细信息字典
        """
        subsidy = self.dao.get_subsidy_by_id(subsidy_id)
        if not subsidy:
            return None
        
        # 获取冲突规则
        conflict_rules = self.dao.get_conflict_rules(subsidy_id)
        conflict_ids = [rule["conflicting_subsidy_id"] for rule in conflict_rules]
        
        # 获取冲突补贴名称
        conflict_subsidies = [
            {"id": rule["conflicting_subsidy_id"], "name": self._get_subsidy_name(rule["conflicting_subsidy_id"])}
            for rule in conflict_rules
        ]
        
        return {
            **subsidy,
            "conflict_ids": conflict_ids,
            "conflict_subsidies": conflict_subsidies
        }
    
    def get_all_subsidies(self, active_only: bool = True) -> List[Dict]:
        """
        获取所有补贴类型（简化信息）
        
        :param active_only: 是否只返回激活的补贴
        :return: 补贴列表
        """
        return self.dao.get_all_subsidies(active_only)
    
    def search_subsidies(
        self, 
        name: str = "", 
        year: Optional[int] = None,
        land_type: str = "",
        active_only: bool = True
    ) -> List[Dict]:
        """
        搜索补贴类型
        
        :param name: 名称关键词
        :param year: 年份
        :param land_type: 土地类型
        :param active_only: 是否只搜索激活的补贴
        :return: 搜索结果列表
        """
        return self.dao.search_subsidies(name, year, land_type, active_only)
    
    def delete_subsidy_type(self, subsidy_id: int) -> bool:
        """
        删除补贴类型
        
        :param subsidy_id: 补贴ID
        :return: 是否成功删除
        """
        # 1. 检查是否有依赖关系
        if self._has_dependencies(subsidy_id):
            raise RuntimeError("无法删除该补贴类型，存在依赖关系")
        
        # 2. 删除关联的冲突规则
        self.dao.delete_conflict_rules(subsidy_id)
        
        # 3. 删除补贴类型
        return self.dao.delete_subsidy(subsidy_id)
    
    def activate_subsidy(self, subsidy_id: int, activate: bool = True) -> Dict:
        """
        激活或停用补贴
        
        :param subsidy_id: 补贴ID
        :param activate: 是否激活
        :return: 更新后的补贴信息
        """
        if not self.dao.activate_subsidy(subsidy_id, activate):
            raise RuntimeError("更新激活状态失败")
        
        return self.get_subsidy_type(subsidy_id)
    
    def get_conflicting_subsidies(self, subsidy_id: int) -> List[Dict]:
        """
        获取与指定补贴冲突的所有补贴
        
        :param subsidy_id: 补贴ID
        :return: 冲突补贴列表
        """
        # 1. 获取该补贴的冲突规则
        conflict_rules = self.dao.get_conflict_rules(subsidy_id)
        conflict_ids = [rule["conflicting_subsidy_id"] for rule in conflict_rules]
        
        # 2. 获取冲突补贴详情
        return [self.get_subsidy_type(cid) for cid in conflict_ids if cid]
    
    def check_conflict(self, subsidy_id: int, other_subsidy_id: int) -> bool:
        """
        检查两个补贴是否存在冲突
        
        :param subsidy_id: 第一个补贴ID
        :param other_subsidy_id: 第二个补贴ID
        :return: 是否存在冲突
        """
        # 检查直接冲突
        conflict_rules = self.dao.get_conflict_rules(subsidy_id)
        direct_conflict = any(
            rule["conflicting_subsidy_id"] == other_subsidy_id 
            for rule in conflict_rules
        )
        
        if direct_conflict:
            return True
        
        # 检查反向冲突
        conflict_rules_other = self.dao.get_conflict_rules(other_subsidy_id)
        reverse_conflict = any(
            rule["conflicting_subsidy_id"] == subsidy_id 
            for rule in conflict_rules_other
        )
        
        return reverse_conflict
    
    def _validate_subsidy_form(self, form_data: Dict) -> bool:
        """
        验证补贴表单数据
        
        :param form_data: 表单数据
        :return: 是否有效
        """
        # 必需字段检查
        required_fields = ["name", "amount", "year"]
        for field in required_fields:
            if field not in form_data or not form_data[field]:
                return False
        
        # 金额检查
        try:
            amount = float(form_data["amount"])
            if amount < 0:
                return False
        except ValueError:
            return False
        
        # 年份检查
        try:
            year = int(form_data["year"])
            if year < 2000 or year > datetime.now().year + 5:
                return False
        except ValueError:
            return False
        
        # 互斥检查
        if form_data.get("is_mutual_exclusive") and not form_data.get("conflict_ids"):
            return False
        
        return True
    
    def _get_subsidy_name(self, subsidy_id: int) -> str:
        """
        获取补贴名称（内部方法）
        
        :param subsidy_id: 补贴ID
        :return: 补贴名称
        """
        subsidy = self.dao.get_subsidy_by_id(subsidy_id)
        return subsidy["name"] if subsidy else "未知补贴"
    
    def _has_dependencies(self, subsidy_id: int) -> bool:
        """
        检查补贴是否存在依赖关系（内部方法）
        
        :param subsidy_id: 补贴ID
        :return: 是否存在依赖
        """
        # TODO: 实现实际的依赖检查逻辑
        # 例如：检查是否有家庭申请了该补贴
        # 检查是否有其他补贴与该补贴存在冲突关系
        return False
    
    def get_available_conflicts(self, subsidy_id: int) -> List[Dict]:
        """
        获取可选的冲突补贴列表（排除自身和已存在的冲突）
        
        :param subsidy_id: 当前补贴ID
        :return: 可选冲突补贴列表
        """
        # 获取所有激活的补贴
        all_subsidies = self.dao.get_all_subsidies(active_only=True)
        
        # 获取当前补贴已有的冲突ID
        current_conflicts = self.dao.get_conflict_rules(subsidy_id)
        conflict_ids = {rule["conflicting_subsidy_id"] for rule in current_conflicts}
        
        # 过滤结果
        return [
            {
                "id": sub["id"],
                "name": sub["name"],
                "year": sub["year"],
                "land_type": sub.get("land_type", "")
            }
            for sub in all_subsidies
            if sub["id"] != subsidy_id and sub["id"] not in conflict_ids
        ]
    
    def export_subsidies_to_csv(self, file_path: str, active_only: bool = True):
        """
        导出补贴数据到CSV文件
        
        :param file_path: 文件路径
        :param active_only: 是否只导出激活的补贴
        """
        subsidies = self.dao.get_all_subsidies(active_only)
        
        if not subsidies:
            raise ValueError("没有可导出的补贴数据")
        
        import csv
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "id", "name", "amount", "year", "land_type", 
                "is_mutual_exclusive", "is_activate", "description"
            ])
            
            writer.writeheader()
            for subsidy in subsidies:
                writer.writerow({
                    "id": subsidy["id"],
                    "name": subsidy["name"],
                    "amount": subsidy["amount"],
                    "year": subsidy["year"],
                    "land_type": subsidy.get("land_type", ""),
                    "is_mutual_exclusive": "是" if subsidy.get("is_mutual_exclusive") else "否",
                    "is_activate": "是" if subsidy.get("is_activate") else "否",
                    "description": subsidy.get("description", "")
                })
    
    def import_subsidies_from_csv(self, file_path: str) -> int:
        """
        从CSV文件导入补贴数据
        
        :param file_path: 文件路径
        :return: 成功导入的记录数
        """
        import csv
        count = 0
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    subsidy_data = {
                        "name": row["name"],
                        "amount": float(row["amount"]),
                        "year": int(row["year"]),
                        "land_type": row.get("land_type", ""),
                        "is_mutual_exclusive": 1 if row.get("is_mutual_exclusive", "否") == "是" else 0,
                        "is_activate": 1 if row.get("is_activate", "是") == "是" else 0,
                        "description": row.get("description", "")
                    }
                    
                    # 创建补贴
                    self.dao.create_subsidy_type(subsidy_data)
                    count += 1
                except (ValueError, KeyError) as e:
                    print(f"导入失败: {e}, 行数据: {row}")
        
        return count
    def export_subsidies_to_excel(self, file_path: str, active_only: bool = True):
        """
        导出补贴数据到Excel文件 (XLSX格式)
        
        :param file_path: 文件路径
        :param active_only: 是否只导出激活的补贴
        """
        subsidies = self.dao.get_all_subsidies(active_only)
        
        if not subsidies:
            raise ValueError("没有可导出的补贴数据")
        
        # 创建工作簿和工作表
        wb = Workbook()
        ws = wb.active
        ws.title = "补贴类型"
        
        # 设置表头
        headers = [
            "ID", "补贴名称", "补贴金额", "补贴年份", "适用土地类型", 
            "是否互斥", "是否激活", "详细描述"
        ]
        
        # 写入表头并设置样式
        header_font = Font(bold=True)
        header_alignment = Alignment(horizontal='center')
        border = Border(bottom=Side(style='medium'))
        
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.alignment = header_alignment
            cell.border = border
        
        # 写入数据
        for row_idx, subsidy in enumerate(subsidies, 2):
            ws.cell(row=row_idx, column=1, value=subsidy["id"])
            ws.cell(row=row_idx, column=2, value=subsidy["name"])
            ws.cell(row=row_idx, column=3, value=subsidy["amount"])
            ws.cell(row=row_idx, column=4, value=subsidy["year"])
            ws.cell(row=row_idx, column=5, value=subsidy.get("land_type", ""))
            ws.cell(row=row_idx, column=6, value="是" if subsidy.get("is_mutual_exclusive") else "否")
            ws.cell(row=row_idx, column=7, value="是" if subsidy.get("is_activate") else "否")
            ws.cell(row=row_idx, column=8, value=subsidy.get("description", ""))
        
        # 自动调整列宽
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter  # 获取列字母
            
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column].width = adjusted_width
        
        # 冻结首行
        ws.freeze_panes = "A2"
        
        # 保存文件
        wb.save(file_path)
    
    def import_subsidies_from_excel(self, file_path: str) -> int:
        """
        从Excel文件导入补贴数据
        
        :param file_path: 文件路径
        :return: 成功导入的记录数
        """
        count = 0
        
        try:
            wb = load_workbook(filename=file_path)
            ws = wb.active
            
            # 获取列映射 (根据表头)
            header_map = {}
            for col_idx, cell in enumerate(ws[1], 1):
                header_map[cell.value] = col_idx
            
            # 必需字段检查
            required_fields = ["补贴名称", "补贴金额", "补贴年份"]
            for field in required_fields:
                if field not in header_map:
                    raise ValueError(f"缺少必需字段: {field}")
            
            # 遍历数据行
            for row in ws.iter_rows(min_row=2, values_only=True):
                # 跳过空行
                if not row[0]:
                    continue
                try:
                    subsidy_data = {
                        "name": row[header_map["补贴名称"] - 1],
                        "amount": float(row[header_map["补贴金额"] - 1]),
                        "year": int(row[header_map["补贴年份"] - 1]),
                        "land_type": row[header_map.get("适用土地类型", 0) - 1] if "适用土地类型" in header_map else "",
                        "is_mutual_exclusive": 1 if row[header_map.get("是否互斥", 0) - 1] == "是" else 0,
                        "is_activate": 1 if row[header_map.get("是否激活", 0) - 1] == "是" else 1,  # 默认为激活
                        "description": row[header_map.get("详细描述", 0) - 1] if "详细描述" in header_map else ""
                    }
                    # 验证数据
                    if not self._validate_import_data(subsidy_data):
                        print(f"跳过无效数据行: {row}")
                        continue
                    
                    # 创建补贴
                    self.dao.create_subsidy_type(subsidy_data)
                    count += 1
                
                except (ValueError, TypeError) as e:
                    print(f"导入失败: {e}, 行数据: {row}")
        
        except Exception as e:
            print(f"Excel文件处理失败: {e}")
            raise
        
        return count
    
    def _validate_import_data(self, data: Dict) -> bool:
        """
        验证导入数据有效性
        
        :param data: 导入数据字典
        :return: 是否有效
        """
        # 必需字段检查
        required_fields = ["name", "amount", "year"]
        for field in required_fields:
            if field not in data or data[field] is None:
                return False
        
        # 金额检查
        try:
            amount = float(data["amount"])
            if amount < 0:
                return False
        except (ValueError, TypeError):
            return False
        
        # 年份检查
        try:
            year = int(data["year"])
            current_year = datetime.now().year
            if year < 2000 or year > current_year + 5:
                return False
        except (ValueError, TypeError):
            return False
        
        return True
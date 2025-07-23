import sys
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
import pandas as pd

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                              QListWidget, QListWidgetItem, QTextEdit, 
                              QTableWidget, QTableWidgetItem, QCheckBox,
                              QFrame, QSplitter, QScrollArea, QGroupBox,
                              QLineEdit, QDateEdit, QMessageBox, QMenu,
                              QAbstractItemView)
from PySide6.QtCore import Qt, QMimeData, QTimer, QDate, Signal
from PySide6.QtGui import QFont, QColor, QDragEnterEvent, QDropEvent, QAction
from qfluentwidgets import (FluentWindow, PrimaryPushButton, PushButton,
                           CardWidget, StrongBodyLabel, BodyLabel, InfoBar,
                           InfoBarPosition, LineEdit, ComboBox, CheckBox,
                           ToolButton, Icon, ProgressBar)

    
class VillageCard(CardWidget):
    """村庄卡片"""
    file_dropped = Signal(str, list)  # 村庄名, 文件路径列表
    clicked = Signal(str)  # 村庄名
    
    def __init__(self, village_name, archived=False, parent=None):
        super().__init__(parent)
        self.village_name = village_name
        self.archived = archived
        self.setAcceptDrops(True)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # 村庄名称
        self.name_label = StrongBodyLabel(self.village_name)
        self.name_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        
        # 状态标签
        self.status_label = BodyLabel()
        
        # 拖拽区域
        self.drop_area = QFrame()
        self.drop_area.setFixedHeight(60)
        self.drop_area.setStyleSheet("""
            QFrame {
                border: 2px dashed #cccccc;
                border-radius: 4px;
                background-color: #fafafa;
            }
            QFrame:hover {
                border-color: #0078d4;
                background-color: #f0f8ff;
            }
        """)
        self.drop_area_label = BodyLabel("拖拽文件到此处归档")
        self.drop_area_label.setAlignment(Qt.AlignCenter)
        self.drop_area_label.setStyleSheet("color: #666666;")
        
        drop_layout = QVBoxLayout(self.drop_area)
        drop_layout.addWidget(self.drop_area_label)
        drop_layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(self.name_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.drop_area)
        
        # 初始化状态
        self.update_status()
        
    def update_status(self):
        if self.archived:
            self.status_label.setText("✓ 已归档")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            self.drop_area.setVisible(False)
        else:
            self.status_label.setText("⚠ 未归档")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            self.drop_area.setVisible(True)
            
    def set_archived(self, archived):
        self.archived = archived
        self.update_status()
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit(self.village_name)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and not self.archived:
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        if self.archived:
            return
            
        files = []
        for url in event.mimeData().urls():
            files.append(url.toLocalFile())
            
        if files:
            self.file_dropped.emit(self.village_name, files)
            event.acceptProposedAction()

class ProjectManager:
    """项目管理器"""
    def __init__(self):
        self.projects_file = "projects.json"
        self.projects = self.load_projects()
        self.current_project = None
        
    def load_projects(self):
        if os.path.exists(self.projects_file):
            try:
                with open(self.projects_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
        
    def save_projects(self):
        with open(self.projects_file, 'w', encoding='utf-8') as f:
            json.dump(self.projects, f, ensure_ascii=False, indent=2)
            
    def create_project(self, name, work_folder, excel_file):
        project_id = f"proj_{len(self.projects) + 1}"
        project = {
            'id': project_id,
            'name': name,
            'work_folder': work_folder,
            'excel_file': excel_file,
            'created_time': datetime.now().isoformat(),
            'status': '进行中',
            'villages': {},
            'tasks': {}
        }
        self.projects[project_id] = project
        self.save_projects()
        return project_id
        
    def get_project(self, project_id):
        return self.projects.get(project_id)
        
    def get_all_projects(self):
        return list(self.projects.values())
        
    def set_current_project(self, project_id):
        self.current_project = project_id
        return self.projects.get(project_id)
        
    def update_project_village(self, project_id, village_name, data):
        if project_id in self.projects:
            self.projects[project_id]['villages'][village_name] = data
            self.save_projects()
            
    def mark_village_archived(self, project_id, village_name):
        if project_id in self.projects and village_name in self.projects[project_id]['villages']:
            self.projects[project_id]['villages'][village_name]['archived'] = True
            self.projects[project_id]['villages'][village_name]['archive_time'] = datetime.now().isoformat()
            self.save_projects()
            
    def add_task(self, project_id, village_name, due_date, notes=""):
        if project_id in self.projects:
            task_id = f"task_{len(self.projects[project_id].get('tasks', {})) + 1}"
            if 'tasks' not in self.projects[project_id]:
                self.projects[project_id]['tasks'] = {}
            self.projects[project_id]['tasks'][task_id] = {
                'id': task_id,
                'village_name': village_name,
                'due_date': due_date,
                'notes': notes,
                'completed': False,
                'created_time': datetime.now().isoformat()
            }
            self.save_projects()
            return task_id
    def validate_project_paths(self, work_folder, excel_file):
        """验证项目路径"""
        errors = []
        
        # 检查工作文件夹
        if work_folder and not os.path.exists(work_folder):
            errors.append("工作文件夹不存在")
            
        # 检查Excel文件（如果指定了路径）
        if excel_file and os.path.exists(excel_file):
            try:
                pd.read_excel(excel_file)
            except Exception as e:
                errors.append(f"Excel文件格式错误: {str(e)}")
                
        return len(errors) == 0, errors

class ArchiveManager:
    """归档管理器"""
    def __init__(self, work_folder, excel_file):
        self.work_folder = work_folder
        self.excel_file = excel_file
        self.ensure_folders()
        
    def ensure_folders(self):
        """确保工作文件夹存在"""
        Path(self.work_folder).mkdir(parents=True, exist_ok=True)
        
    def scan_villages(self):
        """扫描文件夹中的村庄"""
        villages = {}
        work_path = Path(self.work_folder)
        
        # 首先确保工作文件夹存在
        if not work_path.exists():
            work_path.mkdir(parents=True, exist_ok=True)
            return villages
        
        # 从Excel中读取所有村庄（如果Excel存在）
        all_villages_from_excel = set()
        village_archived_status = {}
        
        if os.path.exists(self.excel_file):
            try:
                df = pd.read_excel(self.excel_file)
                if '村庄名称' in df.columns:
                    all_villages_from_excel = set(df['村庄名称'].dropna().tolist())
                    # 读取归档状态
                    for _, row in df.iterrows():
                        village_name = row['村庄名称']
                        archived_status = row.get('归档状态', '未归档')
                        village_archived_status[village_name] = str(archived_status) == '已归档'
            except Exception as e:
                print(f"读取Excel时出错: {e}")
        
        # 查找所有包含"村"的文件夹
        existing_folders = {}
        if work_path.exists():
            for item in work_path.iterdir():
                if item.is_dir() and '村' in item.name:
                    village_name = item.name
                    files = [f.name for f in item.iterdir() if f.is_file()]
                    existing_folders[village_name] = {
                        'folder_path': str(item),
                        'files': files
                    }
                    all_villages_from_excel.add(village_name)  # 确保文件夹中的村庄也被包含
        
        # 为每个村庄创建记录
        for village_name in all_villages_from_excel:
            # 检查是否已归档
            archived = village_archived_status.get(village_name, False)
            archive_time = None
            
            # 获取文件夹信息
            folder_path = existing_folders.get(village_name, {}).get('folder_path', '')
            files = existing_folders.get(village_name, {}).get('files', [])
            
            villages[village_name] = {
                'name': village_name,
                'folder_path': folder_path,
                'archived': archived,
                'files': files,
                'archive_time': archive_time
            }
            
        return villages
            
    def create_excel_if_not_exists(self):
        """创建Excel文件（如果不存在）"""
        if not os.path.exists(self.excel_file):
            df = pd.DataFrame(columns=['村庄名称', '归档状态', '文件数量', '归档时间', '备注'])
            df.to_excel(self.excel_file, index=False)
            
    def update_excel_record(self, village_name, archived=True):
        """更新Excel记录"""
        self.create_excel_if_not_exists()
        
        try:
            df = pd.read_excel(self.excel_file)
            
            # 确保必要的列存在
            required_columns = ['村庄名称', '归档状态', '文件数量', '归档时间', '备注']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ''
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 如果村庄已存在，更新记录
            if village_name in df['村庄名称'].values:
                df.loc[df['村庄名称'] == village_name, '归档状态'] = '已归档' if archived else '未归档'
                df.loc[df['村庄名称'] == village_name, '归档时间'] = current_time if archived else ''
                # 更新文件数量
                village_folder = Path(self.work_folder) / village_name
                if village_folder.exists():
                    file_count = len([f for f in village_folder.iterdir() if f.is_file()])
                    df.loc[df['村庄名称'] == village_name, '文件数量'] = file_count
            else:
                # 添加新记录
                village_folder = Path(self.work_folder) / village_name
                file_count = 0
                if village_folder.exists():
                    file_count = len([f for f in village_folder.iterdir() if f.is_file()])
                    
                new_row = {
                    '村庄名称': village_name,
                    '归档状态': '已归档' if archived else '未归档',
                    '文件数量': file_count,
                    '归档时间': current_time if archived else '',
                    '备注': ''
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                
            df.to_excel(self.excel_file, index=False)
        except Exception as e:
            print(f"更新Excel时出错: {e}")
            
    def archive_files(self, village_name, file_paths):
        """归档文件到指定村庄文件夹"""
        village_folder = Path(self.work_folder) / village_name
        village_folder.mkdir(exist_ok=True)
        
        success_count = 0
        for file_path in file_paths:
            try:
                src_path = Path(file_path)
                # 保持原文件名
                dst_path = village_folder / src_path.name
                if src_path.exists():
                    shutil.copy2(file_path, str(dst_path))
                    success_count += 1
            except Exception as e:
                print(f"复制文件 {file_path} 时出错: {e}")
                
        return success_count

class DocumentArchiverWidget(QWidget):
    """文档归档主界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("documentachiver")
        self.project_manager = ProjectManager()
        self.archive_manager = None
        self.current_project = None
        
        self.setup_ui()
        self.refresh_project_list()
        self.setup_timer()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        
        # 左侧面板
        left_panel = QFrame()
        left_panel.setFixedWidth(250)
        left_layout = QVBoxLayout(left_panel)
        
        # 项目管理标题
        title_label = StrongBodyLabel("项目管理")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        
        # 新建项目按钮
        self.new_project_btn = PrimaryPushButton("新建项目")
        self.new_project_btn.clicked.connect(self.create_new_project)
        
        # 项目列表
        self.project_list = QListWidget()
        self.project_list.itemClicked.connect(self.select_project)
        
        left_layout.addWidget(title_label)
        left_layout.addWidget(self.new_project_btn)
        left_layout.addWidget(self.project_list)
        
        # 右侧主面板
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        # 项目标题和工具栏
        header_layout = QHBoxLayout()
        self.project_title = StrongBodyLabel("请选择项目")
        self.project_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        
        self.refresh_btn = PushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_current_project)
        
        header_layout.addWidget(self.project_title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_btn)
        right_layout.addLayout(header_layout)
        
        # 项目统计
        self.stats_group = QGroupBox("项目统计")
        stats_layout = QHBoxLayout(self.stats_group)
        
        self.total_villages_label = BodyLabel("总村庄数: 0")
        self.archived_label = BodyLabel("已归档: 0")
        self.unarchived_label = BodyLabel("未归档: 0")
        self.completion_label = BodyLabel("完成率: 0%")
        
        stats_layout.addWidget(self.total_villages_label)
        stats_layout.addWidget(self.archived_label)
        stats_layout.addWidget(self.unarchived_label)
        stats_layout.addWidget(self.completion_label)
        stats_layout.addStretch()
        
        right_layout.addWidget(self.stats_group)
        
        # 项目列表添加右键菜单
        self.project_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.project_list.customContextMenuRequested.connect(self.show_project_context_menu)
        # 村庄卡片区域
        self.villages_scroll = QScrollArea()
        self.villages_scroll.setWidgetResizable(True)
        self.villages_widget = QWidget()
        self.villages_layout = QHBoxLayout(self.villages_widget)
        self.villages_layout.setAlignment(Qt.AlignLeft)
        self.villages_layout.setSpacing(10)
        self.villages_scroll.setWidget(self.villages_widget)
        
        right_layout.addWidget(QLabel("村庄状态:"))
        right_layout.addWidget(self.villages_scroll)
        
        # 未归档提醒区域
        self.unarchived_group = QGroupBox("未归档提醒")
        unarchived_layout = QVBoxLayout(self.unarchived_group)
        
        self.unarchived_text = QTextEdit()
        self.unarchived_text.setReadOnly(True)
        self.unarchived_text.setMaximumHeight(150)
        
        unarchived_layout.addWidget(self.unarchived_text)
        right_layout.addWidget(self.unarchived_group)
        
        # 任务规划区域
        self.tasks_group = QGroupBox("下一阶段任务规划")
        tasks_layout = QVBoxLayout(self.tasks_group)
        
        # 添加任务控件
        add_task_layout = QHBoxLayout()
        self.task_village_combo = ComboBox()
        self.task_date_edit = QDateEdit()
        self.task_date_edit.setDate(QDate.currentDate().addDays(1))
        self.task_notes_edit = LineEdit()
        self.task_notes_edit.setPlaceholderText("任务备注...")
        self.add_task_btn = PushButton("添加任务")
        self.add_task_btn.clicked.connect(self.add_task)
        
        add_task_layout.addWidget(QLabel("村庄:"))
        add_task_layout.addWidget(self.task_village_combo)
        add_task_layout.addWidget(QLabel("截止日期:"))
        add_task_layout.addWidget(self.task_date_edit)
        add_task_layout.addWidget(self.task_notes_edit)
        add_task_layout.addWidget(self.add_task_btn)
        
        # 任务列表
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(4)
        self.tasks_table.setHorizontalHeaderLabels(['村庄', '截止日期', '备注', '状态'])
        self.tasks_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        tasks_layout.addLayout(add_task_layout)
        tasks_layout.addWidget(self.tasks_table)
        
        right_layout.addWidget(self.tasks_group)
        
        # 添加到主布局
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([250, 950])
        
        main_layout.addWidget(splitter)
        
    def setup_timer(self):
        """设置定时器"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_refresh)
        self.timer.start(60000)  # 1分钟自动刷新一次
    
    def show_project_context_menu(self, position):
        """显示项目右键菜单"""
        item = self.project_list.itemAt(position)
        if item:
            project_id = item.data(Qt.UserRole)
            menu = self.get_project_context_menu(project_id)
            menu.exec(self.project_list.mapToGlobal(position))
            
    def get_project_context_menu(self, project_id):
        """获取项目右键菜单"""
        menu = QMenu(self)
        
        edit_action = QAction("编辑项目", self)
        edit_action.triggered.connect(lambda: self.edit_project(project_id))
        menu.addAction(edit_action)
        
        delete_action = QAction("删除项目", self)
        delete_action.triggered.connect(lambda: self.delete_project(project_id))
        menu.addAction(delete_action)
        
        return menu        
    
    def edit_project(self, project_id):
        """编辑项目"""
        project = self.project_manager.get_project(project_id)
        if not project:
            return
            
        # 创建编辑对话框
        from PySide6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox, QGridLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑项目")
        dialog.setModal(True)
        dialog.resize(500, 300)
        
        layout = QVBoxLayout(dialog)
        
        # 标题
        title_label = StrongBodyLabel("编辑项目信息")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setHorizontalSpacing(20)
        
        # 项目名称
        name_edit = LineEdit()
        name_edit.setText(project.get('name', ''))
        name_edit.setPlaceholderText("请输入项目名称")
        
        # 工作文件夹
        folder_edit = LineEdit()
        folder_edit.setText(project.get('work_folder', ''))
        folder_edit.setPlaceholderText("请选择工作文件夹")
        folder_btn = PushButton("浏览")
        
        def select_folder():
            current_path = folder_edit.text() if folder_edit.text() else ""
            folder = QFileDialog.getExistingDirectory(dialog, "选择工作文件夹", current_path)
            if folder:
                folder_edit.setText(folder)
                
        folder_btn.clicked.connect(select_folder)
        
        # Excel文件
        excel_edit = LineEdit()
        excel_edit.setText(project.get('excel_file', ''))
        excel_edit.setPlaceholderText("请选择Excel文件")
        excel_btn = PushButton("浏览")
        
        def select_excel():
            current_path = excel_edit.text() if excel_edit.text() else ""
            file, _ = QFileDialog.getOpenFileName(dialog, "选择Excel文件", current_path, "Excel Files (*.xlsx)")
            if not file and not excel_edit.text():  # 如果取消选择但原路径为空，提供创建新文件的选项
                file, _ = QFileDialog.getSaveFileName(dialog, "创建Excel文件", current_path, "Excel Files (*.xlsx)")
                if file and not file.endswith('.xlsx'):
                    file += '.xlsx'
            if file:
                excel_edit.setText(file)
                
        excel_btn.clicked.connect(select_excel)
        
        # 布局工作文件夹行
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(folder_edit)
        folder_layout.addWidget(folder_btn)
        
        # 布局Excel文件行
        excel_layout = QHBoxLayout()
        excel_layout.addWidget(excel_edit)
        excel_layout.addWidget(excel_btn)
        
        form_layout.addRow("项目名称:", name_edit)
        form_layout.addRow("工作文件夹:", folder_layout)
        form_layout.addRow("Excel文件:", excel_layout)
        
        # 显示当前统计信息
        stats_group = QGroupBox("当前项目统计")
        stats_layout = QGridLayout(stats_group)
        
        total_label = BodyLabel("总村庄数:")
        archived_label = BodyLabel("已归档:")
        unarchived_label = BodyLabel("未归档:")
        
        total_value = BodyLabel("0")
        archived_value = BodyLabel("0")
        unarchived_value = BodyLabel("0")
        
        if project.get('villages'):
            total_villages = len(project['villages'])
            archived_villages = sum(1 for v in project['villages'].values() if v.get('archived', False))
            unarchived_villages = total_villages - archived_villages
            
            total_value.setText(str(total_villages))
            archived_value.setText(str(archived_villages))
            unarchived_value.setText(str(unarchived_villages))
            unarchived_value.setStyleSheet("color: #dc3545; font-weight: bold;")
        
        stats_layout.addWidget(total_label, 0, 0)
        stats_layout.addWidget(total_value, 0, 1)
        stats_layout.addWidget(archived_label, 0, 2)
        stats_layout.addWidget(archived_value, 0, 3)
        stats_layout.addWidget(unarchived_label, 0, 4)
        stats_layout.addWidget(unarchived_value, 0, 5)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        layout.addLayout(form_layout)
        layout.addWidget(stats_group)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.Accepted:
            # 验证路径
            work_folder = folder_edit.text()
            excel_file = excel_edit.text()
            
            # 验证工作文件夹
            if work_folder and not os.path.exists(work_folder):
                reply = QMessageBox.question(
                    self, 
                    '文件夹不存在', 
                    f'工作文件夹 "{work_folder}" 不存在，是否创建？',
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                    QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Cancel:
                    return
                elif reply == QMessageBox.Yes:
                    try:
                        Path(work_folder).mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        QMessageBox.warning(self, "创建失败", f"创建文件夹失败: {str(e)}")
                        return
            
            # 验证Excel文件
            if excel_file:
                if not os.path.exists(excel_file):
                    reply = QMessageBox.question(
                        self, 
                        'Excel文件不存在', 
                        f'Excel文件 "{excel_file}" 不存在，是否创建？',
                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                        QMessageBox.Cancel
                    )
                    
                    if reply == QMessageBox.Cancel:
                        return
                    elif reply == QMessageBox.Yes:
                        try:
                            # 创建默认Excel模板
                            df = pd.DataFrame(columns=['村庄名称', '归档状态', '文件数量', '归档时间', '备注'])
                            df.to_excel(excel_file, index=False)
                        except Exception as e:
                            QMessageBox.warning(self, "创建失败", f"创建Excel文件失败: {str(e)}")
                            return
                else:
                    # 验证Excel文件格式
                    try:
                        pd.read_excel(excel_file)
                    except Exception as e:
                        QMessageBox.warning(self, "文件错误", f"Excel文件格式错误: {str(e)}")
                        return
            
            # 更新项目信息
            old_work_folder = project.get('work_folder', '')
            old_excel_file = project.get('excel_file', '')
            
            project['name'] = name_edit.text().strip()
            project['work_folder'] = work_folder.strip()
            project['excel_file'] = excel_file.strip()
            
            # 保存更新
            self.project_manager.save_projects()
            
            # 如果是当前项目，更新界面
            if self.current_project and self.current_project['id'] == project_id:
                self.current_project = project
                self.project_title.setText(project['name'])
                self.archive_manager = ArchiveManager(project['work_folder'], project['excel_file'])
                self.refresh_current_project()
            
            self.refresh_project_list()
            
            InfoBar.success(
                title='项目更新成功',
                content=f'项目 "{project["name"]}" 已更新',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )

    def auto_refresh(self):
        """自动刷新"""
        if self.current_project:
            self.refresh_current_project()
            
    def create_new_project(self):
        """创建新项目"""
        # 获取项目信息
        project_name, work_folder, excel_file = self.get_project_info()
        if not all([project_name, work_folder, excel_file]):
            return
            
        # 创建项目
        project_id = self.project_manager.create_project(project_name, work_folder, excel_file)
        
        # 初始化归档管理器
        self.archive_manager = ArchiveManager(work_folder, excel_file)
        
        # 扫描村庄
        villages = self.archive_manager.scan_villages()
        for village_name, village_data in villages.items():
            self.project_manager.update_project_village(project_id, village_name, village_data)
            
        # 刷新界面
        self.refresh_project_list()
        
        InfoBar.success(
            title='项目创建成功',
            content=f'项目 "{project_name}" 创建成功',
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )
        
    def get_project_info(self):
        """获取项目信息对话框"""
        from PySide6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("创建新项目")
        dialog.setModal(True)
        dialog.resize(400, 200)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        name_edit = LineEdit()
        name_edit.setPlaceholderText("请输入项目名称")
        
        folder_edit = LineEdit()
        folder_edit.setPlaceholderText("请选择工作文件夹")
        folder_btn = PushButton("浏览")
        
        def select_folder():
            folder = QFileDialog.getExistingDirectory(dialog, "选择工作文件夹")
            if folder:
                folder_edit.setText(folder)
                
        folder_btn.clicked.connect(select_folder)
        
        excel_edit = LineEdit()
        excel_edit.setPlaceholderText("请选择或创建Excel文件")
        excel_btn = PushButton("浏览")
        
        def select_excel():
            file, _ = QFileDialog.getSaveFileName(dialog, "选择Excel文件", "", "Excel Files (*.xlsx)")
            if file:
                if not file.endswith('.xlsx'):
                    file += '.xlsx'
                excel_edit.setText(file)
                
        excel_btn.clicked.connect(select_excel)
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(folder_edit)
        folder_layout.addWidget(folder_btn)
        
        excel_layout = QHBoxLayout()
        excel_layout.addWidget(excel_edit)
        excel_layout.addWidget(excel_btn)
        
        form_layout.addRow("项目名称:", name_edit)
        form_layout.addRow("工作文件夹:", folder_layout)
        form_layout.addRow("Excel文件:", excel_layout)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.Accepted:
            return name_edit.text(), folder_edit.text(), excel_edit.text()
        return None, None, None
        
    def refresh_project_list(self):
        """刷新项目列表"""
        self.project_list.clear()
        projects = self.project_manager.get_all_projects()
        
        for project in projects:
            item = QListWidgetItem(project['name'])
            item.setData(Qt.UserRole, project['id'])
            self.project_list.addItem(item)
            
    def select_project(self, item):
        """选择项目"""
        project_id = item.data(Qt.UserRole)
        self.current_project = self.project_manager.set_current_project(project_id)
        
        if self.current_project:
            self.project_title.setText(self.current_project['name'])
            work_folder = self.current_project['work_folder']
            excel_file = self.current_project['excel_file']
            self.archive_manager = ArchiveManager(work_folder, excel_file)
            self.refresh_current_project()
            
    def refresh_current_project(self):
        """刷新当前项目"""
        if not self.current_project:
            return
        
        # 重新扫描村庄（包括Excel中的所有村庄）
        villages = self.archive_manager.scan_villages()
        
        # 更新项目数据
        for village_name, village_data in villages.items():
            self.project_manager.update_project_village(
                self.current_project['id'], village_name, village_data
            )
            
        # 更新界面
        self.update_village_cards()
        self.update_statistics()
        self.update_unarchived_reminder()
        self.update_task_planning()

        
    def update_village_cards(self):
        """更新村庄卡片"""
        # 清除现有卡片
        for i in reversed(range(self.villages_layout.count())):
            widget = self.villages_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        # 添加村庄卡片
        if not self.current_project:
            return
            
        villages = self.current_project.get('villages', {})
        for village_name, village_data in villages.items():
            archived = village_data.get('archived', False)
            card = VillageCard(village_name, archived)
            card.file_dropped.connect(self.on_files_dropped)
            card.clicked.connect(self.on_village_clicked)
            self.villages_layout.addWidget(card)
            
        # 更新任务下拉框
        self.task_village_combo.clear()
        for village_name in villages.keys():
            self.task_village_combo.addItem(village_name)
            
    def update_statistics(self):
        """更新统计信息"""
        if not self.current_project:
            return
            
        villages = self.current_project.get('villages', {})
        total = len(villages)
        archived = sum(1 for v in villages.values() if v.get('archived', False))
        unarchived = total - archived
        completion = (archived / total * 100) if total > 0 else 0
        
        self.total_villages_label.setText(f"总村庄数: {total}")
        self.archived_label.setText(f"已归档: {archived}")
        self.unarchived_label.setText(f"未归档: {unarchived}")
        self.completion_label.setText(f"完成率: {completion:.1f}%")
        
    def update_unarchived_reminder(self):
        """更新未归档提醒"""
        if not self.current_project:
            self.unarchived_text.setPlainText("请先选择项目")
            return
            
        villages = self.current_project.get('villages', {})
        unarchived_villages = [name for name, data in villages.items() if not data.get('archived', False)]
        
        if not unarchived_villages:
            self.unarchived_text.setPlainText("🎉 恭喜！所有村庄都已归档完成！")
            return
            
        reminder_text = "⚠️ 以下村庄尚未归档：\n\n"
        for village_name in unarchived_villages:
            reminder_text += f"• {village_name}\n"
            
        reminder_text += f"\n共 {len(unarchived_villages)} 个村庄等待归档"
        self.unarchived_text.setPlainText(reminder_text)
        
    def update_task_planning(self):
        """更新任务规划"""
        if not self.current_project:
            return
            
        tasks = self.current_project.get('tasks', {})
        self.tasks_table.setRowCount(len(tasks))
        
        for row, (task_id, task_data) in enumerate(tasks.items()):
            self.tasks_table.setItem(row, 0, QTableWidgetItem(task_data['village_name']))
            self.tasks_table.setItem(row, 1, QTableWidgetItem(task_data['due_date']))
            self.tasks_table.setItem(row, 2, QTableWidgetItem(task_data.get('notes', '')))
            
            status = "已完成" if task_data.get('completed', False) else "进行中"
            status_item = QTableWidgetItem(status)
            if task_data.get('completed', False):
                status_item.setForeground(QColor(0, 128, 0))
            else:
                status_item.setForeground(QColor(255, 0, 0))
            self.tasks_table.setItem(row, 3, status_item)
            
    def on_files_dropped(self, village_name, file_paths):
        """文件拖拽处理"""
        if not self.archive_manager:
            return
            
        # 归档文件
        success_count = self.archive_manager.archive_files(village_name, file_paths)
        
        if success_count > 0:
            # 标记为已归档
            self.project_manager.mark_village_archived(self.current_project['id'], village_name)
            
            # 更新Excel记录
            self.archive_manager.update_excel_record(village_name, archived=True)
            
            # 刷新界面
            self.refresh_current_project()
            
            InfoBar.success(
                title='归档成功',
                content=f'成功归档 {success_count} 个文件到 {village_name}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
        else:
            InfoBar.warning(
                title='归档失败',
                content='文件归档过程中出现错误',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
            
    def on_village_clicked(self, village_name):
        """村庄卡片点击处理"""
        print(f"点击了村庄: {village_name}")
        
    def add_task(self):
        """添加任务"""
        if not self.current_project:
            return
            
        village_name = self.task_village_combo.currentText()
        due_date = self.task_date_edit.date().toString("yyyy-MM-dd")
        notes = self.task_notes_edit.text()
        
        if not village_name:
            InfoBar.warning(
                title='添加失败',
                content='请选择村庄',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
            return
            
        task_id = self.project_manager.add_task(
            self.current_project['id'], village_name, due_date, notes
        )
        
        self.update_task_planning()
        self.task_notes_edit.clear()
        
        InfoBar.success(
            title='任务添加成功',
            content=f'已为 {village_name} 添加任务',
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=1500,
            parent=self
        )

    def delete_project(self, project_id):
        """删除项目"""
        project = self.project_manager.get_project(project_id)
        if not project:
            return
            
        reply = QMessageBox.question(
            self, 
            '确认删除', 
            f'确定要删除项目 "{project["name"]}" 吗？\n\n注意：这只会删除项目记录，不会删除实际的文件和文件夹。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 从项目列表中删除
            if project_id in self.project_manager.projects:
                del self.project_manager.projects[project_id]
                self.project_manager.save_projects()
                
                # 如果删除的是当前项目，清空界面
                if self.current_project and self.current_project['id'] == project_id:
                    self.current_project = None
                    self.project_title.setText("请选择项目")
                    self.clear_project_view()
                
                self.refresh_project_list()
                
                InfoBar.success(
                    title='删除成功',
                    content=f'项目 "{project["name"]}" 已删除',
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=2000,
                    parent=self
                )

    def clear_project_view(self):
        """清空项目视图"""
        # 清空村庄卡片
        for i in reversed(range(self.villages_layout.count())):
            widget = self.villages_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        # 重置统计信息
        self.total_villages_label.setText("总村庄数: 0")
        self.archived_label.setText("已归档: 0")
        self.unarchived_label.setText("未归档: 0")
        self.completion_label.setText("完成率: 0%")
        
        # 清空提醒和任务
        self.unarchived_text.setPlainText("请先选择项目")
        self.tasks_table.setRowCount(0)
        self.task_village_combo.clear()     
   
class MainWindow(FluentWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文档归档管理系统")
        self.resize(1200, 800)
        
        # 创建主界面
        self.archiver_widget = DocumentArchiverWidget()
        self.addSubInterface(self.archiver_widget, "archiver", "文档归档")
        
        # 设置窗口居中
        self.center_window()
        
    def center_window(self):
        """窗口居中"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
     
def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("文档归档管理系统")
    app.setApplicationVersion("1.0.0")
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

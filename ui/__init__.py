from .family_manage_ui import FamilyManageUI
# from .land_manage_ui import LandManageUI
# from .subsidy_manage_ui import SubsidyManageUI
# from .person_manage_ui import PersonManageUI
from .main_window import MainWindow  # 注意这里应该是 MainWindow 而不是 MainUI
from .New_window  import NewWindow
__all__ = [
    'FamilyManageUI',
   # 'LandManageUI',
  #  'SubsidyManageUI',
    'MainWindow',
    'NewWindow'  # 确保这里与上面的导入名称一致
]

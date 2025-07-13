# models/__init__.py
from .family_controller import FamilyController
from .person_controller import PersonController
from .subsidy_controller import SubsidyController
from .report_controller import ReportController

#数据访问对象

__all__ = [
    'FamilyController', 
    'PersonController', 
    'SubsidyController', 
    'ReportController', 
]
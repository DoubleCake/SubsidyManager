from ui.rule_table_page import RuleTablePage
from services.subsidy_service import SubsidyService

def open_rule_page(self):
    page = RuleTablePage()
    page.show()        # 独立窗口，可拖动
    
open_rule_page( )
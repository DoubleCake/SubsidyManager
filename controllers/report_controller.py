from services.report_service import ReportService


class ReportController:
    def __init__(self, view):
        self.view = view
        self.service = ReportService()

    def generate_report(self):
        try:
            report_data = self.service.generate_report()
            self.view.report_output.setText(self.format_report(report_data))
        except Exception as e:
            self.view.show_error(f"生成报告时出错：{str(e)}")

    def format_report(self, data):
        result = "📊 补贴统计报告\n"
        result += "--------------------------\n"
        result += f"总家庭数: {data['total_families']}\n"
        result += f"总补贴金额: ￥{data['total_subsidy_amount']:.2f}\n"
        result += f"已发放补贴金额: ￥{data['distributed_amount']:.2f}\n"
        result += f"未发放补贴金额: ￥{data['pending_amount']:.2f}\n"
        result += f"人均补贴金额: ￥{data['average_per_family']:.2f}\n"
        result += "--------------------------\n"
        result += f"生成时间: {data['timestamp']}"
        return result
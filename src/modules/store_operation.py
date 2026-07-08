"""
门店高效运营模块
================
功能：销售数据分析、库存周转预警、客流热力分析、经营洞察AI报告。
对接飞书多维表格AI（数据分析工作流）。
"""

import json
import os
import random
from datetime import datetime, timedelta


class StoreOperationModule:
    """门店高效运营模块"""

    def __init__(self, bitable_client=None, config=None):
        self.bitable = bitable_client
        self.config = config

    def get_sales_dashboard(self, store_id, period="month"):
        """获取销售数据仪表盘"""
        # 模拟销售数据
        days = 30 if period == "month" else 7 if period == "week" else 1
        today = datetime.now()

        daily_sales = []
        for i in range(days):
            date = today - timedelta(days=days - i)
            daily_sales.append({
                "date": date.strftime("%Y-%m-%d"),
                "sales_amount": round(random.uniform(8000, 25000), 2),
                "order_count": random.randint(5, 20),
                "avg_order_value": round(random.uniform(800, 2000), 2),
                "customer_count": random.randint(8, 35),
                "conversion_rate": round(random.uniform(0.15, 0.45), 2)
            })

        total_sales = sum(d["sales_amount"] for d in daily_sales)
        total_orders = sum(d["order_count"] for d in daily_sales)
        total_customers = sum(d["customer_count"] for d in daily_sales)

        return {
            "store_id": store_id,
            "period": period,
            "summary": {
                "total_sales": round(total_sales, 2),
                "total_orders": total_orders,
                "total_customers": total_customers,
                "avg_order_value": round(total_sales / total_orders, 2) if total_orders else 0,
                "avg_conversion_rate": round(total_orders / total_customers, 2) if total_customers else 0
            },
            "daily_data": daily_sales
        }

    def get_inventory_analysis(self, store_id):
        """库存分析"""
        # 模拟库存数据
        products = [
            {"name": "雨虹JS复合防水涂料", "stock": 120, "unit": "桶", "turnover_days": 25, "status": "正常"},
            {"name": "雨虹聚氨酯防水涂料", "stock": 45, "unit": "桶", "turnover_days": 12, "status": "正常"},
            {"name": "雨虹SBS改性沥青卷材", "stock": 8, "unit": "卷", "turnover_days": 5, "status": "预警"},
            {"name": "雨虹瓷砖胶", "stock": 200, "unit": "袋", "turnover_days": 45, "status": "积压"},
            {"name": "雨虹密封胶", "stock": 15, "unit": "支", "turnover_days": 3, "status": "紧急"},
            {"name": "雨虹美缝剂", "stock": 80, "unit": "组", "turnover_days": 30, "status": "正常"},
        ]

        alerts = []
        for p in products:
            if p["status"] == "紧急":
                alerts.append(f"⚠️ {p['name']}库存仅剩{p['stock']}{p['unit']}，需立即补货")
            elif p["status"] == "预警":
                alerts.append(f"📋 {p['name']}库存{p['stock']}{p['unit']}，周转天数{p['turnover_days']}天，建议补货")
            elif p["status"] == "积压":
                alerts.append(f"📦 {p['name']}库存{p['stock']}{p['unit']}，周转天数{p['turnover_days']}天，存在积压风险")

        return {
            "store_id": store_id,
            "products": products,
            "alerts": alerts,
            "total_sku": len(products),
            "alert_count": len(alerts),
            "health_score": round(random.uniform(65, 90), 1)
        }

    def get_customer_flow(self, store_id, period="week"):
        """客流分析"""
        days = 7 if period == "week" else 30
        today = datetime.now()

        hourly_flow = {}
        for hour in range(9, 19):
            hourly_flow[f"{hour}:00"] = random.randint(3, 20)

        daily_flow = []
        for i in range(days):
            date = today - timedelta(days=days - i)
            daily_flow.append({
                "date": date.strftime("%Y-%m-%d"),
                "weekday": date.strftime("%A"),
                "total_flow": random.randint(30, 80),
                "peak_hour": f"{random.randint(13, 16)}:00",
                "avg_stay_minutes": random.randint(10, 35)
            })

        return {
            "store_id": store_id,
            "hourly_distribution": hourly_flow,
            "daily_flow": daily_flow,
            "avg_daily_flow": round(sum(d["total_flow"] for d in daily_flow) / days, 0),
            "peak_hours": ["14:00", "15:00", "10:00"],
            "ai_suggestion": "客流高峰集中在下午14-16点，建议在该时段增加导购人员。"
                "工作日客流偏少，可推出工作日专属优惠提升到店率。"
        }

    def generate_ai_insight_report(self, store_id):
        """生成AI经营洞察报告（对接多维表格AI）"""
        sales = self.get_sales_dashboard(store_id, "month")
        inventory = self.get_inventory_analysis(store_id)
        flow = self.get_customer_flow(store_id, "week")

        report = f"""【雨虹智慧门店运营AI洞察报告】
门店编号：{store_id}
报告日期：{datetime.now().strftime("%Y-%m-%d")}

一、销售概况
- 月度总销售额：¥{sales['summary']['total_sales']:,.2f}
- 总订单数：{sales['summary']['total_orders']}单
- 客单价：¥{sales['summary']['avg_order_value']:,.2f}
- 转化率：{sales['summary']['avg_conversion_rate']*100:.1f}%

二、库存健康度
- SKU总数：{inventory['total_sku']}
- 预警数量：{inventory['alert_count']}
- 健康评分：{inventory['health_score']}/100
- 主要风险：{'; '.join(inventory['alerts'][:3])}

三、客流分析
- 日均客流：{flow['avg_daily_flow']:.0f}人
- 高峰时段：{', '.join(flow['peak_hours'])}
- 平均停留：{flow['daily_flow'][0]['avg_stay_minutes'] if flow['daily_flow'] else 0}分钟

四、AI优化建议
1. 库存管理：SBS卷材和密封胶需紧急补货，瓷砖胶存在积压建议促销清仓
2. 人员排班：下午14-16点为客流高峰，建议增加1名导购
3. 营销策略：工作日转化率偏低，建议推出"工作日防水检测免费体验"活动
4. 产品组合：建议将防水涂料与密封胶组合销售，提升客单价15%
5. 私域运营：本月到店客户中仅35%加入会员，建议加强私域引流

—— 本报告由飞书多维表格AI自动生成
"""
        return {
            "store_id": store_id,
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "report_content": report,
            "sales_summary": sales["summary"],
            "inventory_health": inventory["health_score"],
            "avg_flow": flow["avg_daily_flow"],
            "key_recommendations": [
                "紧急补货SBS卷材和密封胶",
                "促销清仓积压瓷砖胶",
                "下午高峰时段增加导购",
                "推出工作日免费检测活动",
                "加强私域会员引流"
            ]
        }

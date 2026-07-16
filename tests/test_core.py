"""
雨虹渠道智慧运营助手 - 核心业务逻辑测试
======================================
覆盖巡检评分、产品搜索、客户画像、流失风险预测、渠道管理等核心逻辑。

运行方式：
    cd yuhong-smart-store
    python -m pytest tests/test_core.py -v
"""

import sys
import os
from datetime import datetime, timedelta

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from modules.store_inspection import StoreInspectionModule, INSPECTION_ITEMS
from modules.ai_shopping_guide import AIShoppingGuideModule
from modules.customer_relation import CustomerRelationModule
from modules.channel_management import ChannelManagementModule


class TestStoreInspection:
    """门店巡检模块测试"""

    def setup_method(self):
        self.module = StoreInspectionModule()

    def test_inspection_items_count(self):
        """巡检检查项应为6个维度"""
        assert len(INSPECTION_ITEMS) == 6

    def test_inspection_total_max_score(self):
        """巡检满分应为100分"""
        total = sum(item["max_score"] for item in INSPECTION_ITEMS)
        assert total == 100

    def test_submit_inspection_excellent(self):
        """总分≥90应为优秀"""
        scores = {
            "display": 20, "cleanliness": 15, "pricing": 15,
            "inventory": 20, "service": 15, "safety": 15
        }
        result = self.module.submit_inspection("S001", "张督导", scores)
        assert result["总分"] == 100
        assert result["巡检结果"] == "优秀"
        assert result["是否通过"] == "通过"

    def test_submit_inspection_pass(self):
        """总分≥80且<90应为合格"""
        scores = {
            "display": 16, "cleanliness": 12, "pricing": 12,
            "inventory": 16, "service": 12, "safety": 12
        }
        result = self.module.submit_inspection("S002", "李督导", scores)
        assert result["总分"] == 80
        assert result["巡检结果"] == "合格"
        assert result["是否通过"] == "通过"

    def test_submit_inspection_fail(self):
        """总分<80应为不合格"""
        scores = {
            "display": 10, "cleanliness": 8, "pricing": 8,
            "inventory": 10, "service": 8, "safety": 8
        }
        result = self.module.submit_inspection("S003", "王督导", scores)
        assert result["总分"] == 52
        assert result["巡检结果"] == "不合格"
        assert result["是否通过"] == "不通过"

    def test_inspection_record_fields(self):
        """巡检记录应包含所有必要字段"""
        scores = {"display": 18, "cleanliness": 14, "pricing": 14,
                  "inventory": 18, "service": 14, "safety": 14}
        result = self.module.submit_inspection("S004", "测试", scores)
        required_fields = ["门店编号", "巡检人", "巡检时间", "总分", "巡检结果", "是否通过"]
        for field in required_fields:
            assert field in result, f"缺少字段: {field}"


class TestAIShoppingGuide:
    """AI导购模块测试"""

    def setup_method(self):
        self.module = AIShoppingGuideModule()

    def test_load_products(self):
        """产品知识库应能正常加载"""
        products = self.module._load_products()
        assert isinstance(products, list)
        assert len(products) > 0

    def test_search_products_by_keyword(self):
        """关键词搜索应返回匹配的产品"""
        results = self.module.search_products(keyword="防水")
        assert isinstance(results, list)

    def test_search_products_by_category(self):
        """分类搜索应返回指定分类的产品"""
        results = self.module.search_products(category="防水涂料")
        assert isinstance(results, list)
        for p in results:
            assert p.get("category") == "防水涂料"

    def test_search_products_empty_result(self):
        """不存在的关键词应返回空列表"""
        results = self.module.search_products(keyword="不存在的产品XYZ")
        assert results == []

    def test_get_product_detail(self):
        """应根据产品ID获取详情"""
        products = self.module._load_products()
        if products:
            first_id = products[0].get("id")
            detail = self.module.get_product_detail(first_id)
            assert detail is not None
            assert detail.get("id") == first_id


class TestCustomerRelation:
    """客户维护模块测试"""

    def setup_method(self):
        self.module = CustomerRelationModule()

    def test_build_customer_profile(self):
        """应正确构建客户画像"""
        data = {
            "id": "C001",
            "name": "张三",
            "phone": "13800138000",
            "total_purchase": 12000,
            "purchase_count": 5,
            "last_purchase_date": datetime.now().strftime("%Y-%m-%d"),
            "needs": "卫生间防水",
        }
        profile = self.module.build_customer_profile(data)
        assert profile["customer_id"] == "C001"
        assert profile["name"] == "张三"
        assert "高价值客户" in profile["tags"] or "中等价值客户" in profile["tags"]
        assert "卫生间防水需求" in profile["tags"]

    def test_member_level_diamond(self):
        """累计消费≥20000应为钻石会员"""
        level = self.module._calculate_member_level(25000)
        assert level == "钻石会员"

    def test_member_level_gold(self):
        """累计消费≥10000且<20000应为金卡会员"""
        level = self.module._calculate_member_level(15000)
        assert level == "金卡会员"

    def test_member_level_silver(self):
        """累计消费≥5000且<10000应为银卡会员"""
        level = self.module._calculate_member_level(7000)
        assert level == "银卡会员"

    def test_member_level_normal(self):
        """累计消费<5000应为普通会员"""
        level = self.module._calculate_member_level(3000)
        assert level == "普通会员"

    def test_churn_risk_high(self):
        """超过180天未购买应为高流失风险"""
        data = {"last_purchase_date": (datetime.now() - timedelta(days=200)).strftime("%Y-%m-%d")}
        risk = self.module._calculate_churn_risk(data)
        assert risk == "高"

    def test_churn_risk_medium(self):
        """超过90天未购买应为中流失风险"""
        data = {"last_purchase_date": (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")}
        risk = self.module._calculate_churn_risk(data)
        assert risk == "中"

    def test_churn_risk_low(self):
        """90天内购买过应为低流失风险"""
        data = {"last_purchase_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")}
        risk = self.module._calculate_churn_risk(data)
        assert risk == "低"

    def test_churn_risk_no_data(self):
        """无购买记录应为高流失风险"""
        risk = self.module._calculate_churn_risk({})
        assert risk == "高"

    def test_tags_high_value(self):
        """消费>10000应标记为高价值客户"""
        tags = self.module._generate_tags({"total_purchase": 15000, "purchase_count": 3})
        assert "高价值客户" in tags

    def test_tags_high_frequency(self):
        """购买次数>5应标记为高频复购"""
        tags = self.module._generate_tags({"total_purchase": 3000, "purchase_count": 6})
        assert "高频复购" in tags

    def test_predict_next_purchase_insufficient(self):
        """购买次数<2应返回数据不足"""
        result = self.module._predict_next_purchase({"purchase_count": 1})
        assert result == "数据不足"


class TestChannelManagement:
    """渠道管理中枢模块测试"""

    def setup_method(self):
        self.module = ChannelManagementModule()

    def test_compliance_dashboard_structure(self):
        """合规率看板应返回正确数据结构"""
        result = self.module.get_compliance_dashboard()
        assert "national_compliance_rate" in result
        assert "total_stores" in result
        assert "region_ranking" in result
        assert "store_type_compliance" in result
        assert "rectification_tracking" in result
        assert "ai_insight" in result
        assert isinstance(result["region_ranking"], list)
        assert len(result["region_ranking"]) == 7

    def test_compliance_dashboard_region_data(self):
        """各区域合规率数据应完整"""
        result = self.module.get_compliance_dashboard()
        for region in result["region_ranking"]:
            assert "region" in region
            assert "compliance_rate" in region
            assert "total_stores" in region
            assert "passed_stores" in region
            assert "rectification_rate" in region
            assert "rank" in region

    def test_compliance_dashboard_national_rate(self):
        """全国合规率应为合理数值"""
        result = self.module.get_compliance_dashboard()
        assert 0 < result["national_compliance_rate"] <= 100

    def test_smart_dispatch_returns_recommended_store(self):
        """合规排名应返回推荐网点"""
        order_info = {
            "product": "雨虹JS复合防水涂料",
            "quantity": 10,
            "address": "河南省郑州市新郑市",
            "urgent": False
        }
        result = self.module.smart_dispatch(order_info)
        assert "recommended_store" in result
        assert "store_name" in result["recommended_store"]
        assert "match_score" in result["recommended_store"]
        assert "delivery_plan" in result
        assert "estimated_delivery_hours" in result

    def test_smart_dispatch_urgent_order(self):
        """紧急订单分单应包含加急信息"""
        order_info = {
            "product": "雨虹SBS改性沥青卷材",
            "quantity": 50,
            "address": "河南省郑州市新郑市",
            "urgent": True
        }
        result = self.module.smart_dispatch(order_info)
        assert result["order_info"]["urgent"] is True
        assert "紧急" in result["delivery_plan"]

    def test_smart_dispatch_alternative_stores(self):
        """合规排名应返回备选网点"""
        order_info = {"product": "雨虹密封胶", "quantity": 5}
        result = self.module.smart_dispatch(order_info)
        assert "alternative_stores" in result
        assert isinstance(result["alternative_stores"], list)

    def test_fulfillment_monitor_overdue_alerts(self):
        """库存预警应返回预警列表"""
        result = self.module.get_fulfillment_monitor()
        assert "overdue_alerts" in result
        assert isinstance(result["overdue_alerts"], list)
        assert len(result["overdue_alerts"]) >= 1

    def test_fulfillment_monitor_orders_count(self):
        """库存预警应返回8个在途订单"""
        result = self.module.get_fulfillment_monitor()
        assert len(result["orders"]) == 8
        assert result["summary"]["total_in_transit"] == 8

    def test_fulfillment_monitor_overdue_marked(self):
        """超时订单应标记is_overdue为True"""
        result = self.module.get_fulfillment_monitor()
        for alert in result["overdue_alerts"]:
            assert alert["is_overdue"] is True
            assert alert["risk_level"] == "超时预警"

    def test_store_ranking_default_dimension(self):
        """门店排名默认按销售额排序"""
        result = self.module.get_store_ranking()
        assert result["dimension"] == "sales"
        assert len(result["ranking"]) == 10
        sales_values = [s["sales_万元"] for s in result["ranking"]]
        assert sales_values == sorted(sales_values, reverse=True)

    def test_store_ranking_by_compliance(self):
        """门店排名按合规率应正确排序"""
        result = self.module.get_store_ranking(dimension='compliance')
        assert result["dimension"] == "compliance"
        compliance_values = [s["compliance_rate"] for s in result["ranking"]]
        assert compliance_values == sorted(compliance_values, reverse=True)

    def test_store_ranking_rank_assignment(self):
        """门店排名应正确分配排名序号"""
        result = self.module.get_store_ranking()
        for i, store in enumerate(result["ranking"]):
            assert store["rank"] == i + 1

    def test_expansion_tracking_structure(self):
        """渠道拓展应返回5个新网点"""
        result = self.module.get_expansion_tracking()
        assert len(result["new_stores"]) == 5
        assert "summary" in result
        for store in result["new_stores"]:
            assert "选址评分" in store
            assert "开业进度" in store
            assert "租金评估" in store
            assert "当前阶段" in store

    def test_channel_insight_structure(self):
        """渠道经营洞察应返回正确数据结构"""
        result = self.module.get_channel_insight()
        assert "region_ranking" in result
        assert "product_sales_top5" in result
        assert "trend_analysis" in result
        assert len(result["product_sales_top5"]) == 5
        assert "ai_insight" in result

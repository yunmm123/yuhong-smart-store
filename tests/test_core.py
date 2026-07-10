"""
雨虹智慧门店运营助手 - 核心业务逻辑测试
======================================
覆盖巡检评分、产品搜索、客户画像、流失风险预测等核心逻辑。

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

"""
门店巡检模块
============
功能：门店陈列合规性AI检测、移动巡检表单、巡检结果自动同步。
对接飞书妙搭（低代码巡检应用）+ 多维表格（数据存储）。
"""

import json
import os
import re
from datetime import datetime
import random


# 巡检检查项标准
INSPECTION_ITEMS = [
    {"id": "display", "name": "产品陈列标准", "max_score": 20, "check_points": [
        "防水材料按品类分区陈列",
        "畅销品放置在黄金视线区域",
        "陈列面整洁无积灰",
        "价签与产品对应准确"
    ]},
    {"id": "cleanliness", "name": "门店卫生状况", "max_score": 15, "check_points": [
        "地面清洁无污渍",
        "展架无灰尘",
        "样品无破损",
        "照明设备正常运作"
    ]},
    {"id": "pricing", "name": "价签与促销物料", "max_score": 15, "check_points": [
        "价签信息完整（品名、规格、价格）",
        "促销海报按公司规范张贴",
        "活动信息及时更新",
        "价签无缺失"
    ]},
    {"id": "inventory", "name": "库存与样品展示", "max_score": 20, "check_points": [
        "样品库存充足",
        "滞销品及时下架",
        "新品上架及时",
        "库存与系统数据一致"
    ]},
    {"id": "service", "name": "服务规范", "max_score": 15, "check_points": [
        "店员着统一工装",
        "接待话术规范",
        "客户咨询响应及时",
        "施工预约流程清晰"
    ]},
    {"id": "safety", "name": "安全合规", "max_score": 15, "check_points": [
        "消防通道畅通",
        "危险品按规定存放",
        "电气设备安全",
        "应急标识完好"
    ]}
]


class StoreInspectionModule:
    """门店巡检模块"""

    def __init__(self, bitable_client=None, config=None, aily_client=None):
        self.bitable = bitable_client
        self.config = config
        self.aily = aily_client
        self.mock_data_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'inspection_records.json'
        )

    def get_inspection_template(self):
        """获取巡检检查模板（供妙搭应用使用）"""
        return {
            "template_name": "东方雨虹门店巡检表",
            "version": "2.0",
            "total_max_score": 100,
            "items": INSPECTION_ITEMS,
            "created_at": datetime.now().isoformat()
        }

    def submit_inspection(self, store_id, inspector, scores, photos=None, notes=""):
        """
        提交巡检结果
        scores: {"display": 18, "cleanliness": 14, ...}
        """
        total_score = sum(scores.values())
        passed = total_score >= 80
        level = "优秀" if total_score >= 90 else "合格" if total_score >= 80 else "不合格"

        record = {
            "门店编号": store_id,
            "巡检人": inspector,
            "巡检时间": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "陈列标准得分": scores.get("display", 0),
            "卫生状况得分": scores.get("cleanliness", 0),
            "价签物料得分": scores.get("pricing", 0),
            "库存样品得分": scores.get("inventory", 0),
            "服务规范得分": scores.get("service", 0),
            "安全合规得分": scores.get("safety", 0),
            "总分": total_score,
            "巡检结果": level,
            "是否通过": "通过" if passed else "未通过",
            "备注": notes,
            "照片附件": photos or []
        }

        if self.bitable and not self.config.USE_MOCK_DATA:
            # 写入飞书多维表格
            self.bitable.create_record(
                self.config.BITABLE_INSPECTION_TABLE_ID, record
            )

        return record

    def ai_detect_display_compliance(self, image_description):
        """
        AI图像识别检测陈列合规性。
        优先通过飞书aily智能体分析图片描述，未配置aily或调用失败时降级为模拟检测。
        """
        # 优先使用aily智能体分析
        if self.aily and self.config and not self.config.USE_MOCK_DATA:
            try:
                result = self.aily.chat(
                    f"请分析以下门店陈列描述，评估货架利用率、价签覆盖率、卫生状况，并指出问题：{image_description}"
                )
                reply = result.get("reply", "")
                # 尝试从aily回复中提取结构化信息，同时保留原始分析文本
                detections = self._parse_aily_detection(reply, image_description)
                print("[INFO] aily陈列合规性检测完成")
                return detections
            except Exception as e:
                print(f"[WARN] aily分析失败，降级使用模拟检测: {e}")

        # 降级：使用模拟AI检测
        return self._mock_detect_display_compliance()

    def _parse_aily_detection(self, reply, image_description):
        """
        解析aily智能体回复，提取结构化检测结果。
        尝试从文本中匹配百分比/小数数值；无法提取的字段保留为None。
        返回格式与模拟检测保持一致，额外附带aily原始分析文本。
        """
        def _extract_ratio(keywords):
            """从回复中提取与关键词关联的比率值（0~1）"""
            for kw in keywords:
                # 匹配 "关键词...85%" 或 "关键词...0.85" 等模式
                pattern = kw + r'[^\d]*?(\d+\.?\d*)\s*%'
                m = re.search(pattern, reply)
                if m:
                    return round(float(m.group(1)) / 100, 2)
                pattern2 = kw + r'[^\d]*?(0\.\d+)'
                m = re.search(pattern2, reply)
                if m:
                    return round(float(m.group(1)), 2)
            return None

        shelf_utilization = _extract_ratio(["货架利用率", "利用率"])
        price_tag_coverage = _extract_ratio(["价签覆盖率", "覆盖率"])
        cleanliness_score = _extract_ratio(["卫生", "清洁"])

        # 根据提取到的数值推断合规状态
        issues = []
        if shelf_utilization is not None and shelf_utilization < 0.8:
            issues.append("部分货架利用率偏低，建议补充样品")
        if price_tag_coverage is not None and price_tag_coverage < 0.9:
            issues.append(f"约{int((1-price_tag_coverage)*100)}%的商品缺少价签")
        if cleanliness_score is not None and cleanliness_score < 0.85:
            issues.append("部分展架存在积灰，需及时清洁")

        overall = "合规" if len(issues) == 0 else "需整改"

        return {
            "product_categories": [],
            "shelf_utilization": shelf_utilization,
            "price_tag_coverage": price_tag_coverage,
            "cleanliness_score": cleanliness_score,
            "issues_detected": issues,
            "overall_compliance": overall,
            "ai_suggestion": reply,
            "aily_analysis": reply,
            "source": "feishu_aily"
        }

    def _mock_detect_display_compliance(self):
        """模拟AI检测结果（Demo模式 / aily不可用时的fallback）"""
        # 模拟AI检测结果
        detections = {
            "product_categories": ["防水涂料", "瓷砖胶", "密封胶", "美缝剂"],
            "shelf_utilization": round(random.uniform(0.65, 0.95), 2),
            "price_tag_coverage": round(random.uniform(0.70, 0.98), 2),
            "cleanliness_score": round(random.uniform(0.75, 0.95), 2),
            "issues_detected": []
        }

        issues = []
        if detections["shelf_utilization"] < 0.8:
            issues.append("部分货架利用率偏低，建议补充样品")
        if detections["price_tag_coverage"] < 0.9:
            issues.append(f"约{int((1-detections['price_tag_coverage'])*100)}%的商品缺少价签")
        if detections["cleanliness_score"] < 0.85:
            issues.append("部分展架存在积灰，需及时清洁")

        detections["issues_detected"] = issues
        detections["overall_compliance"] = "合规" if len(issues) == 0 else "需整改"
        detections["ai_suggestion"] = "；".join(issues) if issues else "门店陈列合规，继续保持"

        return detections

    def get_inspection_history(self, store_id=None, limit=20):
        """获取巡检历史记录"""
        if self.bitable and not self.config.USE_MOCK_DATA:
            filter_cond = None
            if store_id:
                filter_cond = f'CurrentValue.[门店编号] = "{store_id}"'
            records = self.bitable.list_records(
                self.config.BITABLE_INSPECTION_TABLE_ID,
                filter_condition=filter_cond
            )
            return records[:limit]
        else:
            # 使用模拟数据
            try:
                with open(self.mock_data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if store_id:
                    data = [r for r in data if r.get("门店编号") == store_id]
                return data[:limit]
            except FileNotFoundError:
                return []

    def generate_inspection_report(self, store_id):
        """生成门店巡检分析报告"""
        history = self.get_inspection_history(store_id)

        if not history:
            return {"error": "暂无巡检记录"}

        avg_score = sum(r.get("总分", 0) for r in history) / len(history)
        pass_rate = sum(1 for r in history if r.get("是否通过") == "通过") / len(history)

        # 趋势分析
        recent_scores = [r.get("总分", 0) for r in history[:5]]
        trend = "上升" if len(recent_scores) >= 2 and recent_scores[0] > recent_scores[-1] else "下降" if len(recent_scores) >= 2 and recent_scores[0] < recent_scores[-1] else "平稳"

        # 薄弱项分析
        item_record_keys = {
            "display": "陈列标准得分",
            "cleanliness": "卫生状况得分",
            "pricing": "价签物料得分",
            "inventory": "库存样品得分",
            "service": "服务规范得分",
            "safety": "安全合规得分"
        }
        category_scores = {}
        for item in INSPECTION_ITEMS:
            record_key = item_record_keys.get(item["id"], f"{item['name']}得分")
            scores = [r.get(record_key, 0) for r in history]
            if scores:
                category_scores[item["name"]] = sum(scores) / len(scores)

        weakest = min(category_scores, key=category_scores.get) if category_scores else "无"

        return {
            "store_id": store_id,
            "inspection_count": len(history),
            "average_score": round(avg_score, 1),
            "pass_rate": f"{pass_rate*100:.0f}%",
            "trend": trend,
            "weakest_area": weakest,
            "ai_recommendation": f"门店平均得分{avg_score:.1f}分，趋势{trend}。"
                f"薄弱项为「{weakest}」，建议重点改进。"
                f"通过率{pass_rate*100:.0f}%，"
                + ("整体表现良好。" if pass_rate > 0.8 else "需加强管理。"),
            "score_history": recent_scores
        }

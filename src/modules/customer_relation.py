"""
私域客户维护模块
================
功能：客户画像构建、AI话术推荐、跟进任务自动生成、复购预测。
对接飞书aily（智能跟进）+ 多维表格（客户管理）。
"""

import json
import os
import random
from datetime import datetime, timedelta


class CustomerRelationModule:
    """私域客户维护模块"""

    def __init__(self, aily_client=None, bitable_client=None, config=None):
        self.aily = aily_client
        self.bitable = bitable_client
        self.config = config

    def build_customer_profile(self, customer_data):
        """构建客户画像"""
        profile = {
            "customer_id": customer_data.get("id", ""),
            "name": customer_data.get("name", ""),
            "phone": customer_data.get("phone", ""),
            "registration_date": customer_data.get("registration_date", ""),
            "tags": self._generate_tags(customer_data),
            "lifetime_value": customer_data.get("total_purchase", 0),
            "purchase_frequency": customer_data.get("purchase_count", 0),
            "last_purchase_date": customer_data.get("last_purchase_date", ""),
            "preferred_category": customer_data.get("preferred_category", "防水涂料"),
            "preferred_channel": customer_data.get("preferred_channel", "门店"),
            "member_level": self._calculate_member_level(customer_data.get("total_purchase", 0)),
            "churn_risk": self._calculate_churn_risk(customer_data),
            "next_purchase_prediction": self._predict_next_purchase(customer_data),
        }
        return profile

    def _generate_tags(self, data):
        """自动生成客户标签"""
        tags = []
        total = data.get("total_purchase", 0)
        count = data.get("purchase_count", 0)

        if total > 10000:
            tags.append("高价值客户")
        elif total > 5000:
            tags.append("中等价值客户")
        else:
            tags.append("潜力客户")

        if count > 5:
            tags.append("高频复购")
        elif count > 2:
            tags.append("多次购买")
        else:
            tags.append("新客")

        if "卫生间" in str(data.get("needs", "")):
            tags.append("卫生间防水需求")
        if "外墙" in str(data.get("needs", "")):
            tags.append("外墙防水需求")
        if "屋顶" in str(data.get("needs", "")):
            tags.append("屋面防水需求")

        return tags

    def _calculate_member_level(self, total_purchase):
        if total_purchase >= 20000:
            return "钻石会员"
        elif total_purchase >= 10000:
            return "金卡会员"
        elif total_purchase >= 5000:
            return "银卡会员"
        else:
            return "普通会员"

    def _calculate_churn_risk(self, data):
        """计算流失风险"""
        last_purchase = data.get("last_purchase_date", "")
        if not last_purchase:
            return "高"

        try:
            last_date = datetime.strptime(last_purchase, "%Y-%m-%d")
            days_since = (datetime.now() - last_date).days

            if days_since > 180:
                return "高"
            elif days_since > 90:
                return "中"
            else:
                return "低"
        except:
            return "未知"

    def _predict_next_purchase(self, data):
        """预测下次购买时间"""
        count = data.get("purchase_count", 0)
        if count < 2:
            return "数据不足"

        # 模拟预测
        days_ahead = random.randint(30, 90)
        predicted_date = datetime.now() + timedelta(days=days_ahead)
        return predicted_date.strftime("%Y-%m-%d")

    def generate_followup_script(self, customer_profile, scenario="repurchase"):
        """
        生成AI跟进话术
        实际对接飞书aily，Demo模式使用模板生成
        """
        name = customer_profile.get("name", "客户")
        level = customer_profile.get("member_level", "普通会员")
        preferred = customer_profile.get("preferred_category", "防水材料")
        tags = customer_profile.get("tags", [])

        scripts = {
            "repurchase": f"""【复购跟进话术】
客户：{name}（{level}）
标签：{'、'.join(tags)}

开场白：
"{name}您好！我是雨虹门店的专属顾问小虹。上次您购买的{preferred}使用效果怎么样？
现在我们新到了一批升级款产品，针对您之前的需求做了优化。
作为{level}，您本次购买可享专属9折优惠，还赠送一次免费上门检测服务。
您看这周末方便来店里看看吗？"

跟进要点：
1. 询问上次购买产品的使用体验
2. 推荐升级款或配套产品
3. 强调会员专属优惠
4. 邀请到店体验
5. 记录客户反馈，更新画像
""",
            "festival": f"""【节日关怀话术】
客户：{name}（{level}）

"{name}您好！端午安康！🌿
感谢您一直信任雨虹。值此佳节，我们为您准备了{level}专属礼遇：
- 免费房屋防水健康检测1次
- 全场产品会员价基础上再享95折
- 赠送雨虹定制雨伞1把
活动持续到月底，随时欢迎您来店里坐坐～"

跟进要点：
1. 节日问候，拉近距离
2. 会员专属礼遇提升归属感
3. 低门槛免费服务引流到店
4. 设置截止时间制造紧迫感
""",
            "winback": f"""【流失挽回话术】
客户：{name}（{level}，流失风险：{customer_profile.get('churn_risk', '高')}）

"{name}您好！好久不见，我是雨虹的小虹。
注意到您有一段时间没来店里了，想了解下最近是否有防水方面的需求？
我们近期推出了'旧房防水焕新'专项服务，针对老客户有特别优惠：
- 免费上门勘测漏水点
- 10年质保防水方案
- 分期0利息
上次您关注的{preferred}现在也有新款到货，要不要我先发您看看？"

跟进要点：
1. 温暖问候，不直接推销
2. 提供有价值的免费服务
3. 低门槛重新激活
4. 用新款产品引发兴趣
5. 不强求，保持友好关系
"""
        }

        return scripts.get(scenario, scripts["repurchase"])

    def auto_create_followup_task(self, customer_profile):
        """自动创建跟进任务"""
        churn_risk = customer_profile.get("churn_risk", "低")
        level = customer_profile.get("member_level", "普通会员")

        tasks = []

        if churn_risk == "高":
            tasks.append({
                "task_type": "流失挽回",
                "priority": "高",
                "deadline": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                "action": "电话回访，了解客户现状",
                "script_scenario": "winback"
            })

        if level in ["金卡会员", "钻石会员"]:
            tasks.append({
                "task_type": "VIP关怀",
                "priority": "中",
                "deadline": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "action": "发送新品推荐+专属优惠",
                "script_scenario": "repurchase"
            })

        # 定期跟进
        tasks.append({
            "task_type": "定期关怀",
            "priority": "低",
            "deadline": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "action": "微信/飞书消息关怀，分享防水知识",
            "script_scenario": "festival"
        })

        return tasks

    def get_customer_segmentation(self, customers):
        """客户分层分析"""
        segments = {
            "高价值活跃": [],
            "高价值流失风险": [],
            "潜力客户": [],
            "新客待培育": [],
            "沉睡客户": []
        }

        for c in customers:
            profile = self.build_customer_profile(c)
            ltv = profile["lifetime_value"]
            risk = profile["churn_risk"]

            if ltv > 10000 and risk == "低":
                segments["高价值活跃"].append(profile)
            elif ltv > 10000 and risk in ["中", "高"]:
                segments["高价值流失风险"].append(profile)
            elif ltv > 3000:
                segments["潜力客户"].append(profile)
            elif profile["purchase_frequency"] <= 1:
                segments["新客待培育"].append(profile)
            else:
                segments["沉睡客户"].append(profile)

        return {
            "segment_summary": {k: len(v) for k, v in segments.items()},
            "total_customers": len(customers),
            "segments": segments,
            "ai_strategy": {
                "高价值活跃": "保持服务品质，定期推送新品，提升复购频次",
                "高价值流失风险": "立即启动挽回计划，专属顾问1对1回访",
                "潜力客户": "设计升级路径，推荐高毛利配套产品",
                "新客待培育": "发送防水知识科普+首次复购优惠券",
                "沉睡客户": "批量短信触达，低成本唤醒"
            }
        }

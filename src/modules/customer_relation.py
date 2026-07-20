"""
私域客户维护模块
================
功能：客户画像构建、AI话术推荐、跟进任务自动生成、复购预测。
对接飞书aily（智能跟进）+ 多维表格（客户管理）。
"""

import json
from datetime import datetime, timedelta


def _val(fields, key, default=""):
    """通用值提取：兼容文本/数字/单选/公式等Bitable字段，单值取首个文本"""
    v = fields.get(key, default)
    if isinstance(v, list) and v:
        return v[0].get("text", v[0]) if isinstance(v[0], dict) else v[0]
    return v


def _val_multi(fields, key):
    """多选字段提取：返回所有文本组成的列表"""
    v = fields.get(key, [])
    if isinstance(v, list):
        return [item.get("text", item) if isinstance(item, dict) else item for item in v]
    return [v] if v else []


def _date_to_str(v):
    """将Bitable日期字段(毫秒时间戳)或字符串转换为%Y-%m-%d字符串"""
    if isinstance(v, list) and v:
        v = v[0].get("text", v[0]) if isinstance(v[0], dict) else v[0]
    if isinstance(v, (int, float)) and v > 1000000000:
        return datetime.fromtimestamp(v / 1000).strftime("%Y-%m-%d")
    if not v:
        return ""
    return str(v)[:10]


def _to_number(v, default=0):
    """确保返回数字类型（兼容字符串数字）"""
    if isinstance(v, bool):
        return default
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        try:
            return float(v) if "." in v else int(v)
        except ValueError:
            return default
    return default


# 客户字段别名映射（兼容Bitable中文键与API英文键）
_CUSTOMER_FIELD_ALIASES = {
    "id": ["id", "customer_id", "客户编号"],
    "name": ["name", "客户姓名"],
    "phone": ["phone", "手机号"],
    "customer_type": ["customer_type", "客户类型"],
    "registration_date": ["registration_date", "注册日期"],
    "total_purchase": ["total_purchase", "累计消费元", "lifetime_value"],
    "purchase_count": ["purchase_count", "购买次数", "purchase_frequency"],
    "last_purchase_date": ["last_purchase_date", "最近购买日期"],
    "preferred_category": ["preferred_category", "偏好品类"],
    "preferred_channel": ["preferred_channel", "偏好渠道"],
    "needs": ["needs", "需求标签"],
    "member_level": ["member_level", "会员等级"],
    "churn_risk": ["churn_risk", "流失风险"],
    "ai_tags": ["ai_tags", "AI客户标签"],
}


class CustomerRelationModule:
    """私域客户维护模块"""

    def __init__(self, aily_client=None, bitable_client=None, config=None):
        self.aily = aily_client
        self.bitable = bitable_client
        self.config = config

    def get_customers_from_bitable(self):
        """从飞书多维表格客户表读取所有客户记录，返回标准化字典列表"""
        if not (self.bitable and self.config and not self.config.USE_MOCK_DATA):
            return []

        try:
            records = self.bitable.list_records(
                self.config.BITABLE_CUSTOMER_TABLE_ID,
                page_size=100
            )
        except Exception:
            return []

        customers = []
        for r in records or []:
            f = r.get("fields", {})
            # 需求标签为多选字段，合并为字符串
            needs_list = _val_multi(f, "需求标签")
            customers.append({
                "id": _val(f, "客户编号"),
                "name": _val(f, "客户姓名"),
                "phone": _val(f, "手机号"),
                "customer_type": _val(f, "客户类型"),
                "registration_date": _date_to_str(f.get("注册日期", "")),
                "total_purchase": _to_number(_val(f, "累计消费元", 0)),
                "purchase_count": _to_number(_val(f, "购买次数", 0)),
                "last_purchase_date": _date_to_str(f.get("最近购买日期", "")),
                "preferred_category": _val(f, "偏好品类"),
                "preferred_channel": _val(f, "偏好渠道"),
                "needs": "、".join(str(x) for x in needs_list if x),
                "member_level": _val(f, "会员等级"),
                "churn_risk": _val(f, "流失风险"),
                "ai_tags": _val(f, "AI客户标签"),
            })
        return customers

    def build_customer_profile(self, customer_data):
        """构建客户画像（兼容Bitable格式与API格式输入）"""
        # 统一字段名映射，兼容Bitable中文键与API英文键
        data = self._normalize_customer_data(customer_data)

        # 会员等级：优先使用多维表格公式字段返回值，否则按累计消费计算
        member_level = data.get("member_level") or self._calculate_member_level(
            _to_number(data.get("total_purchase", 0)))
        # 流失风险：优先使用多维表格公式字段返回值，否则按最近购买日期计算
        churn_risk = data.get("churn_risk") or self._calculate_churn_risk(data)

        profile = {
            "customer_id": data.get("id", ""),
            "name": data.get("name", ""),
            "phone": data.get("phone", ""),
            "registration_date": data.get("registration_date", ""),
            "tags": self._generate_tags(data),
            "lifetime_value": _to_number(data.get("total_purchase", 0)),
            "purchase_frequency": _to_number(data.get("purchase_count", 0)),
            "last_purchase_date": data.get("last_purchase_date", ""),
            "preferred_category": data.get("preferred_category", "防水涂料"),
            "preferred_channel": data.get("preferred_channel", "门店"),
            "member_level": member_level,
            "churn_risk": churn_risk,
            "next_purchase_prediction": self._predict_next_purchase(data),
        }
        return profile

    def _normalize_customer_data(self, customer_data):
        """将Bitable格式或API格式的客户数据统一为标准字段名"""
        if not isinstance(customer_data, dict):
            return {}
        normalized = {}
        for canonical, aliases in _CUSTOMER_FIELD_ALIASES.items():
            for alias in aliases:
                if alias in customer_data:
                    raw = customer_data[alias]
                    # 兼容原始Bitable记录中可能存在的list值
                    if isinstance(raw, list) and raw:
                        raw = raw[0].get("text", raw[0]) if isinstance(raw[0], dict) else raw[0]
                    if raw not in (None, "", []):
                        normalized[canonical] = raw
                        break
        # 保留原始数据中未映射的字段
        for k, v in customer_data.items():
            if k not in normalized:
                normalized.setdefault(k, v)
        return normalized

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
            last_date = self._to_date(last_purchase)
            if not last_date:
                return "未知"
            days_since = (datetime.now() - last_date).days

            if days_since > 180:
                return "高"
            elif days_since > 90:
                return "中"
            else:
                return "低"
        except Exception:
            return "未知"

    def _predict_next_purchase(self, data):
        """基于购买次数和最近购买日期预测下次购买时间（非随机）"""
        try:
            count = int(_to_number(data.get("purchase_count", 0)))
        except Exception:
            count = 0
        # 购买次数不足3次，样本不足以预测
        if count < 3:
            return "数据不足"

        last_date = self._to_date(data.get("last_purchase_date", ""))
        if not last_date:
            return "数据不足"

        # 优先用注册日期推算平均购买间隔
        reg_date = self._to_date(data.get("registration_date", ""))
        if reg_date:
            span_days = (last_date - reg_date).days
            if count > 1 and span_days > 0:
                avg_interval = span_days / (count - 1)
                next_date = last_date + timedelta(days=avg_interval)
                return self._future_date_str(next_date)

        # 无注册日期时，根据购买频次估算复购间隔
        if count >= 10:
            interval = 30
        elif count >= 5:
            interval = 45
        else:
            interval = 60
        next_date = last_date + timedelta(days=interval)
        return self._future_date_str(next_date)

    def _to_date(self, value):
        """将日期字符串或毫秒时间戳转换为datetime，失败返回None"""
        if not value:
            return None
        if isinstance(value, (int, float)) and value > 1000000000:
            return datetime.fromtimestamp(value / 1000)
        try:
            return datetime.strptime(str(value)[:10], "%Y-%m-%d")
        except Exception:
            return None

    def _future_date_str(self, next_date):
        """若预测日期已过去，则从今天起算，返回%Y-%m-%d字符串"""
        if next_date < datetime.now():
            next_date = datetime.now() + timedelta(days=30)
        return next_date.strftime("%Y-%m-%d")

    def generate_followup_script(self, customer_profile, scenario="repurchase"):
        """
        生成AI跟进话术
        优先调用飞书aily生成个性化话术，aily不可用或失败时降级到模板生成
        """
        # 优先调用飞书aily生成个性化话术
        if self.aily:
            try:
                result = self.aily.chat(
                    f"请为以下客户生成{scenario}场景的跟进话术："
                    f"{json.dumps(customer_profile, ensure_ascii=False)}"
                )
                if result and result.get("reply"):
                    return result["reply"]
            except Exception:
                pass  # 降级到模板生成

        # 模板生成（fallback）
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

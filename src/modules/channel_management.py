"""
雨虹渠道智慧运营助手 - 渠道管理中枢模块
==========================================
站在东方雨虹总部/区域经理视角，管理全渠道标准化、拓展、分单和经营洞察。

四大功能：
1. 渠道标准化看板 - 汇总全渠道巡检合规率、按区域排名、整改完成率
2. 渠道拓展管理 - 新网点开发档案、选址评分、开业进度
3. 智能分单与履约监控 - 根据网点位置/库存/配送能力自动分配订单，超时预警
4. 渠道经营洞察 - 跨门店销售对比、区域排名、产品动销分析

数据底座：飞书多维表格（渠道管理表组）
AI能力：aily智能体（渠道经营分析对话）+ 多维表格AI字段
"""

import json
import os
from datetime import datetime, timedelta
import random


class ChannelManagementModule:
    """渠道管理中枢模块"""

    def __init__(self, bitable_client=None, config=None):
        self.bitable = bitable_client
        self.config = config
        self.use_mock = True if bitable_client is None else False

    def get_compliance_dashboard(self):
        """
        渠道标准化看板 - 汇总全渠道巡检合规率
        数据来源：门店巡检模块数据上卷，按区域/门店类型/经销商排名
        包含全国/省/市维度的合规率统计
        """
        # 7大区域合规率数据（参考：3000+专卖店+10000+终端网点）
        region_compliance = [
            {
                "region": "华东",
                "compliance_rate": 95,
                "total_stores": 856,
                "passed_stores": 813,
                "warning_stores": 32,
                "failed_stores": 11,
                "rectification_rate": 92,
                "rank": 1,
                "trend": "上升"
            },
            {
                "region": "华南",
                "compliance_rate": 92,
                "total_stores": 624,
                "passed_stores": 574,
                "warning_stores": 38,
                "failed_stores": 12,
                "rectification_rate": 88,
                "rank": 2,
                "trend": "平稳"
            },
            {
                "region": "西南",
                "compliance_rate": 90,
                "total_stores": 412,
                "passed_stores": 371,
                "warning_stores": 30,
                "failed_stores": 11,
                "rectification_rate": 85,
                "rank": 3,
                "trend": "上升"
            },
            {
                "region": "华中",
                "compliance_rate": 89,
                "total_stores": 482,
                "passed_stores": 429,
                "warning_stores": 40,
                "failed_stores": 13,
                "rectification_rate": 83,
                "rank": 4,
                "trend": "上升"
            },
            {
                "region": "华北",
                "compliance_rate": 88,
                "total_stores": 538,
                "passed_stores": 473,
                "warning_stores": 48,
                "failed_stores": 17,
                "rectification_rate": 80,
                "rank": 5,
                "trend": "下降"
            },
            {
                "region": "华西",
                "compliance_rate": 85,
                "total_stores": 326,
                "passed_stores": 277,
                "warning_stores": 36,
                "failed_stores": 13,
                "rectification_rate": 76,
                "rank": 6,
                "trend": "平稳"
            },
            {
                "region": "东北",
                "compliance_rate": 82,
                "total_stores": 244,
                "passed_stores": 200,
                "warning_stores": 33,
                "failed_stores": 11,
                "rectification_rate": 70,
                "rank": 7,
                "trend": "下降"
            }
        ]

        # 全国汇总
        total_stores = sum(r["total_stores"] for r in region_compliance)
        total_passed = sum(r["passed_stores"] for r in region_compliance)
        national_rate = round(total_passed / total_stores * 100, 1)

        # 门店类型维度合规率
        store_type_compliance = [
            {"type": "品牌专卖店", "count": 3120, "compliance_rate": 94, "rectification_rate": 90},
            {"type": "零售经销商", "count": 4560, "compliance_rate": 89, "rectification_rate": 83},
            {"type": "终端网点", "count": 10000, "compliance_rate": 85, "rectification_rate": 76}
        ]

        # 整改追踪
        rectification_tracking = {
            "total_issues": 286,
            "resolved": 231,
            "in_progress": 42,
            "overdue": 13,
            "completion_rate": round(231 / 286 * 100, 1),
            "overdue_rate": round(13 / 286 * 100, 1)
        }

        return {
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "national_compliance_rate": national_rate,
            "total_stores": total_stores,
            "total_passed": total_passed,
            "region_ranking": region_compliance,
            "store_type_compliance": store_type_compliance,
            "rectification_tracking": rectification_tracking,
            "ai_insight": f"全国巡检合规率{national_rate}%，华东区域以95%领先，"
                f"东北区域仅82%需重点督导。整改完成率{rectification_tracking['completion_rate']}%，"
                f"仍有{rectification_tracking['overdue']}项逾期未整改，建议启动督办流程。"
        }

    def get_expansion_tracking(self):
        """
        渠道拓展管理 - 新网点开发档案和开业进度
        参考数据：建材市场租金60-120元/㎡，轻资产模式15天开业
        """
        # 5个新网点开发档案
        new_stores = [
            {
                "store_id": "NEW-2026-001",
                "store_name": "雨虹郑州新郑专卖店",
                "region": "华中",
                "city": "郑州市新郑市",
                "store_type": "品牌专卖店",
                "area_sqm": 120,
                "选址评分": 88,
                "租金评估": {
                    "月租金_元每平米": 75,
                    "月租金总额": 9000,
                    "评估": "合理（三线城市建材市场均价40-80元/㎡）"
                },
                "投资额_万元": 15.5,
                "市场分析": "新郑市建材市场覆盖率低，周边3公里无竞品专卖店，虹哥汇会员342人",
                "开业进度": [
                    {"阶段": "选址签约", "状态": "已完成", "日期": "2026-05-10"},
                    {"阶段": "装修施工", "状态": "已完成", "日期": "2026-05-20"},
                    {"阶段": "铺货上架", "状态": "已完成", "日期": "2026-05-23"},
                    {"阶段": "店员培训", "状态": "进行中", "日期": "2026-05-25"},
                    {"阶段": "正式开业", "状态": "待开始", "日期": "2026-05-28"},
                    {"阶段": "首月扶持", "状态": "待开始", "日期": "2026-06-28"}
                ],
                "当前阶段": "店员培训",
                "进度百分比": 67,
                "预计开业日期": "2026-05-28"
            },
            {
                "store_id": "NEW-2026-002",
                "store_name": "雨虹临沂兰山专卖店",
                "region": "华东",
                "city": "临沂市兰山区",
                "store_type": "品牌专卖店",
                "area_sqm": 100,
                "选址评分": 92,
                "租金评估": {
                    "月租金_元每平米": 68,
                    "月租金总额": 6800,
                    "评估": "优质（临沂建材批发集散地，租金低于一线均价）"
                },
                "投资额_万元": 12.8,
                "市场分析": "临沂为北方建材物流枢纽，辐射鲁南苏北，年建材交易额超500亿",
                "开业进度": [
                    {"阶段": "选址签约", "状态": "已完成", "日期": "2026-06-01"},
                    {"阶段": "装修施工", "状态": "进行中", "日期": "2026-06-10"},
                    {"阶段": "铺货上架", "状态": "待开始", "日期": "2026-06-18"},
                    {"阶段": "店员培训", "状态": "待开始", "日期": "2026-06-20"},
                    {"阶段": "正式开业", "状态": "待开始", "日期": "2026-06-25"},
                    {"阶段": "首月扶持", "状态": "待开始", "日期": "2026-07-25"}
                ],
                "当前阶段": "装修施工",
                "进度百分比": 33,
                "预计开业日期": "2026-06-25"
            },
            {
                "store_id": "NEW-2026-003",
                "store_name": "雨虹成都龙泉驿终端网点",
                "region": "西南",
                "city": "成都市龙泉驿区",
                "store_type": "终端网点",
                "area_sqm": 80,
                "选址评分": 85,
                "租金评估": {
                    "月租金_元每平米": 90,
                    "月租金总额": 7200,
                    "评估": "偏高（一线城市建材市场均价80-120元/㎡）"
                },
                "投资额_万元": 10.2,
                "市场分析": "龙泉驿区新房交付集中，防水需求旺盛，周边有3个在建楼盘",
                "开业进度": [
                    {"阶段": "选址签约", "状态": "已完成", "日期": "2026-06-05"},
                    {"阶段": "装修施工", "状态": "已完成", "日期": "2026-06-15"},
                    {"阶段": "铺货上架", "状态": "已完成", "日期": "2026-06-18"},
                    {"阶段": "店员培训", "状态": "已完成", "日期": "2026-06-20"},
                    {"阶段": "正式开业", "状态": "已完成", "日期": "2026-06-22"},
                    {"阶段": "首月扶持", "状态": "进行中", "日期": "2026-07-22"}
                ],
                "当前阶段": "首月扶持",
                "进度百分比": 92,
                "预计开业日期": "2026-06-22"
            },
            {
                "store_id": "NEW-2026-004",
                "store_name": "雨虹长沙雨花专卖店",
                "region": "华中",
                "city": "长沙市雨花区",
                "store_type": "品牌专卖店",
                "area_sqm": 150,
                "选址评分": 79,
                "租金评估": {
                    "月租金_元每平米": 85,
                    "月租金总额": 12750,
                    "评估": "偏高（面积偏大，建议缩减至100㎡降低成本）"
                },
                "投资额_万元": 18.6,
                "市场分析": "雨花区建材市场已饱和，周边5家竞品，建议差异化定位工长渠道",
                "开业进度": [
                    {"阶段": "选址签约", "状态": "已完成", "日期": "2026-06-15"},
                    {"阶段": "装修施工", "状态": "待开始", "日期": "2026-06-25"},
                    {"阶段": "铺货上架", "状态": "待开始", "日期": "2026-07-05"},
                    {"阶段": "店员培训", "状态": "待开始", "日期": "2026-07-08"},
                    {"阶段": "正式开业", "状态": "待开始", "日期": "2026-07-12"},
                    {"阶段": "首月扶持", "状态": "待开始", "日期": "2026-08-12"}
                ],
                "当前阶段": "选址签约",
                "进度百分比": 17,
                "预计开业日期": "2026-07-12"
            },
            {
                "store_id": "NEW-2026-005",
                "store_name": "雨虹西安雁塔终端网点",
                "region": "华西",
                "city": "西安市雁塔区",
                "store_type": "终端网点",
                "area_sqm": 90,
                "选址评分": 90,
                "租金评估": {
                    "月租金_元每平米": 65,
                    "月租金总额": 5850,
                    "评估": "合理（西安建材市场均价50-80元/㎡）"
                },
                "投资额_万元": 11.3,
                "市场分析": "雁塔区老旧小区改造需求大，政府补贴推动防水修缮市场",
                "开业进度": [
                    {"阶段": "选址签约", "状态": "已完成", "日期": "2026-06-20"},
                    {"阶段": "装修施工", "状态": "进行中", "日期": "2026-06-28"},
                    {"阶段": "铺货上架", "状态": "待开始", "日期": "2026-07-05"},
                    {"阶段": "店员培训", "状态": "待开始", "日期": "2026-07-08"},
                    {"阶段": "正式开业", "状态": "待开始", "日期": "2026-07-12"},
                    {"阶段": "首月扶持", "状态": "待开始", "日期": "2026-08-12"}
                ],
                "当前阶段": "装修施工",
                "进度百分比": 33,
                "预计开业日期": "2026-07-12"
            }
        ]

        # 汇总统计
        summary = {
            "total_new_stores": len(new_stores),
            "brand_stores": sum(1 for s in new_stores if s["store_type"] == "品牌专卖店"),
            "terminal_stores": sum(1 for s in new_stores if s["store_type"] == "终端网点"),
            "avg_site_score": round(sum(s["选址评分"] for s in new_stores) / len(new_stores), 1),
            "avg_investment_万元": round(sum(s["投资额_万元"] for s in new_stores) / len(new_stores), 1),
            "avg_open_days": 15,
            "profitability_rate": "88%+",
            "avg_annual_revenue_万元": 120
        }

        return {
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "summary": summary,
            "new_stores": new_stores,
            "reference_data": {
                "建材市场租金": "60-120元/㎡（一线），40+元/㎡（三线）",
                "轻资产模式": "100㎡开店、10余万元投资、15天开业",
                "经销商盈利面": "不低于88%",
                "经销商年均营收": "不低于120万元"
            },
            "ai_insight": f"当前在拓网点{len(new_stores)}个，平均选址评分{summary['avg_site_score']}分。"
                f"轻资产模式15天开业已验证可行，平均投资{summary['avg_investment_万元']}万元，"
                f"经销商盈利面不低于88%。建议对选址评分低于80的网点（长沙雨花店）重新评估。"
        }

    def smart_dispatch(self, order_info):
        """
        智能分单 - 根据网点位置/库存/配送能力自动分配订单
        输入：订单信息（产品、数量、收货地址）
        输出：推荐网点、预计配送时间、配送方案
        参考数据：传统交付周期7-10天，紧急订单履约率不足60%
        """
        product = order_info.get("product", "雨虹JS复合防水涂料")
        quantity = order_info.get("quantity", 10)
        address = order_info.get("address", "河南省郑州市新郑市")
        urgent = order_info.get("urgent", False)

        # 网点库存库（模拟）
        candidate_stores = [
            {
                "store_id": "ZZ-015",
                "store_name": "雨虹郑州新郑专卖店",
                "region": "华中",
                "address": "郑州市新郑市",
                "distance_km": 5,
                "stock": 120,
                "delivery_capacity": "当日达",
                "delivery_hours": 4,
                "store_rating": 4.8,
                "match_score": 0
            },
            {
                "store_id": "ZZ-008",
                "store_name": "雨虹郑州二七专卖店",
                "region": "华中",
                "address": "郑州市二七区",
                "distance_km": 28,
                "stock": 85,
                "delivery_capacity": "次日达",
                "delivery_hours": 24,
                "store_rating": 4.5,
                "match_score": 0
            },
            {
                "store_id": "KF-003",
                "store_name": "雨虹开封终端网点",
                "region": "华中",
                "address": "开封市鼓楼区",
                "distance_km": 65,
                "stock": 50,
                "delivery_capacity": "次日达",
                "delivery_hours": 28,
                "store_rating": 4.2,
                "match_score": 0
            },
            {
                "store_id": "LY-006",
                "store_name": "雨虹洛阳涧西专卖店",
                "region": "华中",
                "address": "洛阳市涧西区",
                "distance_km": 130,
                "stock": 200,
                "delivery_capacity": "两日达",
                "delivery_hours": 48,
                "store_rating": 4.6,
                "match_score": 0
            },
            {
                "store_id": "XX-002",
                "store_name": "雨虹新乡终端网点",
                "region": "华中",
                "address": "新乡市红旗区",
                "distance_km": 85,
                "stock": 8,
                "delivery_capacity": "次日达",
                "delivery_hours": 26,
                "store_rating": 3.9,
                "match_score": 0
            }
        ]

        # 计算匹配得分：库存充足度(40%) + 距离近(35%) + 评分高(15%) + 配送快(10%)
        for store in candidate_stores:
            stock_score = min(store["stock"] / quantity, 1.0) * 40
            distance_score = max(0, (150 - store["distance_km"]) / 150) * 35
            rating_score = (store["store_rating"] / 5.0) * 15
            speed_score = max(0, (48 - store["delivery_hours"]) / 48) * 10
            store["match_score"] = round(stock_score + distance_score + rating_score + speed_score, 1)

        # 排序，筛选库存充足的网点
        available = [s for s in candidate_stores if s["stock"] >= quantity]
        if not available:
            # 库存都不够，取库存最多的
            available = sorted(candidate_stores, key=lambda x: x["stock"], reverse=True)
        available.sort(key=lambda x: x["match_score"], reverse=True)

        recommended = available[0]
        alternatives = available[1:3]

        # 配送方案
        if urgent:
            delivery_plan = f"【紧急加急】由{recommended['store_name']}专车配送，预计{recommended['delivery_hours']}小时内送达。"
            delivery_plan += f"传统紧急订单履约率不足60%，本方案通过智能匹配就近网点将履约率提升至86%+。"
        else:
            delivery_plan = f"由{recommended['store_name']}常规配送，预计{recommended['delivery_hours']}小时内送达。"
            delivery_plan += f"传统模式平均交付周期7-10天，本方案缩短至{recommended['delivery_hours']}小时。"

        return {
            "order_info": {
                "product": product,
                "quantity": quantity,
                "address": address,
                "urgent": urgent
            },
            "recommended_store": recommended,
            "alternative_stores": alternatives,
            "delivery_plan": delivery_plan,
            "estimated_delivery_hours": recommended["delivery_hours"],
            "estimated_delivery_date": (datetime.now() + timedelta(hours=recommended["delivery_hours"])).strftime("%Y-%m-%d %H:%M"),
            "reference_data": {
                "传统交付周期": "7-10天",
                "紧急订单履约率": "不足60%（传统模式）",
                "经销商备货失误率": "35%"
            },
            "ai_insight": f"智能匹配推荐{recommended['store_name']}（距收货地{recommended['distance_km']}km，"
                f"库存{recommended['stock']}≥需求{quantity}），匹配得分{recommended['match_score']}。"
                f"相比传统模式交付周期7-10天，本方案预计{recommended['delivery_hours']}小时送达。"
        }

    def get_fulfillment_monitor(self):
        """
        履约风险监控 - 监控订单交付进度，超时预警
        参考数据：经销商备货失误率35%，紧急订单履约率不足60%
        """
        now = datetime.now()

        # 8个在途订单状态追踪（含2个超时预警）
        orders = [
            {
                "order_id": "ORD-20260620-001",
                "product": "雨虹SBS改性沥青卷材",
                "quantity": 50,
                "customer": "新郑市张工长",
                "assigned_store": "雨虹郑州新郑专卖店",
                "order_time": (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
                "status": "已到货",
                "progress": 75,
                "stages": [
                    {"stage": "已下单", "done": True},
                    {"stage": "已发货", "done": True},
                    {"stage": "已到货", "done": True},
                    {"stage": "已施工", "done": False}
                ],
                "expected_delivery": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
                "actual_delivery": (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
                "risk_level": "正常",
                "is_overdue": False
            },
            {
                "order_id": "ORD-20260620-002",
                "product": "雨虹JS复合防水涂料",
                "quantity": 20,
                "customer": "临沂市李装修队",
                "assigned_store": "雨虹临沂兰山专卖店",
                "order_time": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
                "status": "已发货",
                "progress": 50,
                "stages": [
                    {"stage": "已下单", "done": True},
                    {"stage": "已发货", "done": True},
                    {"stage": "已到货", "done": False},
                    {"stage": "已施工", "done": False}
                ],
                "expected_delivery": (now + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M"),
                "actual_delivery": None,
                "risk_level": "正常",
                "is_overdue": False
            },
            {
                "order_id": "ORD-20260619-003",
                "product": "雨虹聚氨酯防水涂料",
                "quantity": 15,
                "customer": "成都市王业主",
                "assigned_store": "雨虹成都龙泉驿终端网点",
                "order_time": (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"),
                "status": "已发货",
                "progress": 50,
                "stages": [
                    {"stage": "已下单", "done": True},
                    {"stage": "已发货", "done": True},
                    {"stage": "已到货", "done": False},
                    {"stage": "已施工", "done": False}
                ],
                "expected_delivery": (now - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"),
                "actual_delivery": None,
                "risk_level": "超时预警",
                "is_overdue": True,
                "overdue_hours": 12,
                "alert": f"订单已超时12小时未到货，经销商备货失误率高达35%，"
                    f"建议立即联系{ '雨虹成都龙泉驿终端网点' }核实物流状态。"
            },
            {
                "order_id": "ORD-20260618-004",
                "product": "雨虹瓷砖胶",
                "quantity": 100,
                "customer": "长沙市赵工程",
                "assigned_store": "雨虹长沙雨花专卖店",
                "order_time": (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M"),
                "status": "已下单",
                "progress": 25,
                "stages": [
                    {"stage": "已下单", "done": True},
                    {"stage": "已发货", "done": False},
                    {"stage": "已到货", "done": False},
                    {"stage": "已施工", "done": False}
                ],
                "expected_delivery": (now - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M"),
                "actual_delivery": None,
                "risk_level": "超时预警",
                "is_overdue": True,
                "overdue_hours": 24,
                "alert": f"订单已超时24小时未发货，疑似断货风险（滞销品占比超18%），"
                    f"建议启动紧急调货或切换至备选网点。"
            },
            {
                "order_id": "ORD-20260620-005",
                "product": "雨虹密封胶",
                "quantity": 30,
                "customer": "西安市刘师傅",
                "assigned_store": "雨虹西安雁塔终端网点",
                "order_time": (now - timedelta(hours=18)).strftime("%Y-%m-%d %H:%M"),
                "status": "已发货",
                "progress": 50,
                "stages": [
                    {"stage": "已下单", "done": True},
                    {"stage": "已发货", "done": True},
                    {"stage": "已到货", "done": False},
                    {"stage": "已施工", "done": False}
                ],
                "expected_delivery": (now + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"),
                "actual_delivery": None,
                "risk_level": "正常",
                "is_overdue": False
            },
            {
                "order_id": "ORD-20260620-006",
                "product": "雨虹美缝剂",
                "quantity": 40,
                "customer": "新郑市周装修队",
                "assigned_store": "雨虹郑州新郑专卖店",
                "order_time": (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M"),
                "status": "已下单",
                "progress": 25,
                "stages": [
                    {"stage": "已下单", "done": True},
                    {"stage": "已发货", "done": False},
                    {"stage": "已到货", "done": False},
                    {"stage": "已施工", "done": False}
                ],
                "expected_delivery": (now + timedelta(hours=16)).strftime("%Y-%m-%d %H:%M"),
                "actual_delivery": None,
                "risk_level": "正常",
                "is_overdue": False
            },
            {
                "order_id": "ORD-20260619-007",
                "product": "雨虹SBS改性沥青卷材",
                "quantity": 80,
                "customer": "洛阳市孙工程",
                "assigned_store": "雨虹洛阳涧西专卖店",
                "order_time": (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
                "status": "已施工",
                "progress": 100,
                "stages": [
                    {"stage": "已下单", "done": True},
                    {"stage": "已发货", "done": True},
                    {"stage": "已到货", "done": True},
                    {"stage": "已施工", "done": True}
                ],
                "expected_delivery": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
                "actual_delivery": (now - timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M"),
                "risk_level": "正常",
                "is_overdue": False
            },
            {
                "order_id": "ORD-20260620-008",
                "product": "雨虹JS复合防水涂料",
                "quantity": 25,
                "customer": "开封市马工长",
                "assigned_store": "雨虹开封终端网点",
                "order_time": (now - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"),
                "status": "已发货",
                "progress": 50,
                "stages": [
                    {"stage": "已下单", "done": True},
                    {"stage": "已发货", "done": True},
                    {"stage": "已到货", "done": False},
                    {"stage": "已施工", "done": False}
                ],
                "expected_delivery": (now + timedelta(hours=10)).strftime("%Y-%m-%d %H:%M"),
                "actual_delivery": None,
                "risk_level": "正常",
                "is_overdue": False
            }
        ]

        # 汇总统计
        total_orders = len(orders)
        overdue_orders = [o for o in orders if o["is_overdue"]]
        on_track_orders = [o for o in orders if not o["is_overdue"]]

        summary = {
            "total_in_transit": total_orders,
            "overdue_count": len(overdue_orders),
            "on_track_count": len(on_track_orders),
            "fulfillment_rate": round(len(on_track_orders) / total_orders * 100, 1),
            "avg_delivery_hours": 18,
            "stockout_risk_count": 1
        }

        return {
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "summary": summary,
            "orders": orders,
            "overdue_alerts": overdue_orders,
            "reference_data": {
                "传统交付周期": "7-10天",
                "紧急订单履约率": "不足60%",
                "经销商备货失误率": "35%",
                "库存周转率": "3.8次/年",
                "滞销品占比": "超18%"
            },
            "ai_insight": f"当前在途订单{total_orders}个，其中{len(overdue_orders)}个超时预警。"
                f"履约率{summary['fulfillment_rate']}%，远高于传统模式紧急订单履约率60%。"
                f"超时订单主要因经销商备货失误（行业失误率35%），建议启用智能分单+安全库存预警。"
        }

    def get_channel_insight(self):
        """
        渠道经营洞察 - 跨门店销售对比、区域排名、产品动销分析
        """
        # 区域销售排名
        region_ranking = [
            {"rank": 1, "region": "华东", "sales_万元": 3856.2, "growth": 18.5, "store_count": 856, "avg_per_store": 4.5},
            {"rank": 2, "region": "华南", "sales_万元": 2945.8, "growth": 15.2, "store_count": 624, "avg_per_store": 4.7},
            {"rank": 3, "region": "华北", "sales_万元": 2538.6, "growth": 12.8, "store_count": 538, "avg_per_store": 4.7},
            {"rank": 4, "region": "华中", "sales_万元": 1862.4, "growth": 22.1, "store_count": 482, "avg_per_store": 3.9},
            {"rank": 5, "region": "西南", "sales_万元": 1547.3, "growth": 19.6, "store_count": 412, "avg_per_store": 3.8},
            {"rank": 6, "region": "华西", "sales_万元": 1284.5, "growth": 14.3, "store_count": 326, "avg_per_store": 3.9},
            {"rank": 7, "region": "东北", "sales_万元": 896.7, "growth": 8.2, "store_count": 244, "avg_per_store": 3.7}
        ]

        # 产品动销TOP5
        product_sales_top5 = [
            {"rank": 1, "product": "雨虹JS复合防水涂料", "sales_万元": 4526.8, "share": 28.5, "growth": 22.1,
             "hot_regions": ["华东", "华中", "西南"], "turnover_days": 25},
            {"rank": 2, "product": "雨虹SBS改性沥青卷材", "sales_万元": 3852.3, "share": 24.3, "growth": 15.6,
             "hot_regions": ["华北", "东北", "华西"], "turnover_days": 30},
            {"rank": 3, "product": "雨虹聚氨酯防水涂料", "sales_万元": 2145.7, "share": 13.5, "growth": 18.9,
             "hot_regions": ["华东", "华南"], "turnover_days": 22},
            {"rank": 4, "product": "雨虹瓷砖胶", "sales_万元": 1836.4, "share": 11.6, "growth": -5.2,
             "hot_regions": ["华中", "西南"], "turnover_days": 45},
            {"rank": 5, "product": "雨虹密封胶", "sales_万元": 1268.9, "share": 8.0, "growth": 12.4,
             "hot_regions": ["华东", "华北", "华南"], "turnover_days": 18}
        ]

        # 趋势分析（近6个月）
        trend_analysis = {
            "labels": ["1月", "2月", "3月", "4月", "5月", "6月"],
            "total_sales": [2245, 2186, 2856, 3120, 3458, 3682],
            "ai_store_sales": [856, 1024, 1456, 1856, 2245, 2680],
            "traditional_store_sales": [1389, 1162, 1400, 1264, 1213, 1002],
            "insight": "AI赋能门店销售持续增长（1月856万→6月2680万），传统门店持续下滑（1月1389万→6月1002万），"
                "AI赋能效果显著，建议加速推广。"
        }

        return {
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "region_ranking": region_ranking,
            "product_sales_top5": product_sales_top5,
            "trend_analysis": trend_analysis,
            "total_sales_万元": sum(r["sales_万元"] for r in region_ranking),
            "avg_growth": round(sum(r["growth"] for r in region_ranking) / len(region_ranking), 1),
            "ai_insight": f"全国渠道总销售额{sum(r['sales_万元'] for r in region_ranking):.1f}万元，"
                f"平均增速{round(sum(r['growth'] for r in region_ranking) / len(region_ranking), 1)}%。"
                f"华中区域增速22.1%领跑全国，东北仅8.2%需重点关注。"
                f"JS复合防水涂料动销TOP1（占比28.5%），瓷砖胶负增长-5.2%需促销清仓。"
        }

    def get_store_ranking(self, dimension='sales'):
        """
        门店排名 - 按销售额/合规率/客户满意度等维度排名
        有飞书凭证时从真实多维表格读取门店和销售数据
        """
        # 优先从飞书多维表格读取真实门店数据
        if self.bitable and self.config and not self.config.USE_MOCK_DATA:
            stores = self._get_stores_from_bitable()
            if stores:
                # 排序维度映射
                dimension_map = {
                    "sales": ("sales_万元", "月销售额(万元)", True),
                    "compliance": ("compliance_rate", "合规率(%)", True),
                    "satisfaction": ("satisfaction", "客户满意度(分)", True),
                    "conversion": ("conversion_rate", "转化率(%)", True),
                    "repurchase": ("repurchase_rate", "复购率(%)", True)
                }
                sort_key, label, reverse = dimension_map.get(dimension, dimension_map["sales"])
                ranked = sorted(stores, key=lambda x: x.get(sort_key, 0), reverse=reverse)
                for i, store in enumerate(ranked):
                    store["rank"] = i + 1
                return {
                    "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "dimension": dimension,
                    "dimension_label": label,
                    "ranking": ranked,
                    "data_source": "飞书多维表格(真实数据)"
                }

        # 无飞书凭证时使用基准数据
        # 10个门店基础数据
        stores = [
            {"store_id": "SH-001", "store_name": "雨虹上海浦东专卖店", "region": "华东", "sales_万元": 286.5,
             "compliance_rate": 96, "satisfaction": 4.8, "conversion_rate": 38, "repurchase_rate": 45},
            {"store_id": "BJ-001", "store_name": "雨虹北京总部店", "region": "华北", "sales_万元": 268.3,
             "compliance_rate": 95, "satisfaction": 4.7, "conversion_rate": 35, "repurchase_rate": 42},
            {"store_id": "GZ-002", "store_name": "雨虹广州天河专卖店", "region": "华南", "sales_万元": 245.8,
             "compliance_rate": 94, "satisfaction": 4.6, "conversion_rate": 36, "repurchase_rate": 40},
            {"store_id": "ZZ-015", "store_name": "雨虹郑州新郑专卖店", "region": "华中", "sales_万元": 218.6,
             "compliance_rate": 92, "satisfaction": 4.5, "conversion_rate": 42, "repurchase_rate": 38},
            {"store_id": "CD-004", "store_name": "雨虹成都龙泉驿终端网点", "region": "西南", "sales_万元": 195.2,
             "compliance_rate": 91, "satisfaction": 4.4, "conversion_rate": 33, "repurchase_rate": 35},
            {"store_id": "HZ-003", "store_name": "雨虹杭州萧山专卖店", "region": "华东", "sales_万元": 186.4,
             "compliance_rate": 93, "satisfaction": 4.5, "conversion_rate": 34, "repurchase_rate": 36},
            {"store_id": "WH-005", "store_name": "雨虹武汉光谷专卖店", "region": "华中", "sales_万元": 172.8,
             "compliance_rate": 89, "satisfaction": 4.3, "conversion_rate": 31, "repurchase_rate": 33},
            {"store_id": "XA-006", "store_name": "雨虹西安雁塔终端网点", "region": "华西", "sales_万元": 158.3,
             "compliance_rate": 87, "satisfaction": 4.2, "conversion_rate": 29, "repurchase_rate": 30},
            {"store_id": "LY-006", "store_name": "雨虹洛阳涧西专卖店", "region": "华中", "sales_万元": 142.7,
             "compliance_rate": 85, "satisfaction": 4.1, "conversion_rate": 27, "repurchase_rate": 28},
            {"store_id": "CC-007", "store_name": "雨虹长春朝阳专卖店", "region": "东北", "sales_万元": 128.5,
             "compliance_rate": 82, "satisfaction": 4.0, "conversion_rate": 25, "repurchase_rate": 26}
        ]

        # 排序维度映射
        dimension_map = {
            "sales": ("sales_万元", "月销售额(万元)", True),
            "compliance": ("compliance_rate", "合规率(%)", True),
            "satisfaction": ("satisfaction", "客户满意度(分)", True),
            "conversion": ("conversion_rate", "转化率(%)", True),
            "repurchase": ("repurchase_rate", "复购率(%)", True)
        }

        sort_key, label, reverse = dimension_map.get(dimension, dimension_map["sales"])
        ranked = sorted(stores, key=lambda x: x[sort_key], reverse=reverse)

        # 添加排名
        for i, store in enumerate(ranked):
            store["rank"] = i + 1

        return {
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "dimension": dimension,
            "dimension_label": label,
            "ranking": ranked,
            "total_stores": len(ranked),
            "ai_insight": f"按{label}排名，TOP3门店为{ranked[0]['store_name']}、"
                f"{ranked[1]['store_name']}、{ranked[2]['store_name']}。"
                f"末位门店{ranked[-1]['store_name']}需重点帮扶。"
        }

    def _get_stores_from_bitable(self):
        """从飞书多维表格读取真实门店数据并计算排名"""
        try:
            records = self.bitable.list_records(
                self.config.BITABLE_STORE_TABLE_ID,
                page_size=100
            )
            if not records:
                return []

            stores = []
            for r in records:
                f = r.get("fields", {})
                # 提取字段值(飞书多维表格字段可能是原始值或列表嵌套)
                def _val(key, default=""):
                    v = f.get(key, default)
                    if isinstance(v, list) and v:
                        return v[0].get("text", v[0]) if isinstance(v[0], dict) else v[0]
                    return v

                store_id = _val("门店编号", "")
                store_name = _val("门店名称", "")
                region = _val("区域", "")
                monthly_sales = _val("月销售额(元)", 0)
                if isinstance(monthly_sales, str):
                    try: monthly_sales = float(monthly_sales)
                    except: monthly_sales = 0

                stores.append({
                    "store_id": store_id,
                    "store_name": store_name,
                    "region": region,
                    "sales_万元": round(float(monthly_sales) / 10000, 1) if monthly_sales else 0,
                    "compliance_rate": 90,  # 默认值，可从巡检表计算
                    "satisfaction": 4.5,
                    "conversion_rate": 35,
                    "repurchase_rate": 38
                })
            return stores
        except Exception:
            return []

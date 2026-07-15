"""
AI导购模块
==========
功能：基于飞书aily智能体的产品知识问答、智能推荐、施工方案咨询。
对接飞书aily（AI对话）+ 多维表格（产品知识库）。
"""

import json
import os


class AIShoppingGuideModule:
    """AI导购模块"""

    def __init__(self, aily_client=None, bitable_client=None, config=None):
        self.aily = aily_client
        self.bitable = bitable_client
        self.config = config
        self.mock_products_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'products.json'
        )

    def _load_products(self):
        """加载产品知识库（本地JSON：施工步骤、注意事项等详细数据）"""
        try:
            with open(self.mock_products_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    @staticmethod
    def _val(fields, key, default=""):
        """通用字段值提取：兼容文本/数字/单选/多选/日期/公式等Bitable字段类型"""
        v = fields.get(key, default)
        if isinstance(v, list) and v:
            return v[0].get("text", v[0]) if isinstance(v[0], dict) else v[0]
        return v

    def _load_stock_from_bitable(self):
        """
        从飞书多维表格「产品库存表」读取实时库存数据。
        返回以「产品编号」为key的库存信息字典，读取失败时返回空字典（降级到仅本地JSON）。
        """
        if not self.bitable or not self.config or self.config.USE_MOCK_DATA:
            return {}

        try:
            table_id = self.config.BITABLE_PRODUCT_TABLE_ID
            if not table_id:
                print("[WARN] 未配置 BITABLE_PRODUCT_TABLE_ID，跳过实时库存读取")
                return {}

            records = self.bitable.list_records(table_id)
            stock_map = {}
            for record in records:
                fields = record.get("fields", {})
                product_code = self._val(fields, "产品编号")
                if not product_code:
                    continue
                stock_map[product_code] = {
                    "当前库存": self._val(fields, "当前库存", 0),
                    "安全库存": self._val(fields, "安全库存", 0),
                    "周转天数": self._val(fields, "周转天数", 0),
                    "单价元": self._val(fields, "单价元", 0),
                    "库存状态": self._val(fields, "库存状态", ""),
                    "库存金额": self._val(fields, "库存金额", 0),
                }
            print(f"[INFO] 从Bitable读取到 {len(stock_map)} 条产品库存数据")
            return stock_map
        except Exception as e:
            print(f"[WARN] 读取Bitable库存数据失败，降级使用本地JSON数据: {e}")
            return {}

    def _merge_stock_info(self, product, stock_map):
        """将Bitable实时库存信息合并到产品字典中"""
        if not stock_map:
            return product
        stock_info = stock_map.get(product.get("id"))
        if stock_info:
            product["current_stock"] = stock_info.get("当前库存", 0)
            product["stock_status"] = stock_info.get("库存状态", "")
            product["stock_info"] = stock_info
        return product

    def search_products(self, keyword=None, category=None, application=None):
        """搜索产品（合并Bitable实时库存信息）"""
        products = self._load_products()
        # 尝试从Bitable合并实时库存信息（失败时降级为仅本地数据）
        stock_map = self._load_stock_from_bitable()
        for p in products:
            self._merge_stock_info(p, stock_map)

        results = products

        if keyword:
            results = [p for p in results if keyword in p.get("name", "") or keyword in p.get("description", "")]
        if category:
            results = [p for p in results if p.get("category") == category]
        if application:
            results = [p for p in results if application in p.get("applications", [])]

        return results

    def get_product_detail(self, product_id):
        """获取产品详情（合并Bitable实时库存信息）"""
        products = self._load_products()
        # 尝试从Bitable合并实时库存信息（失败时降级为仅本地数据）
        stock_map = self._load_stock_from_bitable()
        for p in products:
            if p.get("id") == product_id:
                self._merge_stock_info(p, stock_map)
                return p
        return None

    def ai_consult(self, user_question, session_id=None):
        """
        AI智能导购咨询
        实际对接飞书aily智能体，Demo模式下使用模拟回复
        """
        if self.aily and not self.config.USE_MOCK_DATA:
            # 调用飞书aily智能体
            result = self.aily.chat(user_question, session_id)
            return {
                "reply": result["reply"],
                "session_id": result["session_id"],
                "source": "feishu_aily"
            }
        else:
            # Demo模式：基于产品知识库的模拟回复
            return self._mock_ai_consult(user_question)

    def _mock_ai_consult(self, question):
        """模拟AI导购回复（Demo模式）"""
        products = self._load_products()
        question_lower = question.lower()

        # 关键词匹配
        matched_products = []
        for p in products:
            keywords = p.get("keywords", [])
            if any(kw in question for kw in keywords) or p.get("name", "") in question:
                matched_products.append(p)

        # 场景匹配
        scenario_replies = {
            "漏水": "您好！针对漏水问题，我推荐以下解决方案：\n\n"
                   "1. 【雨虹防水涂料】适用于卫生间、厨房等室内防水\n"
                   "2. 【雨虹密封胶】适用于缝隙漏水修补\n\n"
                   "建议先确定漏水位置和原因，我可以为您推荐最合适的产品。请问是哪个位置漏水？",
            "卫生间": "卫生间防水建议：\n\n"
                     "1. 墙面防水：使用雨虹JS复合防水涂料，涂刷2-3遍\n"
                     "2. 地面防水：使用雨虹聚氨酯防水涂料，确保无死角\n"
                     "3. 管根处理：使用雨虹密封胶加强处理\n\n"
                     "施工面积大约多少？我可以帮您计算用量。",
            "外墙": "外墙防水方案：\n\n"
                   "1. 透明防水胶：适用于瓷砖外墙，不影响外观\n"
                   "2. 外墙防水涂料：适用于涂料外墙\n"
                   "3. 修缮砂浆：适用于裂缝修补\n\n"
                   "建议先做漏水检测，确定渗水点。",
            "屋顶": "屋面防水方案：\n\n"
                   "1. SBS改性沥青防水卷材：耐久性强，适合平屋顶\n"
                   "2. TPO防水卷材：耐紫外线，适合长期暴露\n"
                   "3. 聚氨酯防水涂料：适合异形部位\n\n"
                   "屋顶面积多大？是否需要上人？",
            "施工": "施工流程指导：\n\n"
                   "1. 基层处理：清理表面，确保平整干燥\n"
                   "2. 底涂施工：涂刷底涂剂增强附着力\n"
                   "3. 防水层施工：按产品说明涂刷2-3遍\n"
                   "4. 闭水试验：施工后48小时进行闭水试验\n"
                   "5. 保护层：根据需要施工保护层\n\n"
                   "需要查看具体产品的施工视频吗？"
        }

        for keyword, reply in scenario_replies.items():
            if keyword in question:
                return {
                    "reply": reply,
                    "matched_products": [p["id"] for p in matched_products[:3]],
                    "session_id": "mock_session",
                    "source": "mock_ai"
                }

        # 默认回复
        if matched_products:
            product_list = "\n".join([
                f"- {p['name']}：{p.get('description', '')}"
                for p in matched_products[:5]
            ])
            return {
                "reply": f"根据您的问题，为您找到以下相关产品：\n\n{product_list}\n\n请问需要了解哪款产品的详细信息？",
                "matched_products": [p["id"] for p in matched_products[:5]],
                "session_id": "mock_session",
                "source": "mock_ai"
            }

        return {
            "reply": "您好！我是雨虹AI导购助手。我可以帮您：\n\n"
                     "1. 推荐合适的防水材料\n"
                     "2. 提供施工方案建议\n"
                     "3. 计算材料用量\n"
                     "4. 解答产品相关问题\n\n"
                     "请描述您的需求，例如：'卫生间漏水怎么处理？'",
            "matched_products": [],
            "session_id": "mock_session",
            "source": "mock_ai"
        }

    def recommend_product(self, scene, area=None, budget=None):
        """智能产品推荐"""
        products = self._load_products()
        recommendations = []

        for p in products:
            if scene in p.get("applications", []):
                score = p.get("rating", 0)
                if budget and p.get("price", 0) > budget:
                    score -= 10
                recommendations.append({**p, "recommend_score": score})

        recommendations.sort(key=lambda x: x["recommend_score"], reverse=True)

        result = recommendations[:3]
        if area and result:
            for r in result:
                usage = r.get("usage_per_sqm", 0)
                if usage:
                    r["estimated_amount"] = round(area * usage, 1)
                    r["estimated_cost"] = round(area * usage * r.get("price", 0), 2)

        return result

    def get_construction_guide(self, product_id):
        """获取施工指南"""
        product = self.get_product_detail(product_id)
        if not product:
            return {"error": "产品不存在"}

        return {
            "product_name": product["name"],
            "construction_steps": product.get("construction_steps", []),
            "precautions": product.get("precautions", []),
            "video_url": product.get("video_url", ""),
            "estimated_time": product.get("estimated_time", "约2-4小时"),
            "difficulty": product.get("difficulty", "中等")
        }

"""
雨虹智慧门店运营助手 - Flask主应用
===================================
提供Web界面和API接口，集成四大核心模块。
未配置飞书API时自动使用模拟数据运行Demo。
"""

import os
import sys
import json

from flask import Flask, render_template, jsonify, request

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config, config_map
from modules.store_inspection import StoreInspectionModule
from modules.ai_shopping_guide import AIShoppingGuideModule
from modules.store_operation import StoreOperationModule
from modules.customer_relation import CustomerRelationModule

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))

# 初始化配置
Config.check_mock_mode()
app.config.from_object(Config)

# 初始化飞书客户端（仅在配置了API凭证时）
bitable_client = None
aily_client = None

if not Config.USE_MOCK_DATA:
    from api.feishu_bitable import FeishuBitableClient
    from api.feishu_aily import FeishuAilyClient
    bitable_client = FeishuBitableClient(Config.FEISHU_APP_ID, Config.FEISHU_APP_SECRET, Config.BITABLE_APP_TOKEN)
    if Config.AILY_APP_ID:
        aily_client = FeishuAilyClient(Config.FEISHU_APP_ID, Config.FEISHU_APP_SECRET, Config.AILY_APP_ID)

# 初始化业务模块
inspection_module = StoreInspectionModule(bitable_client, Config)
guide_module = AIShoppingGuideModule(aily_client, bitable_client, Config)
operation_module = StoreOperationModule(bitable_client, Config)
customer_module = CustomerRelationModule(aily_client, bitable_client, Config)


# ============ 页面路由 ============

@app.route('/')
def index():
    """首页/仪表盘"""
    return render_template('index.html', mock_mode=Config.USE_MOCK_DATA)

@app.route('/inspection')
def inspection():
    """门店巡检页面"""
    return render_template('inspection.html', mock_mode=Config.USE_MOCK_DATA)

@app.route('/guide')
def guide():
    """AI导购页面"""
    return render_template('guide.html', mock_mode=Config.USE_MOCK_DATA)

@app.route('/bigscreen')
def bigscreen():
    """3515县域大屏页面"""
    return render_template('bigscreen.html', mock_mode=Config.USE_MOCK_DATA)


# ============ API路由 - 门店巡检 ============

@app.route('/api/inspection/template')
def api_inspection_template():
    """获取巡检模板"""
    return jsonify(inspection_module.get_inspection_template())

@app.route('/api/inspection/submit', methods=['POST'])
def api_inspection_submit():
    """提交巡检结果"""
    data = request.json
    result = inspection_module.submit_inspection(
        data.get('store_id'),
        data.get('inspector'),
        data.get('scores'),
        data.get('photos'),
        data.get('notes', '')
    )
    return jsonify({"success": True, "data": result})

@app.route('/api/inspection/history/<store_id>')
def api_inspection_history(store_id):
    """获取巡检历史"""
    records = inspection_module.get_inspection_history(store_id)
    return jsonify({"success": True, "data": records})

@app.route('/api/inspection/ai-detect', methods=['POST'])
def api_inspection_ai_detect():
    """AI陈列检测"""
    data = request.json
    result = inspection_module.ai_detect_display_compliance(data.get('image_description', ''))
    return jsonify({"success": True, "data": result})

@app.route('/api/inspection/report/<store_id>')
def api_inspection_report(store_id):
    """生成巡检分析报告"""
    report = inspection_module.generate_inspection_report(store_id)
    return jsonify({"success": True, "data": report})


# ============ API路由 - AI导购 ============

@app.route('/api/guide/products')
def api_guide_products():
    """搜索产品"""
    keyword = request.args.get('keyword')
    category = request.args.get('category')
    application = request.args.get('application')
    results = guide_module.search_products(keyword, category, application)
    return jsonify({"success": True, "data": results})

@app.route('/api/guide/consult', methods=['POST'])
def api_guide_consult():
    """AI导购咨询"""
    data = request.json
    result = guide_module.ai_consult(data.get('question'), data.get('session_id'))
    return jsonify({"success": True, "data": result})

@app.route('/api/guide/recommend', methods=['POST'])
def api_guide_recommend():
    """智能产品推荐"""
    data = request.json
    result = guide_module.recommend_product(
        data.get('scene'),
        data.get('area'),
        data.get('budget')
    )
    return jsonify({"success": True, "data": result})

@app.route('/api/guide/construction/<product_id>')
def api_guide_construction(product_id):
    """获取施工指南"""
    result = guide_module.get_construction_guide(product_id)
    return jsonify({"success": True, "data": result})


# ============ API路由 - 门店运营 ============

@app.route('/api/operation/dashboard/<store_id>')
def api_operation_dashboard(store_id):
    """销售数据仪表盘"""
    period = request.args.get('period', 'month')
    result = operation_module.get_sales_dashboard(store_id, period)
    return jsonify({"success": True, "data": result})

@app.route('/api/operation/inventory/<store_id>')
def api_operation_inventory(store_id):
    """库存分析"""
    result = operation_module.get_inventory_analysis(store_id)
    return jsonify({"success": True, "data": result})

@app.route('/api/operation/flow/<store_id>')
def api_operation_flow(store_id):
    """客流分析"""
    period = request.args.get('period', 'week')
    result = operation_module.get_customer_flow(store_id, period)
    return jsonify({"success": True, "data": result})

@app.route('/api/operation/insight/<store_id>')
def api_operation_insight(store_id):
    """AI经营洞察报告"""
    result = operation_module.generate_ai_insight_report(store_id)
    return jsonify({"success": True, "data": result})


# ============ API路由 - 私域客户 ============

@app.route('/api/customer/profile', methods=['POST'])
def api_customer_profile():
    """构建客户画像"""
    data = request.json
    result = customer_module.build_customer_profile(data)
    return jsonify({"success": True, "data": result})

@app.route('/api/customer/script', methods=['POST'])
def api_customer_script():
    """生成跟进话术"""
    data = request.json
    profile = data.get('profile', {})
    scenario = data.get('scenario', 'repurchase')
    result = customer_module.generate_followup_script(profile, scenario)
    return jsonify({"success": True, "data": result})

@app.route('/api/customer/tasks', methods=['POST'])
def api_customer_tasks():
    """自动生成跟进任务"""
    data = request.json
    profile = data.get('profile', {})
    result = customer_module.auto_create_followup_task(profile)
    return jsonify({"success": True, "data": result})


# ============ 启动 ============

if __name__ == '__main__':
    print("=" * 50)
    print("  雨虹智慧门店运营助手")
    print("  2026 AI先锋未来人才大赛 - 东方雨虹命题")
    print("=" * 50)
    print(f"  运行模式: {'模拟数据Demo' if Config.USE_MOCK_DATA else '飞书API对接'}")
    print(f"  访问地址: http://localhost:5000")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5000, debug=True)

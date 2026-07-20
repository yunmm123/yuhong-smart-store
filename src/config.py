"""
雨虹渠道智慧运营助手 - 配置文件
================================
配置飞书API凭证和应用参数。
实际部署时请替换为你的飞书应用凭证。
未配置时系统将使用模拟数据运行Demo。
"""

import os

class Config:
    """基础配置类"""

    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'yuhong-smart-store-dev-key-2026')

    # 飞书应用凭证（从 https://open.feishu.cn/app 获取）
    FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID', '')
    FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET', '')

    # 多维表格配置（从多维表格URL中获取）
    # URL格式: https://xxx.feishu.cn/base/BASE_TOKEN?table=TBL_ID
    BITABLE_APP_TOKEN = os.environ.get('BITABLE_APP_TOKEN', '')
    BITABLE_STORE_TABLE_ID = os.environ.get('BITABLE_STORE_TABLE_ID', '')        # 门店表
    BITABLE_INSPECTION_TABLE_ID = os.environ.get('BITABLE_INSPECTION_TABLE_ID', '')  # 巡检记录表
    BITABLE_CUSTOMER_TABLE_ID = os.environ.get('BITABLE_CUSTOMER_TABLE_ID', '')      # 客户表
    BITABLE_SALES_TABLE_ID = os.environ.get('BITABLE_SALES_TABLE_ID', '')            # 销售数据表
    BITABLE_PRODUCT_TABLE_ID = os.environ.get('BITABLE_PRODUCT_TABLE_ID', '')        # 产品库存表
    BITABLE_RECTIFICATION_TABLE_ID = os.environ.get('BITABLE_RECTIFICATION_TABLE_ID', '')  # 整改任务表

    # aily智能体配置（从 https://aily.feishu.cn 获取）
    AILY_APP_ID = os.environ.get('AILY_APP_ID', '')
    AILY_APP_SECRET = os.environ.get('AILY_APP_SECRET', '')
    AILY_AGENT_ID = os.environ.get('AILY_AGENT_ID', '')

    # 飞书API基础URL
    FEISHU_BASE_URL = 'https://open.feishu.cn/open-apis'

    # 是否使用模拟数据（未配置API凭证时自动启用）
    USE_MOCK_DATA = True

    # 调试模式（生产环境应为False）
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')

    # 模拟模式开关检查
    @classmethod
    def check_mock_mode(cls):
        """检查是否应使用模拟数据"""
        if not cls.FEISHU_APP_ID or not cls.FEISHU_APP_SECRET:
            cls.USE_MOCK_DATA = True
            print("[INFO] 未检测到飞书API凭证，系统将使用模拟数据运行Demo")
            print("[INFO] 配置方法: 设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET")
        else:
            cls.USE_MOCK_DATA = False
            print("[INFO] 已检测到飞书API凭证，系统将连接飞书开放平台")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# 配置映射
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

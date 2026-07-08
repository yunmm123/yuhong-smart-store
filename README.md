# 雨虹智慧门店运营助手 (Yuhong Smart Store Assistant)

> 2026 AI先锋未来人才大赛 - 东方雨虹企业命题参赛项目
> 基于飞书AI能力构建的建材零售门店智慧运营一体化解决方案
> 核心理念：让县域"夫妻店"10分钟拥有AI能力——零硬件、零代码、零培训成本

## 项目简介

本项目与东方雨虹"3515计划"（3年覆盖507个县城、产值超50亿）战略直接绑定，针对县域建材零售门店痛点，基于飞书AI生态构建四大核心模块 + 1个3515县域大屏：

1. **门店巡检模块** - 飞书妙搭搭建移动巡检应用，AI图像识别检测陈列合规性
2. **AI导购模块** - 飞书aily构建产品知识Agent，支持"记忆"工长采购偏好实现秒级推荐
3. **门店高效运营模块** - 多维表格AI自动分析销售/库存/客流，多维表格即轻量ERP
4. **私域客户维护模块** - aily智能体自动生成跟进话术，多维表格自动排程跟进任务
5. **3515县域大屏** - 县域门店排行、AI经营洞察、一店一码扫码赋能、飞书AI能力矩阵

## 项目结构

```
yuhong-smart-store/
├── README.md                    # 项目说明
├── requirements.txt             # Python依赖
├── run.sh                       # 启动脚本
├── .env.example                 # 环境变量示例
├── GitHub搭建教程.md            # 手把手GitHub上传教程
├── 补充材料汇总说明.md          # 材料导航和使用指南
├── docs/                        # 项目文档（6份，共约4000行）
│   ├── 01_行业研究与竞品分析报告.md
│   ├── 02_技术方案架构设计文档.md
│   ├── 03_用户需求调研报告.md
│   ├── 04_实施路线图与里程碑.md
│   ├── 05_差异化竞争策略与12强攻略.md
│   └── 06_飞书AI实操配置手册.md
├── src/                         # 源代码
│   ├── app.py                   # Flask主应用（含5个页面路由+16个API）
│   ├── config.py                # 配置文件
│   ├── modules/                 # 核心业务模块
│   │   ├── store_inspection.py  # 门店巡检模块
│   │   ├── ai_shopping_guide.py # AI导购模块
│   │   ├── store_operation.py   # 门店运营模块
│   │   └── customer_relation.py # 私域客户维护模块
│   ├── api/                     # 飞书API封装
│   │   ├── feishu_bitable.py    # 多维表格API
│   │   └── feishu_aily.py       # aily智能体API
│   └── utils/                   # 工具函数
│       └── helpers.py
├── templates/                   # 前端页面模板
│   ├── index.html               # 首页/仪表盘
│   ├── inspection.html          # 门店巡检页面
│   ├── guide.html               # AI导购页面
│   └── bigscreen.html           # 3515县域大屏（亮点功能）
├── data/                        # 模拟数据
│   ├── products.json            # 产品知识库
│   ├── stores.json              # 门店数据
│   └── inspection_records.json  # 巡检记录
├── static/                      # 静态资源
├── requirements.txt             # Python依赖
└── run.sh                       # 启动脚本
```

## 快速开始

### 环境要求
- Python 3.9+
- pip

### 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/yuhong-smart-store.git
cd yuhong-smart-store

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置飞书API密钥（可选，不配置则使用模拟数据）
cp src/config.example.py src/config.py
# 编辑 config.py 填入你的飞书应用凭证

# 4. 启动应用
python src/app.py

# 5. 打开浏览器访问
# http://localhost:5000
```

## 技术栈

| 技术 | 用途 | 说明 |
|------|------|------|
| Python + Flask | 后端服务 | 轻量级Web框架 |
| 飞书开放平台API | 数据存储与AI能力 | 多维表格、aily智能体 |
| 飞书aily | AI对话与推荐 | 产品知识问答、智能导购 |
| 多维表格AI | 数据分析 | 销售/库存/客流分析 |
| 妙搭低代码 | 巡检应用搭建 | 移动端巡检表单 |
| Chart.js | 数据可视化 | 门店运营看板 |
| Bootstrap 5 | 前端UI | 响应式设计 |

## 核心功能演示

### 1. 门店巡检模块
- 移动端巡检表单（陈列标准、卫生状况、价签准确等）
- AI图像识别自动检测陈列合规性
- 巡检结果自动同步至多维表格

### 2. AI导购模块
- 产品知识智能问答（防水材料选型、施工方案等）
- 基于客户需求的智能推荐
- 施工工艺视频自动推送

### 3. 门店运营看板
- 实时销售数据分析
- 库存周转预警
- 客流热力图
- 经营洞察AI报告

### 4. 私域客户维护
- 客户画像自动构建
- AI话术推荐
- 跟进任务自动生成
- 复购预测

## 飞书AI能力对接说明

本项目设计了与飞书AI能力的完整对接方案：

| 模块 | 飞书能力 | 对接方式 |
|------|---------|---------|
| 门店巡检 | 妙搭低代码 | 搭建移动巡检应用 |
| AI导购 | aily智能体 | 构建产品知识Agent |
| 门店运营 | 多维表格AI | AI字段 + 数据分析工作流 |
| 私域维护 | aily + 多维表格 | 客户管理表 + 自动化跟进 |

详见 `docs/02_技术方案架构设计文档.md`

## 赛事信息

- **赛事名称**: 2026 AI先锋未来人才大赛
- **企业命题**: 东方雨虹 - 借助飞书AI打造零售门店智慧运营助手
- **赛道**: AI + 营销推广
- **区域**: 华北

## License

MIT License - 本项目仅用于2026 AI先锋未来人才大赛参赛展示

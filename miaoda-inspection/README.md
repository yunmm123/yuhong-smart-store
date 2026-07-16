# 雨虹门店巡检应用 - 妙搭部署指南

## 应用概述

移动端门店巡检应用，支持：
- 6维度标准化巡检评分（陈列/卫生/价签/库存/服务/安全）
- 巡检记录实时同步飞书多维表格
- 巡检历史查看与筛选
- 统计看板（通过率/平均分/各维度分析）

## 妙搭部署步骤

### 1. 创建妙搭应用

1. 打开 [飞书妙搭](https://miaoda.feishu.cn)
2. 点击「创建应用」→ 选择「本地开发」→ 应用类型选「全栈应用」
3. 应用名称填「雨虹门店巡检」
4. 创建完成后获取 `app_id`

### 2. 配置环境变量

在妙搭应用设置页，添加以下环境变量（online环境）：

| 变量名 | 值 |
|--------|-----|
| FEISHU_APP_ID | cli_aadc44eb88f89cc4 |
| FEISHU_APP_SECRET | rknUZjLCegvpqAyzgL531f1CO712ejxw |
| BITABLE_APP_TOKEN | R7v9bKHNdaBsDFsDdvzcXICOnWh |
| TABLE_STORE | tblz4EvPXhpCVy6l |
| TABLE_INSPECTION | tbl6WQHXuVF6Qgk9 |

### 3. 初始化本地仓库

```bash
# 在妙搭应用页面获取 Git 仓库地址
cd miaoda-inspection
# 将代码推送到妙搭 Git 仓库
git init
git add .
git commit -m "init: 雨虹门店巡检应用"
git remote add origin <妙搭Git仓库地址>
git push -u origin main
```

### 4. 部署上线

1. 在妙搭应用页面点击「部署」
2. 等待构建完成（约1-2分钟）
3. 部署成功后获得在线访问链接（*.feishuapp.com）
4. 在「可见范围」中设置为「租户内可见」或「所有人可见」

### 5. 验证

- 打开部署链接，确认应用正常加载
- 选择门店、填写巡检人、滑动评分、提交
- 检查飞书多维表格中是否新增了巡检记录
- 切换到「巡检历史」Tab 查看记录
- 切换到「统计看板」Tab 查看分析数据

## 本地开发

```bash
cd miaoda-inspection
npm install
npm start
# 打开 http://localhost:3000
```

## 技术架构

- **前端**: 单页HTML（移动优先设计），无框架依赖，纯原生JS
- **后端**: Node.js + Express，代理飞书Bitable API
- **数据存储**: 飞书多维表格（无需自建数据库）
- **部署**: 飞书妙搭平台（自动扩缩容，免运维）

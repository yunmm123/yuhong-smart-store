# static/ 目录说明

本目录用于存放Flask应用的静态资源（CSS/JS/图片）。

当前项目前端样式和图表库均通过CDAN加载（Bootstrap 5 + Chart.js），
模板内联了页面级CSS，因此本目录暂无独立静态文件。

如需扩展自定义样式或脚本，请放置在此目录下，
Flask会自动通过 `/static/` 路径提供服务。

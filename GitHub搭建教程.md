# GitHub仓库搭建分步教程

> 本教程将手把手教你把"雨虹智慧门店运营助手"项目上传到GitHub，并获得可分享的仓库链接填入报名表。

---

## 第一步：在GitHub上创建新仓库

1. 打开浏览器，访问 **https://github.com/new**
2. 登录你的GitHub账号（如果没有，先注册一个）
3. 填写仓库信息：
   - **Repository name**：`yuhong-smart-store`
   - **Description**：`2026 AI先锋未来人才大赛 - 东方雨虹零售门店智慧运营助手`
   - **Visibility**：选择 **Public**（公开，这样评审可以看到）
   - **勾选** "Add a README file"
   - **.gitignore**：选择 `Python`
   - **License**：选择 `MIT License`
4. 点击绿色的 **"Create repository"** 按钮

---

## 第二步：下载项目文件

我已经为你创建好了完整的项目文件，存放在 `/workspace/yuhong-smart-store/` 目录下。

你可以通过以下方式获取这些文件：
- 如果你使用的是TRAE IDE，直接在文件浏览器中找到 `/workspace/yuhong-smart-store/` 文件夹
- 将整个文件夹复制到你的电脑本地

---

## 第三步：安装Git（如果还没有安装）

### Windows
1. 访问 https://git-scm.com/download/win
2. 下载并安装，一路"Next"即可
3. 安装完成后，打开"Git Bash"或"命令提示符"

### Mac
```bash
# 如果已安装Homebrew
brew install git
```

### 验证安装
```bash
git --version
# 应该显示类似: git version 2.43.0
```

---

## 第四步：配置Git（首次使用需要）

在终端/命令行中执行：
```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

---

## 第五步：将项目上传到GitHub

打开终端/命令行，依次执行以下命令：

```bash
# 1. 进入项目目录
cd /path/to/yuhong-smart-store
# （将 /path/to/ 替换为你电脑上实际的路径）

# 2. 初始化Git仓库
git init

# 3. 添加所有文件到暂存区
git add .

# 4. 查看将要提交的文件（确认无误）
git status

# 5. 提交到本地仓库
git commit -m "初始提交：雨虹智慧门店运营助手完整项目

- 四大核心模块：门店巡检、AI导购、门店运营、私域客户维护
- 飞书AI对接：aily智能体API、多维表格API封装
- 完整文档：行业研究、技术架构、用户调研、实施路线图
- 可运行Demo：Flask Web应用 + 模拟数据"

# 6. 关联远程GitHub仓库
# 将下面的 URL 替换为你刚才创建的仓库地址
git remote add origin https://github.com/你的用户名/yuhong-smart-store.git

# 7. 推送到GitHub
git branch -M main
git push -u origin main
```

**如果提示输入用户名和密码：**
- Username：你的GitHub用户名
- Password：使用GitHub Personal Access Token（不是登录密码）
  - 获取Token：GitHub → Settings → Developer settings → Personal access tokens → Generate new token
  - 勾选 `repo` 权限
  - 复制生成的Token作为密码粘贴

---

## 第六步：验证上传成功

1. 打开你的GitHub仓库页面：`https://github.com/你的用户名/yuhong-smart-store`
2. 确认能看到所有文件和文件夹
3. 你的仓库链接就是：`https://github.com/你的用户名/yuhong-smart-store`

---

## 第七步：本地运行Demo验证

在上传之前或之后，你可以在本地运行Demo确认一切正常：

```bash
# 1. 进入项目目录
cd /path/to/yuhong-smart-store

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行应用
python src/app.py

# 4. 打开浏览器访问
# http://localhost:5000
```

你应该能看到：
- 首页仪表盘（数据概览、四大模块入口、销售趋势图）
- 门店巡检页面（巡检表单、AI检测、历史记录）
- AI导购页面（智能问答、产品搜索、智能推荐）

---

## 第八步：（可选）创建GitHub Pages在线演示

如果你想提供一个在线可访问的Demo链接：

1. 在仓库中创建 `gh-pages` 分支：
```bash
git checkout -b gh-pages
```

2. 将 `templates/index.html` 的内容复制为仓库根目录的 `index.html`
3. 推送：
```bash
git add .
git commit -m "添加GitHub Pages演示页面"
git push origin gh-pages
```

4. 在GitHub仓库设置中启用Pages：
   - Settings → Pages → Source → 选择 `gh-pages` 分支
   - 等待几分钟后，你会得到一个在线链接：`https://你的用户名.github.io/yuhong-smart-store/`

---

## 第九步：将链接填入报名表

在报名表的"团队补充材料"部分：

### 附件格式
```
GitHub仓库：https://github.com/你的用户名/yuhong-smart-store
```

### 链接格式
```
在线Demo：https://你的用户名.github.io/yuhong-smart-store/（如果做了GitHub Pages）
项目文档：https://github.com/你的用户名/yuhong-smart-store/tree/main/docs
```

---

## 常见问题

### Q: push时提示"Permission denied"
A: 需要配置SSH key或使用HTTPS + Personal Access Token。最简单的方式是使用Token：
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → 勾选 `repo` → Generate
3. push时用户名填GitHub用户名，密码填Token

### Q: push时提示"rejected - non-fast-forward"
A: 远程仓库已有README等文件，先拉取再推送：
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Q: 文件太大无法上传
A: 确保没有大文件，`.gitignore`已排除不需要的文件。如果单个文件超过100MB，需要使用Git LFS。

### Q: 想修改仓库为Public但找不到设置
A: 仓库页面 → Settings → 滚动到最底部 "Danger Zone" → Change repository visibility → Make public

---

## 项目文件清单

上传后你的仓库应该包含以下文件：

```
yuhong-smart-store/
├── README.md                              # 项目说明
├── requirements.txt                       # Python依赖
├── run.sh                                # 启动脚本
├── .env.example                          # 环境变量示例
├── .gitignore                            # Git忽略配置
├── LICENSE                               # MIT许可证
├── docs/
│   ├── 01_行业研究与竞品分析报告.md        # ~400行
│   ├── 02_技术方案架构设计文档.md          # ~1000行，含16个架构图
│   ├── 03_用户需求调研报告.md             # ~300行
│   └── 04_实施路线图与里程碑.md            # ~300行
├── src/
│   ├── app.py                            # Flask主应用
│   ├── config.py                         # 配置文件
│   ├── api/
│   │   ├── feishu_bitable.py             # 飞书多维表格API
│   │   └── feishu_aily.py                # 飞书aily智能体API
│   └── modules/
│       ├── store_inspection.py           # 门店巡检模块
│       ├── ai_shopping_guide.py          # AI导购模块
│       ├── store_operation.py            # 门店运营模块
│       └── customer_relation.py          # 私域客户维护模块
├── templates/
│   ├── index.html                        # 首页仪表盘
│   ├── inspection.html                   # 门店巡检页面
│   └── guide.html                        # AI导购页面
└── data/
    ├── products.json                     # 产品知识库(8款产品)
    ├── stores.json                       # 门店数据(5家门店)
    └── inspection_records.json           # 巡检记录(8条)
```

---

## 总结

完成以上步骤后，你将获得：
1. **一个完整的GitHub公开仓库** — 展示你的技术实力和项目完成度
2. **4份专业文档** — 支撑开题报告的行业研究、技术架构、用户调研和实施路线
3. **一个可运行的Demo** — 评审可以直接clone下来运行体验
4. **可直接填入报名表的链接** — GitHub仓库URL + 可选的在线Demo链接

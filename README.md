# GitHub Trending Crawler

> Win11 风格的 GitHub 热门仓库爬虫 | A Win11-style GitHub trending repository crawler

[中文](#中文) | [English](#english)

---

## 中文

### 简介

一款基于 Python 的 GitHub 热门仓库爬虫，采用 Win11 资源管理器风格界面，支持热榜浏览、仓库搜索、镜像加速下载、翻译、多语言等功能。

### 功能一览

| 功能 | 说明 |
|------|------|
| 热榜浏览 | 日榜 / 周榜 / 月榜，支持按语言筛选 |
| 仓库搜索 | 按关键词搜索 GitHub 仓库，查看详细信息 |
| 仓库详情 | 点击仓库查看 README、Issues、评论 |
| 镜像加速下载 | 多源自动切换：ghfast.top / ghproxy.cn / 直连 |
| 翻译功能 | Google Translate / 百度翻译，中英互译 |
| 多语言界面 | 中文 / English / 日本語 / 한국어 / Français / Deutsch / Español |
| 批量下载 | 多线程并发，实时进度条，支持终止 |
| GitHub Token | 可选配置，提升 API 速率限制 |

### 安装教程

#### 方式一：直接运行 exe（推荐）

1. 前往 [Releases](https://github.com/NiMark886/github-trending-crawler/releases) 页面
2. 下载 `GitHub热榜爬虫.exe`
3. 双击运行即可，无需安装 Python

> 如果被杀毒软件拦截，请添加信任或暂时关闭杀毒软件。

#### 方式二：从源码运行

**前置要求：** Python 3.8+

```bash
# 1. 克隆仓库
git clone https://github.com/NiMark886/github-trending-crawler.git
cd github-trending-crawler

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动 GUI
python gui.py
```

#### 方式三：打包为 exe

```bash
pip install pyinstaller
python -m PyInstaller github_crawler.spec
```

生成的 exe 在 `dist/` 目录下。

### 使用指南

#### 热榜浏览

1. 启动后默认进入「热榜」页面
2. 选择时间范围：日榜 / 周榜 / 月榜
3. 可选填语言筛选（如 python、javascript）
4. 点击「获取热榜」按钮
5. 点击仓库行 → 查看详情（README + Issues）
6. 点击「下载」按钮 → 跳转到 GitHub 下载页面

#### 仓库搜索

1. 切换到「搜索」页面
2. 输入关键词，可选填语言筛选
3. 点击「搜索」按钮
4. 点击仓库行查看详情
5. 右侧详情面板可查看 Stars、Forks、Issues 等

#### GitHub 仓库下载

1. 从热榜或搜索结果点击「下载」按钮，自动跳转到此页面
2. 选择下载目录
3. 设置并发线程数
4. 点击「下载热榜结果」或「下载搜索结果」
5. 支持多源镜像加速，自动切换
6. 可随时点击「终止」按钮停止下载

#### 链接下载

1. 切换到「链接下载」页面
2. 粘贴下载链接，支持单个或批量下载
3. 设置保存目录和线程数
4. 点击「单个下载」或「批量下载」

#### 仓库详情页

- 点击热榜/搜索结果中的仓库行（非下载按钮）打开详情窗口
- **顶部**：仓库名称、作者、描述、Stars/Forks/Issues、标签
- **中部**：README 内容，支持翻译
  - 「中→英」：将中文翻译为英文
  - 「英→中」：将英文翻译为中文
  - 「显示原文」：恢复原始内容
- **下部**：Open Issues 列表，点击可查看评论

#### 翻译功能

**Google Translate（默认）**
- 免费，无需配置
- 需要能访问 Google（国内可能需要代理）

**百度翻译**
- 国内可直接使用
- 需要在 [fanyi.baidu.com](https://fanyi.baidu.com) 申请 App ID 和密钥（免费）
- 在「设置」页面填写百度 App ID 和密钥

#### 设置

在「设置」页面可配置：

| 配置项 | 说明 |
|--------|------|
| 下载目录 | 仓库 ZIP 保存位置 |
| 并发线程 | 下载线程数 (1-20) |
| 请求间隔 | API 请求间隔 (秒) |
| GitHub Token | 可选，提升 API 速率 10→30 次/分 |
| 界面语言 | 7 种语言可选 |
| 翻译引擎 | Google Translate / 百度翻译 |
| 百度 App ID / Key | 百度翻译 API 凭证 |

配置文件保存在 `~/.github_crawler/config.json`。

#### GitHub Token 配置（可选）

1. 登录 GitHub → Settings → Developer settings
2. Personal access tokens → Generate new token
3. 勾选 `public_repo` 权限
4. 复制 token，粘贴到「设置」页面的 GitHub Token 字段
5. 配置后 API 速率从 10 次/分钟提升到 30 次/分钟

### 项目结构

```
├── gui.py                      # GUI 主界面 (Win11 风格)
├── github_trending_crawler.py  # 热榜爬虫核心
├── search.py                   # 仓库搜索模块
├── config.py                   # 配置管理
├── downloader.py               # 下载模块
├── requirements.txt            # Python 依赖
├── github_crawler.spec         # PyInstaller 打包配置
├── icon.ico                    # 应用图标
└── LICENSE                     # MIT License
```

### 常见问题

**Q: 获取热榜失败，提示 API 速率限制？**
A: 无 Token 时限制为 10 次/分钟。在「设置」中配置 GitHub Token 可提升到 30 次/分钟。

**Q: 翻译功能不可用？**
A: Google Translate 需要能访问 Google；百度翻译需要在设置中配置 App ID 和密钥。

**Q: exe 被杀毒软件拦截？**
A: PyInstaller 打包的程序常被误报，请添加信任或暂时关闭杀毒软件。

**Q: 下载速度很慢？**
A: 程序会自动尝试镜像加速。如果仍然很慢，可能是网络问题，可尝试使用代理。

### 法律声明

本项目仅供学习交流使用。请遵守 GitHub 的服务条款和 robots.txt。

---

## English

### Introduction

A Python-based GitHub trending repository crawler with a Win11 Explorer-style GUI. Browse trending repos, search GitHub, download with mirror acceleration, translate content, and use the interface in 7 languages.

### Features

| Feature | Description |
|---------|-------------|
| Trending | Daily / Weekly / Monthly, filter by language |
| Search | Search GitHub repos by keyword |
| Repo Detail | View README, Issues, and comments |
| Mirror Download | Auto-switch: ghfast.top / ghproxy.cn / direct |
| Translation | Google Translate / Baidu Translate |
| Multi-language | 中文 / English / 日本語 / 한국어 / Français / Deutsch / Español |
| Batch Download | Multi-threaded, real-time progress, stop button |
| GitHub Token | Optional, increases API rate limit |

### Installation

#### Option 1: Download exe (Recommended)

1. Go to [Releases](https://github.com/NiMark886/github-trending-crawler/releases)
2. Download `GitHub热榜爬虫.exe`
3. Double-click to run, no Python needed

> If blocked by antivirus, add an exception or temporarily disable it.

#### Option 2: Run from source

**Requirements:** Python 3.8+

```bash
# 1. Clone the repository
git clone https://github.com/NiMark886/github-trending-crawler.git
cd github-trending-crawler

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch GUI
python gui.py
```

#### Option 3: Build exe

```bash
pip install pyinstaller
python -m PyInstaller github_crawler.spec
```

Output will be in the `dist/` directory.

### Usage Guide

#### Trending

1. Opens on the "Trending" page by default
2. Select time range: Daily / Weekly / Monthly
3. Optionally filter by language (e.g., python, javascript)
4. Click "Fetch Trending"
5. Click a repo row → view detail (README + Issues)
6. Click "Download" → jump to GitHub download page

#### Search

1. Switch to the "Search" page
2. Enter keywords, optionally filter by language
3. Click "Search"
4. Click a repo row to view details
5. Right panel shows Stars, Forks, Issues, etc.

#### GitHub Download

1. Click "Download" from trending/search results to jump here
2. Select download directory
3. Set thread count
4. Click "Download Trending" or "Download Search"
5. Multi-source mirror acceleration with auto-fallback
6. Click "Stop" to cancel at any time

#### URL Download

1. Switch to "URL Download" page
2. Paste download URL(s), supports single or batch
3. Set save directory and thread count
4. Click "Single" or "Batch"

#### Repo Detail Page

- Click a repo row (not the download button) to open detail window
- **Top**: Repo name, author, description, Stars/Forks/Issues, topics
- **Middle**: README content with translation support
  - "ZH→EN": Translate Chinese to English
  - "EN→ZH": Translate English to Chinese
  - "Original": Restore original content
- **Bottom**: Open Issues list, click to view comments

#### Translation

**Google Translate (Default)**
- Free, no configuration needed
- Requires access to Google

**Baidu Translate**
- Works in China without proxy
- Requires App ID from [fanyi.baidu.com](https://fanyi.baidu.com) (free)
- Enter credentials in Settings page

#### Settings

| Setting | Description |
|---------|-------------|
| Download Dir | Where to save repo ZIP files |
| Threads | Download thread count (1-20) |
| Rate Limit | API request interval (seconds) |
| GitHub Token | Optional, increases rate from 10→30 req/min |
| Language | 7 languages available |
| Translate Engine | Google Translate / Baidu Translate |
| Baidu App ID / Key | Baidu Translate API credentials |

Config file: `~/.github_crawler/config.json`

#### GitHub Token (Optional)

1. Login to GitHub → Settings → Developer settings
2. Personal access tokens → Generate new token
3. Check `public_repo` scope
4. Copy token and paste into Settings → GitHub Token
5. Increases API rate from 10 to 30 requests/minute

### Project Structure

```
├── gui.py                      # GUI (Win11 style)
├── github_trending_crawler.py  # Trending crawler core
├── search.py                   # Repository search
├── config.py                   # Configuration manager
├── downloader.py               # Download module
├── requirements.txt            # Python dependencies
├── github_crawler.spec         # PyInstaller build config
├── icon.ico                    # App icon
└── LICENSE                     # MIT License
```

### FAQ

**Q: Trending fails with API rate limit?**
A: Without a token, the limit is 10 requests/minute. Add a GitHub Token in Settings to increase to 30/min.

**Q: Translation not working?**
A: Google Translate requires access to Google. Baidu Translate requires App ID and Key in Settings.

**Q: exe blocked by antivirus?**
A: PyInstaller-built executables are often flagged as false positives. Add an exception or temporarily disable antivirus.

**Q: Download is very slow?**
A: The program automatically tries mirror acceleration. If still slow, it may be a network issue — try using a proxy.

### License

MIT License. For educational purposes only. Please follow GitHub's Terms of Service and robots.txt.

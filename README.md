# Red Command（红队指挥控制平台）
Red Command 是一款综合性红队指挥控制平台，提供资产管理、主机监控、任务管理、作战会议室等功能。

## 功能特性

### 🗂️ 资产管理
- 单位层级目录树管理
- 自定义添加单位和子单位
- 资产IP列表管理
- Excel/JSON批量导入资产
- 资产隶属单位关联

### 🖥️ 主机管理
- 客户端状态监控（在线/离线）
- 动作记录审计
- 实时命令执行
- 聊天消息记录

### 📋 任务管理
- 任务计划创建与管理
- 任务目标分配
- 任务进度跟踪
- 小队分组管理

### 🛠️ 工具列表
- 工具版本管理
- 工具上传与下载
- 工具访问链接管理
- 工具分类展示

### 📦 成果汇总
- 渗透测试结果管理
- 按目标IP分组展示
- 文件上传与查看
- 权限控制（仅查看自己上传的成果）

### 💬 作战会议室
- 实时消息发送与接收（WebSocket）
- 表情符号支持
- 图片上传与预览
- 文件上传与下载
- 消息引用回复
- 成员选择与管理
- 权限控制（仅查看包含自己的会议室）

### 🎥 录屏监控
- 桌面自动录屏
- 锁屏状态自动停止录屏
- 解锁自动恢复录屏
- 录制文件加密上传
- 录制片段自动分割（60秒/段）

### 📊 态势总览
- 在线主机统计
- 今日动作统计
- 成果数量统计
- 工具数量统计
- 最新动作记录展示

### 🔐 安全特性
- HTTPS加密通信
- JWT身份认证
- 密码加密存储（Fernet）
- 视频文件加密传输
- 用户会话定时退出（20分钟）

### 👥 用户权限
- 管理员：可查看所有系统功能和数据
- 普通用户：
  - 成果汇总：仅能看到自己上传的成果
  - 工具列表：查看全部工具
  - 任务管理：查看自己创建的任务或同组任务
  - 资产管理：查看全部资产
  - 作战会议室：仅能看到包含自己的会议室

## 项目结构

```
red_command/
├── agent/                    # Go语言客户端
│   ├── collector/            # 数据采集模块
│   ├── config/               # 配置管理
│   ├── db/                   # 本地数据库
│   ├── recorder/             # 录屏模块
│   ├── sync/                 # 数据同步模块
│   ├── main.go               # Agent入口
│   └── go.mod                # Go依赖
├── server/                   # 后端服务
│   ├── app/                  # 应用代码
│   │   ├── api/              # API路由
│   │   ├── core/             # 核心配置
│   │   ├── db/               # 数据库连接
│   │   ├── models/           # 数据模型
│   │   ├── services/         # 业务服务
│   │   └── videos/           # 加密视频存储
│   ├── web/                  # 前端代码
│   │   ├── src/              # Vue源码
│   │   └── index.html        # 主页面
│   ├── cert/                 # SSL证书
│   ├── main.py               # 后端入口
│   └── requirements.txt      # Python依赖
└── .gitignore                # Git忽略配置
```

## 安装部署

### 环境要求

- Python 3.8+
- Go 1.21+
- FFmpeg (录屏功能)
- Linux (推荐)

### 后端安装

```bash
# 进入后端目录
cd server

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（自动创建）
# 启动服务时会自动创建数据库表

# 启动服务
bash start.sh
```

服务将在以下地址启动：
- HTTPS: `https://localhost:8443`
- HTTP: `http://localhost:8000`（自动重定向到HTTPS）

### 前端安装

前端已集成在后端 `web/index.html` 中，无需额外安装。

### Agent编译

```bash
# 进入Agent目录
cd agent

# 编译
go build -o agent .

# 运行
./agent --server https://your-server:8443
```

## 使用说明

### 默认账号

- **用户名**: admin
- **密码**: admin

### 资产管理

1. 登录系统后点击左侧"资产管理"菜单
2. 左侧显示单位层级目录树
3. 点击单位节点查看该单位下的资产列表
4. 右键节点可添加子单位或在此单位下添加资产

### 作战会议室

1. 点击左侧"作战会议室"菜单
2. 点击"+ 创建房间"创建新会议室
3. 选择会议室成员后创建
4. 支持发送文本、表情、图片、文件
5. 点击消息下方"回复"按钮引用消息

### 录屏功能

Agent运行后自动启动录屏，支持：
- 锁屏自动停止录屏
- 解锁自动恢复录屏
- 每60秒自动分割录制片段

### 任务管理

1. 点击左侧"任务管理"菜单
2. 点击"新建筹划"创建任务计划
3. 选择小队和任务目标
4. 点击任务卡片查看详情和目标列表

## 配置说明

### 后端配置

后端配置位于 `server/app/core/config.py`：

```python
class Settings:
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 20
    DB_URL: str = "sqlite:///./app/db/sql_app.db"
    SSL_CERT_PATH: str = "cert/server.crt"
    SSL_KEY_PATH: str = "cert/server.key"
```

### Agent配置

通过命令行参数指定：

```bash
./agent --server https://your-server:8443
```

## 安全注意事项

1. **HTTPS**: 所有通信均采用HTTPS加密
2. **密码**: 使用Fernet对称加密存储（允许管理员查看）
3. **视频**: 上传视频使用AES加密存储
4. **权限**: 不同用户角色有不同操作权限
5. **会话**: 用户会话20分钟无操作自动退出

## 开发说明

### 添加新功能

1. 在 `server/app/models/models.py` 添加数据库模型
2. 在 `server/app/models/schemas.py` 添加Pydantic模型
3. 在 `server/app/api/routes.py` 添加API路由
4. 在 `server/web/index.html` 添加前端页面

### 测试

```bash
# 运行后端测试
cd server
python -m pytest

# 编译Agent测试
cd agent
go build -o agent .
```

## 贡献

欢迎提交Issue和Pull Request！

---

**注意**: 本项目仅供安全研究和教育目的使用，请遵守相关法律法规。
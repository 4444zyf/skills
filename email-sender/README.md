# Email Sender Skill

通过SMTP发送邮件，支持将文件夹打包成ZIP作为附件发送。

## 功能特性

- 📧 支持标准SMTP协议（Gmail、QQ邮箱、163邮箱等）
- 📦 自动将文件夹压缩为ZIP格式
- 🔒 配置安全存储在 `~/.config/email-sender/`
- 📝 支持自定义邮件主题和正文
- 🗂️ 支持发送多个文件夹
- 🧹 自动清理临时压缩文件

## 安装

将此技能复制到你的Claude skills目录：

```bash
cp -r email-sender ~/.claude/skills/
```

## 使用方法

### 基本用法

```bash
# 发送文件夹
邮件发送 ./my-project 到 recipient@example.com

# 带主题
邮件发送 ./reports 到 boss@company.com --subject "月度报告"

# 带正文
邮件发送 ./data 到 team@company.com --subject "数据备份" --body "请查收附件中的数据"

# 保留ZIP文件
邮件发送 ./archive 到 backup@example.com --keep-zip
```

### 使用Python脚本直接运行

```bash
# 配置
python scripts/config_manager.py setup

# 查看配置
python scripts/config_manager.py show

# 发送邮件
python scripts/send_email.py ./folder --to recipient@example.com --subject "主题"
```

## 首次配置

首次使用时，技能会提示你输入SMTP配置：

1. **SMTP服务器** - 如 smtp.gmail.com、smtp.qq.com
2. **端口** - 通常587（TLS）或465（SSL）
3. **邮箱地址** - 发件人邮箱
4. **密码** - 邮箱密码或应用专用密码（Gmail需要后者）
5. **TLS** - 建议使用TLS加密

### 常见邮箱设置

| 邮箱 | SMTP服务器 | 端口 | 注意事项 |
|------|-----------|------|----------|
| Gmail | smtp.gmail.com | 587 | 需使用应用专用密码 |
| QQ邮箱 | smtp.qq.com | 587 | 需开启SMTP服务 |
| 163邮箱 | smtp.163.com | 587 | 需开启SMTP服务 |
| Outlook | smtp.office365.com | 587 | - |

### 获取Gmail应用专用密码

1. 访问 https://myaccount.google.com/apppasswords
2. 登录你的Google账号
3. 生成新应用密码
4. 在配置中使用此密码代替你的常规密码

## 技能结构

```
email-sender/
├── SKILL.md              # 技能主文档
├── README.md             # 本说明文件
├── evals/
│   └── evals.json        # 测试用例
└── scripts/
    ├── config_manager.py # 配置管理脚本
    └── send_email.py     # 邮件发送脚本
```

## 技术细节

- **Python版本**: 3.7+
- **依赖**: 仅使用Python标准库，无需额外安装
- **配置存储**: `~/.config/email-sender/config.json`（权限0600）
- **压缩格式**: ZIP（Deflated压缩算法）
- **编码**: UTF-8支持中文

## 安全说明

- 配置文件权限设置为仅用户可读（0600）
- 支持TLS加密传输
- 建议使用应用专用密码而非主密码
- 不记录或传输密码到外部

## 故障排查

### 认证失败

- 检查邮箱和密码是否正确
- Gmail用户需使用应用专用密码
- 确认邮箱SMTP服务已开启

### 连接失败

- 检查SMTP服务器地址和端口
- 确认网络连接正常
- 检查防火墙设置

### 附件过大

- 大多数SMTP服务器限制附件大小（通常10-25MB）
- 如需发送大文件，建议分卷压缩或使用云存储链接

## 许可

MIT License

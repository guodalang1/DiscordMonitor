2025 最硬 Discord 主号复用公告监控 → Telegram（纯源码）

1. **创建专用 Chrome 快捷方式**（桌面右键 → 新建 → 快捷方式）
然后登录在新建的浏览器上登录自己的discord 账号
   位置填写：
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --remote-allow-origins=* --user-data-dir="D:\Profile 52"
text（`D:\Profile 52` 改成你自己的空文件夹，比如 D:\DCProfile）

2. 用这个快捷方式启动 Chrome → 正常登录你的 Discord 主号 → 保持开着

3. 用记事本打开 config.py，填 3 处：
- Telegram API_ID / API_HASH（my.telegram.org 拿）
- 要监控的 Discord 频道链接
- 推送到的 Telegram 群ID（-100 开头）

4. 双击 main.py 运行（或右键 → 用 Python 打开）
→ 自动连接你开着的浏览器
→ 弹出绿色状态窗（按 Esc 隐藏，点×退出）
→ 首次让你输入手机号+验证码（只此一次）


以后只要 Chrome 开着，双击 main.py 就直接运行，零弹窗，完美隐身！

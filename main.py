# -*- coding: utf-8 -*-
"""
纯 DOM 版 Discord 公告监控（100% 可靠，无后台问题）
借鉴原脚本：滚动提取 + 翻译重试 + 日志 + 剪贴板 + Telegram
"""

import pyperclip
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from DrissionPage import Chromium
from bs4 import BeautifulSoup
import re
import time
import logging
from datetime import datetime, timedelta
import os
from telethon.sync import TelegramClient
import sys
import os

# 直接粘到 main.py 最前面（所有 import 下面就行）
# ==================== 配置 ====================
try:
    from config import *
except ImportError:
    print("错误：找不到 config.py")
    exit()

PYTHON_PROXY = globals().get('PYTHON_PROXY') or None

os.environ['NO_PROXY'] = '127.0.0.1,localhost,::1'

logging.basicConfig(
    filename=r"C:\Users\Administrator\Desktop\discord_announcement.log",
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)

now = time.time()
for ch in CHANNELS:
    match = re.search(r'/channels/\d+/(\d+)', ch["url"])
    if match:
        ch["channel_id"] = int(match.group(1))
    else:
        raise ValueError(f"无法提取 channel_id: {ch['url']}")
    ch["last_msg_id"] = None
    ch["last_check_time"] = now

# ==================== 翻译函数（支持代理 + 3次重试） ====================
def translate(text, proxy=None):
    if not text.strip():
        return text
    try:
        import urllib.parse
        encoded = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={encoded}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        proxies = {"http": proxy, "https": proxy} if proxy else None
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        for i in range(3):
            try:
                r = session.get(url, headers=headers, proxies=proxies, timeout=20)
                if r.status_code == 200:
                    data = r.json()
                    translated = "".join([part[0] for part in data[0] if part[0]])
                    return translated.strip()
            except Exception as e:
                if i < 2:
                    print(f"[翻译重试 {i+1}/3] {e}")
                    time.sleep(2)
                else:
                    print("[翻译失败] 保留原文")
        return text
    except Exception as e:
        print(f"[翻译异常] {e}")
        return text

# ==================== 接管本地浏览器 ====================
def connect_local_browser():
    print("正在接管你的浏览器...")
    try:
        page = Chromium(addr_or_opts=CHROME_PORT).latest_tab
        print("接管成功！")
        page.get('https://discord.com/channels/@me', timeout=60)
        page.wait.load_start()
        if not page.wait.doc_loaded(timeout=30):
            print("警告：页面未完全加载，但继续运行...")
        print(f"[{datetime.now().strftime('%H:%M')}] 已打开 Discord，开始守护公告")
        return page
    except Exception as e:
        print(f"接管失败: {e}")
        print("请确保：")
        print(f"1. Chrome 已启动，并带参数：--remote-debugging-port={CHROME_PORT} --user-data-dir=\"{CHROME_PROFILE}\"")
        print("2. 没有其他程序占用端口")
        return None

# ==================== DOM 提取公告（借鉴原脚本） ====================
def get_announcement_by_dom(page, ch):
    try:
        page.get(ch["url"], timeout=60)
        page.wait.load_start()
        if not page.wait.eles_loaded('xpath://ol[@data-list-id="chat-messages"]', timeout=20):
            return None, None, None, None

        page.run_js('document.querySelector(\'[data-list-id="chat-messages"]\')?.scrollIntoView({block: "end"})')
        time.sleep(1)

        if not page.wait.eles_loaded('xpath://li[contains(@id, "chat-messages-")][last()]', timeout=10):
            return None, None, None, None

        last_li = page.ele('xpath://li[contains(@id, "chat-messages-")][last()]')
        if not last_li:
            return None, None, None, None

        msg_id = last_li.attr('id')
        if msg_id == ch["last_msg_id"]:
            return None, None, None, None

        soup = BeautifulSoup(last_li.html, 'html.parser')
        content = soup.find("div", class_=re.compile(r"^messageContent"))
        if not content or not content.get_text(strip=True):
            return None, None, None, None

        clean_en = content.get_text("\n", strip=True)
        time_tag = soup.find("time")
        if not time_tag:
            return None, None, None, None
        hk_time = (
            datetime.fromisoformat(time_tag["datetime"].replace("Z", "+00:00"))
            + timedelta(hours=8)
        ).strftime("%m/%d %H:%M")

        name_tag = soup.find("span", class_=re.compile("username"))
        name = name_tag.get_text(strip=True) if name_tag else "Bot"

        clean_zh = translate(clean_en, proxy=PYTHON_PROXY)

        ch["last_msg_id"] = msg_id
        ch["last_check_time"] = time.time()
        return msg_id, name, hk_time, clean_zh
    except Exception as e:
        print(f"[{ch['name']}] DOM 提取失败: {e}")
        return None, None, None, None

# ==================== 推送函数 ====================
def send_to_telegram(ch, name, hk_time, text_zh):
    result = f"""## 最新公告 [{ch['name']}]
@mybitstar 香港時間

**{name} | {hk_time}**

{text_zh}"""

    print("\n" + "═" * 58)
    print("  最后一条公告更新！已翻译")
    print("═" * 58)
    print(f"  {name}  |  {hk_time}")
    print("─" * 58)
    print(text_zh)
    print("═" * 58)

    pyperclip.copy(result)
    if ch["name"] == "OPN":
        print("已复制到剪贴板！Ctrl+V 秒发 X")

    try:
        with TelegramClient(SESSION_NAME, API_ID, API_HASH) as c:
            c.start()
            c.send_message(ch["group_id"], result)
        print("已推送到群")
    except Exception as e:
        print(f"Telegram 失败: {e}")

    logging.info(f"[{ch['name']}] {name} | {hk_time}\n{text_zh}")

# ==================== 状态面板 ====================
def print_status():
    print(f"\n{'=' * 58}")
    print(f"  实时状态 | {datetime.now().strftime('%Y-%m-%d %I:%M %p')} HKT")
    print(f"{'=' * 58}\n")
    print(f"浏览器: 正常 (端口 {CHROME_PORT})")
    for ch in CHANNELS:
        last_time = datetime.fromtimestamp(ch["last_check_time"])
        next_check = last_time + timedelta(seconds=ch["check_interval"])
        countdown = int((next_check - datetime.now()).total_seconds())
        countdown_str = "检查中..." if countdown < 0 else f"{countdown//60}分{countdown%60}秒"
        msg_id_short = ch["last_msg_id"][-8:] if ch["last_msg_id"] else "无"
        print(f"{ch['name']:<6} | {last_time.strftime('%H:%M:%S')} | {msg_id_short} | {next_check.strftime('%H:%M:%S')} ({countdown_str})")
    print(f"{'=' * 58}\n")

# ==================== 主程序 ====================
print(f"[翻译代理] {'使用本地代理' if PYTHON_PROXY else '直连翻译'}")

page = connect_local_browser()
if not page:
    print("无法接管浏览器，程序退出")
    exit()

print("开始守护……\n")

last_status_time = 0
while True:
    try:
        now = time.time()

        if now - last_status_time >= 30:
            print_status()
            last_status_time = now

        # 纯 DOM 模式：按 check_interval 检查每个频道
        for ch in CHANNELS:
            if now - ch["last_check_time"] < ch["check_interval"]:
                continue

            msg_id, name, hk_time, text_zh = get_announcement_by_dom(page, ch)
            if msg_id:
                send_to_telegram(ch, name, hk_time, text_zh)

        time.sleep(MAIN_LOOP_SLEEP_BASE)

    except KeyboardInterrupt:
        print("\n手动停止，程序退出")
        break
    except Exception as e:
        print("程序出错，5秒后重试:", e)
        time.sleep(5)
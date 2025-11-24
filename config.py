# config.py
# 极简配置：每行只填 4 项
# name / url / group_id / check_interval（秒）

# Telegram API（去 https://my.telegram.org 自己注册拿）
API_ID = '12345789'
API_HASH = 'cdef0123456789abcdef'
SESSION_NAME = 'multi_monitor'

CHROME_PORT = 9223
CHROME_PROFILE = r"D:\Profile 52"     #你的浏览器的 个人资料路径 再浏览器输入框 输入“chrome://version/ ” 查询
# ==================== 你的项目（只改这 4 项）================
CHANNELS = [
    {
        "name": "OPN",                                                                                                            # ←项目名称显示名字，
        "url": "https://discord.com/channels/1369791841020674168/1369793575294079073",    # ← 改成你要监控的频道链接
        "group_id": -12345678,                                                                                                  # ← Telegram 推送群ID（-100开头）
        "check_interval": 40 * 60                                                                                                # ←检测的时间 40 分钟一次 # ，
    },
    {
        "name": "RELL",
        "url": "https://discord.com/channels/132124337322661600/132155018547773619",
        "group_id": -12345678,
        "check_interval": 50 * 60
    },
    {
        "name": "RYLS",
        "url": "https://discord.com/channels/123816722371475379/136491546700928562",
        "group_id": -12345678,
        "check_interval": 60 * 60
    },
    {
        "name": "egex",
        "url": "https://discord.com/channels/123945296846833665/123948484037691473",
        "group_id": -12345678,
        "check_interval": 70 * 60
    },

    # ... 你可以继续加到 10 个、20 个
]

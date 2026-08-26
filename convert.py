import os
import requests

# 動態取得當前專案資料夾下的 nhi_files
base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, "nhi_files")

# 如果資料夾不存在則自動建立，避免報錯
if not os.path.exists(input_dir):
    os.makedirs(input_dir)
    print(f"已自動建立資料夾: {input_dir}")

# 取得 GitHub Secret 傳進來的 Discord Webhook 網址
webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

# 執行通知發送
if webhook_url:
    data = {
        "content": "🔔 **健保規範每週檢查完成！**\n系統已完成最新規範比對與更新。"
    }
    try:
        response = requests.post(webhook_url, json=data)
        print(f"Discord 通知發送狀態: {response.status_code}")
    except Exception as e:
        print(f"發送 Discord 通知時發生錯誤: {e}")
else:
    print("未設定 DISCORD_WEBHOOK_URL，跳過發送通知。")
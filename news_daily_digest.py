import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===================== 固定配置 =====================
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PWD = os.getenv("EMAIL_PWD")
RECEIVER = "killuailixiya@163.com"  # 你的收件邮箱，已写死

NEWS_API_URL = "https://newsapi.org/v2/everything"
GAME_QUERY = "game OR video game OR steam OR playstation OR xbox"
AI_QUERY = "artificial intelligence OR AI OR OpenAI OR Google AI OR Meta AI"
AUTHORIZED_SOURCES = {
    "game": ["ign.com", "gamespot.com", "kotaku.com", "store.steampowered.com"],
    "ai": ["openai.com", "ai.google", "ai.meta.com", "technologyreview.com", "venturebeat.com"]
}
COUNT_PER_CATEGORY = 10
# ======================================================

def translate_title(text):
    try:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|zh-CN"
        res = requests.get(url, timeout=5).json()
        return res["responseData"]["translatedText"]
    except:
        return "翻译失败"

def fetch_news(category, query):
    params = {
        "q": query, "apiKey": NEWS_API_KEY, "language": "en",
        "sortBy": "publishedAt", "pageSize": 20
    }
    articles = requests.get(NEWS_API_URL, params=params, timeout=10).json().get("articles", [])
    if not articles: return []

    sorted_articles = []
    authorized = AUTHORIZED_SOURCES[category]
    for art in articles:
        if any(domain in art["url"] for domain in authorized):
            sorted_articles.append(art)
    for art in articles:
        if art not in sorted_articles:
            sorted_articles.append(art)

    final_news = sorted_articles[:COUNT_PER_CATEGORY]
    result = []
    for news in final_news:
        en_title = news["title"].strip()
        cn_title = translate_title(en_title)
        result.append({
            "category": "🎮 游戏资讯" if category == "game" else "🤖 AI 科技",
            "title_en": en_title, "title_cn": cn_title,
            "summary": news["description"] or "无概要",
            "source": news["source"]["name"] or "未知来源",
            "url": news["url"]
        })
    return result

def generate_daily_report(game_news, ai_news):
    html = """
    <html><head><meta charset="utf-8">
    <h2>每日游戏&AI重要新闻日报</h2>
    <p>每日10:00自动发送 | 游戏10条+AI10条 | 按重要度排序</p><hr></head><body>
    """
    all_news = game_news + ai_news
    for idx, news in enumerate(all_news, 1):
        html += f"""
        <div style="margin:15px 0;padding:10px;border-left:4px solid #0066cc;">
            <b>序号：{idx}</b><br>
            <b>类目：</b>{news['category']}<br>
            <b>标题：</b>【中文】{news['title_cn']}<br>
            <b>　　　</b>【英文】{news['title_en']}<br>
            <b>内容概要：</b>{news['summary']}<br>
            <b>信息源：</b>{news['source']}<br>
            <b>原文链接：</b><a href="{news['url']}">点击查看</a>
        </div><hr>
        """
    html += "</body></html>"
    return html

def send_email(html_content):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = RECEIVER
    msg["Subject"] = "📰 每日游戏&AI新闻日报"
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.163.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PWD)
        server.sendmail(EMAIL_USER, RECEIVER, msg.as_string())
    print("邮件发送成功！")

if __name__ == "__main__":
    game_news = fetch_news("game", GAME_QUERY)
    ai_news = fetch_news("ai", AI_QUERY)
    report = generate_daily_report(game_news, ai_news)
    send_email(report)

import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===================== 固定配置 =====================
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PWD = os.getenv("EMAIL_PWD")
RECEIVER = "killuailixiya@163.com"

NEWS_API_URL = "https://newsapi.org/v2/everything"
# 【优化1】更精准的搜索关键词
GAME_QUERY = "video game review OR new video game OR Metacritic OR pc gamer OR steam release OR playstation release OR xbox game review NOT football NOT soccer NOT basketball NOT sports"
AI_QUERY = "Generative AI OR deep learning OR OpenAI GPT OR Google Bard OR AI research OR transformer OR diffusion model OR AI innovation"

# 【优化2】补充更多媒体来源（值得信赖的站点）
AUTHORIZED_SOURCES = {
    "game": ["ign.com", "gamespot.com", "kotaku.com", "store.steampowered.com", "metacritic.com", "pcgamer.com", "polygon.com"],
    "ai": ["openai.com", "ai.google", "ai.meta.com", "technologyreview.com", "venturebeat.com", "wired.com", "arxiv.org"]
}
COUNT_PER_CATEGORY = 10
# ======================================================

def translate_text(text):
    """通用翻译函数（标题+概要都用这个）"""
    try:
        if not text:
            return "无概要"
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|zh-CN"
        res = requests.get(url, timeout=5).json()
        return res["responseData"]["translatedText"]
    except:
        return "翻译失败"

def fetch_news(category, query):
    params = {
        "q": query, "apiKey": NEWS_API_KEY, "language": "en",
        "sortBy": "relevance", "pageSize": 30  # 提高获取数量，再筛选前COUNT_PER_CATEGORY条
    }
    articles = requests.get(NEWS_API_URL, params=params, timeout=10).json().get("articles", [])
    if not articles:
        return []
    
    # 初始化推荐列表
    relevant_articles = []
    authorized = AUTHORIZED_SOURCES[category]
    
    for art in articles:
        # 过滤出来自可信站点的文章
        if any(domain in art["url"] for domain in authorized):
            relevant_articles.append(art)
    
    # 整理文章并按照授权来源优先展示，剔除无效数据
    final_news = relevant_articles[:COUNT_PER_CATEGORY]
    result = []
    
    for news in final_news:
        en_title = news["title"].strip()
        cn_title = translate_text(en_title)
        
        en_summary = news["description"] or "无概要"
        cn_summary = translate_text(en_summary)
        
        result.append({
            "category": "🎮 游戏资讯" if category == "game" else "🤖 AI 科技",
            "title_en": en_title, "title_cn": cn_title,
            "en_summary": en_summary,
            "cn_summary": cn_summary,
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
            <b>内容概要：</b>【中文】{news['cn_summary']}<br>
            <b>　　　　</b>【英文】{news['en_summary']}<br>
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

    # 使用正确的SMTP设置
    with smtplib.SMTP_SSL("smtp.163.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PWD)
        server.sendmail(EMAIL_USER, RECEIVER, msg.as_string())
    print("邮件发送成功！")

if __name__ == "__main__":
    game_news = fetch_news("game", GAME_QUERY)
    ai_news = fetch_news("ai", AI_QUERY)
    report = generate_daily_report(game_news, ai_news)
    send_email(report)

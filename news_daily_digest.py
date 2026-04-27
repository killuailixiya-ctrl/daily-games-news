import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 配置 RSS 源
RSS_FEEDS = {
    "games": [
        "https://www.gamespot.com/feeds/mashup/",
        "https://rss.gamer.com.tw/news.xml"
    ],
    "ai": [
        "https://openai.com/blog/rss/",
        "https://ai.googleblog.com/feeds/posts/default"
    ],
}

# 抓取RSS数据
def fetch_news(feed_urls, category):
    news_list = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            news = {
                "category": category,
                "title": entry.title,
                "summary": entry.summary,
                "link": entry.link,
                "published": entry.get("published", "N/A"),
            }
            news_list.append(news)
    return news_list

# 按重要性排序
def sort_news(news_list):
    return sorted(news_list, key=lambda x: x['published'], reverse=True)

# 生成Markdown日报
def generate_markdown(news_items):
    date_string = datetime.now().strftime("%Y-%m-%d")
    markdown = f"# 游戏与AI新闻日报 - {date_string}\n\n"
    for item in news_items:
        markdown += f"## {item['category']}\n\n"
        markdown += f"**标题**: {item['title']}\n\n"
        markdown += f"**内容概要**: {item['summary']}\n\n"
        markdown += f"**来源**: [原文链接]({item['link']})\n\n"
        markdown += "---\n\n"
    return markdown

# 发送邮件
def send_email(content, subject, recipient_email):
    # 邮件发送配置
    smtp_server = "smtp.163.com"
    smtp_port = 465
    sender_email = "your_email@163.com"
    sender_password = "your_app_password"

    # 设置邮件内容
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(content, 'plain'))

    # 发送邮件
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {e}")

# 主函数
def main():
    all_news = []
    for category, urls in RSS_FEEDS.items():
        news = fetch_news(urls, category)
        all_news.extend(news)
    
    sorted_news = sort_news(all_news)
    markdown_content = generate_markdown(sorted_news)
    
    # 将日报存储到本地文件
    with open("daily_news.md", "w", encoding="utf-8") as file:
        file.write(markdown_content)
    
    # 发送邮件
    subject = "每日游戏与AI新闻日报"
    recipient_email = "killuailixiya@163.com"
    send_email(markdown_content, subject, recipient_email)

if __name__ == "__main__":
    main()
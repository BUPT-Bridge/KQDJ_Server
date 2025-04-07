import requests
from bs4 import BeautifulSoup
import re

def get_wx_article_content(url: str) -> tuple:
    """
    获取微信文章内容并处理

    Args:
        url: 微信文章链接

    Returns:
        处理后的HTML内容
    """
    # 请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
    }

    # 获取页面内容
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"

    # 解析HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # 获取标题
    title_element = soup.find(
        "h1", {"class": "rich_media_title", "id": "activity-name"}
    )
    title = title_element.get_text().strip() if title_element else "无标题"

    # 获取文章内容div
    content_div = soup.find("div", {"class": "rich_media_content", "id": "js_content"})

    if not content_div:
        raise ValueError("未找到文章内容")
    # 只获取内部内容
    content_html = "".join(str(child) for child in content_div.children)
    
    # 替换图片链接
    html_template = re.sub(
        "data-src",
        "src",
        content_html,
    )
    # 对HTML内容中的图片链接进行替换
    html_template = re.sub(
        "https://mmbiz.qpic.cn",
        "https://images.weserv.nl/?url=https://mmbiz.qpic.cn",
        html_template,
    )
    return  title, html_template


if __name__ == "__main__":
    url = "https://mp.weixin.qq.com/s/M45pDQ4BU-0Zcpw-gBVuJg"

    html = get_wx_article_content(url)

    print(html["title"])
    print("=" * 20)
    print(html["title"])

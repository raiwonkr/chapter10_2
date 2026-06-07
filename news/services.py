import os
import re
import urllib.request
import urllib.parse
import json
from groq import Groq


def search_naver_news(keyword: str, display: int = 20) -> list[dict]:
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")

    encoded = urllib.parse.quote(keyword)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encoded}&display={display}&sort=sim"

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode("utf-8"))

    articles = []
    for item in data.get("items", []):
        articles.append({
            "title": _strip_html(item.get("title", "")),
            "description": _strip_html(item.get("description", "")),
            "link": item.get("link", ""),
            "pub_date": item.get("pubDate", ""),
        })
    return articles


def curate_articles(articles: list[dict], filter_prompt: str) -> list[dict]:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    articles_text = "\n\n".join(
        f"[{i+1}] 제목: {a['title']}\n내용: {a['description']}"
        for i, a in enumerate(articles)
    )

    prompt = f"""다음은 뉴스 기사 목록입니다.

{articles_text}

사용자의 필터링 기준: "{filter_prompt}"

위 기사 중 필터링 기준에 가장 잘 맞는 기사 3개를 선정하고,
아래 JSON 형식으로만 응답하세요. 다른 설명은 하지 마세요.

[
  {{
    "index": <원본 번호 (1부터 시작)>,
    "reason": "<선정 이유 한 문장>",
    "summary": "<기사 내용 요약 2~3문장>"
  }},
  ...
]"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.choices[0].message.content.strip()
    # 코드블록 제거
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    selected = json.loads(raw)

    result = []
    for item in selected:
        idx = item["index"] - 1
        article = articles[idx].copy()
        article["reason"] = item["reason"]
        article["summary"] = item["summary"]
        result.append(article)
    return result


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "")

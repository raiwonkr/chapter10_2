from django.shortcuts import render
from .services import search_naver_news, curate_articles


def index(request):
    context = {}

    if request.method == "POST":
        keyword = request.POST.get("keyword", "").strip()
        filter_prompt = request.POST.get("filter_prompt", "").strip()

        if keyword and filter_prompt:
            context["keyword"] = keyword
            context["filter_prompt"] = filter_prompt
            try:
                articles = search_naver_news(keyword, display=20)
                curated = curate_articles(articles, filter_prompt)
                context["articles"] = curated
            except Exception as e:
                context["error"] = str(e)

    return render(request, "news/index.html", context)

from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from .services import search_naver_news, curate_articles
from .models import SavedArticle


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


@require_POST
def save_article(request):
    SavedArticle.objects.create(
        title=request.POST.get("title", ""),
        reason=request.POST.get("reason", ""),
        summary=request.POST.get("summary", ""),
        link=request.POST.get("link", ""),
        pub_date=request.POST.get("pub_date", ""),
    )
    return redirect("history")


def history(request):
    articles = SavedArticle.objects.all()
    return render(request, "news/history.html", {"articles": articles})

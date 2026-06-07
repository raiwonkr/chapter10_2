from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .services import search_naver_news, curate_articles
from .models import SavedArticle


def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    error = None
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get("next", "index"))
        else:
            error = "아이디 또는 비밀번호가 올바르지 않습니다."

    return render(request, "news/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
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


@login_required
@require_POST
def save_article(request):
    SavedArticle.objects.create(
        user=request.user,
        title=request.POST.get("title", ""),
        reason=request.POST.get("reason", ""),
        summary=request.POST.get("summary", ""),
        link=request.POST.get("link", ""),
        pub_date=request.POST.get("pub_date", ""),
    )
    return redirect("history")


@login_required
def history(request):
    articles = SavedArticle.objects.filter(user=request.user)
    return render(request, "news/history.html", {"articles": articles})

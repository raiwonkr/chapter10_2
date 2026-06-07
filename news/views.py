from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .forms import StyledUserCreationForm
from django.views.decorators.http import require_POST
from .services import search_naver_news, curate_articles
from .models import SavedArticle


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_staff, login_url="login")(view_func)


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


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = StyledUserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("index")

    return render(request, "news/signup.html", {"form": form})


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


@staff_required
def dashboard(request):
    total_users = User.objects.count()
    total_articles = SavedArticle.objects.count()
    recent_articles = SavedArticle.objects.select_related("user").order_by("-saved_at")[:20]
    return render(request, "news/dashboard.html", {
        "total_users": total_users,
        "total_articles": total_articles,
        "recent_articles": recent_articles,
    })

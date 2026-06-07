from django.contrib import admin
from .models import SavedArticle


@admin.register(SavedArticle)
class SavedArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "saved_at")
    list_filter = ("user",)
    search_fields = ("title", "summary", "user__username")
    ordering = ("-saved_at",)
    readonly_fields = ("saved_at",)

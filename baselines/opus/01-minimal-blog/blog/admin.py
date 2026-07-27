from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "published_at", "is_published"]
    list_filter = ["published_at", "author"]
    search_fields = ["title", "body"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    autocomplete_fields = ["author"]

    @admin.display(boolean=True, description="Published")
    def is_published(self, obj: Post) -> bool:
        return obj.is_published

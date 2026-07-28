from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class PagesSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self) -> list[str]:
        return ["pages:index"]

    def location(self, item: str) -> str:
        return reverse(item)

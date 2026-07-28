"""Sitemaps wired into ``/sitemap.xml``."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from shop.models import Product


class StaticViewSitemap(Sitemap):
    """Hand-maintained list of the site's static pages."""

    priority = 1.0
    changefreq = "weekly"
    protocol = "https"

    def items(self) -> list[str]:
        return ["pages:index"]

    def location(self, item: str) -> str:
        return reverse(item)


class ProductSitemap(Sitemap):
    priority = 0.7
    changefreq = "daily"
    protocol = "https"

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj: Product):
        return obj.updated_at


SITEMAPS = {
    "static": StaticViewSitemap,
    "products": ProductSitemap,
}

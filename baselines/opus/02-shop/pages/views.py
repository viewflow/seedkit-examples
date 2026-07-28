from typing import Any

from django.views.generic import TemplateView

from shop.models import Product


class IndexView(TemplateView):
    """The shop front page."""

    template_name = "pages/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Welcome"
        context["products"] = Product.objects.filter(is_active=True)[:6]
        return context

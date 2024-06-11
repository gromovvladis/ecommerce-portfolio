from django.apps import apps
from django.urls import include, path, re_path


from oscar.core.application import OscarConfig
from oscar.core.loading import get_class


class CatalogueOnlyConfig(OscarConfig):
    label = "catalogue"
    name = "oscar.apps.catalogue"
    verbose_name = "Каталог"

    namespace = "catalogue"

    # pylint: disable=attribute-defined-outside-init, unused-import
    def ready(self):
        from . import receivers

        super().ready()

        self.detail_view = get_class("catalogue.views", "ProductDetailView")
        self.category_view = get_class("catalogue.views", "ProductCategoryView")
        self.range_view = get_class("offer.views", "RangeDetailView")

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            re_path(
                r"^(?P<category_slug>[\w-]+(/[\w-]+)*)/(?P<product_slug>[\w-]*)/$",
                self.detail_view.as_view(),
                name="detail",
            ),
            re_path(
                r"^(?P<category_slug>[\w-]+(/[\w-]+)*)/$",
                self.category_view.as_view(),
                name="category",
            ),
            re_path(
                r"^ranges/(?P<slug>[\w-]+)/$", self.range_view.as_view(), name="range"
            ),
        ]
        return self.post_process_urls(urls)


class CatalogueReviewsOnlyConfig(OscarConfig):
    label = "catalogue"
    name = "oscar.apps.catalogue"
    verbose_name = "Каталог Отзывы"

    # pylint: disable=attribute-defined-outside-init, unused-import
    def ready(self):
        from . import receivers

        super().ready()

        self.reviews_app = apps.get_app_config("reviews")

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            re_path(
                r"^(?P<product_slug>[\w-]*)_(?P<product_pk>\d+)/reviews/",
                include(self.reviews_app.urls[0]),
            ),
        ]
        return self.post_process_urls(urls)


class CatalogueConfig(CatalogueOnlyConfig, CatalogueReviewsOnlyConfig):
    """
    Composite class combining Products with Reviews
    """

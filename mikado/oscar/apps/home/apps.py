from django.urls import path, re_path
from oscar.core.application import OscarConfig
from oscar.core.loading import get_class


class HomeConfig(OscarConfig):
    label = "home"
    name = "oscar.apps.home"
    verbose_name = "Домашнаяя страница"

    namespace = "home"

    # pylint: disable=attribute-defined-outside-init, unused-import
    def ready(self):
        super().ready()

        self.home_view = get_class("home.views", "HomeView")
        self.actions_view = get_class("home.views", "ActionsView")
        self.action_detail_view = get_class("home.views", "ActionDetailView")
        self.promocat_detail_view = get_class("home.views", "PromoCatDetailView")
        self.cookies_view = get_class("home.views", "GetCookiesView")

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            path("", self.home_view.as_view(), name="index"),
            path("actions/", self.actions_view.as_view(), name="actions"),
            re_path(
                r"^actions/(?P<action_slug>[\w-]+(/[\w-]+)*)/$",
                self.action_detail_view.as_view(),
                name="action-detail",
            ),
            re_path(
                r"^promo/(?P<action_slug>[\w-]+(/[\w-]+)*)/$",
                self.promocat_detail_view.as_view(),
                name="promo-detail",
            ),
            path("api/cookies/", self.cookies_view.as_view(), name="cookies"),
        ]
        return self.post_process_urls(urls)

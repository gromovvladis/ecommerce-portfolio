import logging
from functools import lru_cache

from core.application import DashboardConfig
from core.views.decorators import check_permissions
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.urls import resolve, reverse

logger = logging.getLogger("dashboard")


class Node(object):
    """
    A node in the dashboard navigation menu
    """

    def __init__(
        self,
        label,
        notif=None,
        url_name=None,
        url_args=None,
        url_kwargs=None,
        access_fn=None,
        icon=None,
    ):
        self.label = label
        self.notif = notif
        self.icon = icon
        self.url_name = url_name
        self.url_args = url_args
        self.url_kwargs = url_kwargs
        self.access_fn = access_fn
        self.children = []
        self.paths = []

    @property
    def is_heading(self):
        return self.url_name is None

    @property
    def url(self):
        return reverse(self.url_name, args=self.url_args, kwargs=self.url_kwargs)

    def add_child(self, node):
        self.children.append(node)

    def add_path(self, path):
        self.paths.append(path)

    def is_visible(self, user):
        return self.access_fn is None or self.access_fn(
            user, self.url_name, self.url_args, self.url_kwargs
        )

    def filter(self, user):
        if not self.is_visible(user):
            return None

        node = Node(
            label=self.label,
            url_name=self.url_name,
            url_args=self.url_args,
            url_kwargs=self.url_kwargs,
            access_fn=self.access_fn,
            icon=self.icon,
            notif=self.notif,
        )

        # Добавление видимых дочерних элементов
        for child in filter(lambda child: child.is_visible(user), self.children):
            node.add_child(child)

        # Добавление путей
        for path in self.paths:
            node.add_path(path)

        return node

    def has_children(self):
        return len(self.children) > 0


@lru_cache(maxsize=1)
def _dashboard_url_names_to_config():
    dashboard_configs = (
        config
        for config in apps.get_app_configs()
        if isinstance(config, DashboardConfig)
    )
    urls_to_config = {}
    for config in dashboard_configs:
        for url in config.urls[0]:
            # includes() don't have a name attribute
            # We skipped them because they come from other AppConfigs
            name = getattr(url, "name", None)
            if not name:
                continue

            if name in urls_to_config:
                if urls_to_config[name] != config:
                    raise ImproperlyConfigured(
                        "'{}' exists in both {} and {}!".format(
                            name, config, urls_to_config[name]
                        )
                    )

            urls_to_config[name] = config
    return urls_to_config


def default_access_fn(user, url_name, url_args=None, url_kwargs=None):
    """
    Given a user and a url_name, this function assesses whether the
    user has the right to access the URL.
    Once the permissions for the view are known, the access logic used
    by the dashboard decorator is evaluated
    """
    if url_name is None:  # it's a heading
        return True

    url = reverse(url_name, args=url_args, kwargs=url_kwargs)
    url_match = resolve(url)
    url_name = url_match.url_name
    app_config_instance = _dashboard_url_names_to_config()[url_name]
    permissions = app_config_instance.get_permissions(url_name)

    return check_permissions(user, permissions)

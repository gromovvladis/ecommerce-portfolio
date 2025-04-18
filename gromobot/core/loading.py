import sys
import traceback
import warnings
from functools import lru_cache
from importlib import import_module

from core.exceptions import AppNotFoundError, ClassNotFoundError
from django.apps import apps
from django.apps.config import MODELS_MODULE_NAME
from django.conf import settings
from django.core.exceptions import AppRegistryNotReady
from django.utils.module_loading import import_string

# To preserve backwards compatibility of loading classes which moved
# from one Oscar module to another, we look into the dictionary below
# for the moved items during loading.
MOVED_MODELS = {}


def get_class(module_label, classname, module_prefix="apps"):
    """
    Dynamically import a single class from the given module.

    This is a simple wrapper around `get_classes` for the case of loading a
    single class.

    Args:
        module_label (str): Module label comprising the app label and the
            module name, separated by a dot.  For example, 'catalogue.forms'.
        classname (str): Name of the class to be imported.

    Returns:
        The requested class object or `None` if it can't be found
    """
    return get_classes(module_label, [classname], module_prefix)[0]


@lru_cache(maxsize=100)
def get_class_loader():
    return import_string(settings.DYNAMIC_CLASS_LOADER)


def get_classes(module_label, classnames, module_prefix="apps"):
    class_loader = get_class_loader()
    return class_loader(module_label, classnames, module_prefix)


def default_class_loader(module_label, classnames, module_prefix):
    """
    Dynamically import a list of classes from the given module.

    This works by looking up a matching app from the app registry,
    against the passed module label.  If the requested class can't be found in
    the matching module, then we attempt to import it from the corresponding
    core app.

    This is very similar to ``django.db.models.get_model`` function for
    dynamically loading models.  This function is more general though as it can
    load any class from the matching app, not just a model.

    Args:
        module_label (str): Module label comprising the app label and the
            module name, separated by a dot.  For example, 'catalogue.forms'.
        classname (str): Name of the class to be imported.

    Returns:
        The requested class object or ``None`` if it can't be found

    Examples:

        Load a single class:

        >>> get_class('dashboard.catalogue.forms', 'ProductForm')
        apps.dashboard.catalogue.forms.ProductForm

        Load a list of classes:

        >>> get_classes('dashboard.catalogue.forms',
        ...             ['ProductForm', 'StockRecordForm'])
        [apps.dashboard.catalogue.forms.ProductForm,
         apps.dashboard.catalogue.forms.StockRecordForm]

    Raises:

        AppNotFoundError: If no app is found in ``INSTALLED_APPS`` that matches
            the passed module label.

        ImportError: If the attempted import of a class raises an
            ``ImportError``, it is re-raised
    """

    if "." not in module_label:
        # Importing from top-level modules is not supported, e.g.
        # get_class('shipping', 'Scale'). That should be easy to fix,
        # but @maikhoepfel had a stab and could not get it working reliably.
        # Overridable classes in a __init__.py might not be a good idea anyway.
        raise ValueError("Importing from top-level modules is not supported")

    # import from Oscar package (should succeed in most cases)
    # e.g. 'oscar.apps.dashboard.catalogue.forms'
    oscar_module_label = "%s.%s" % (module_prefix, module_label)
    oscar_module = _import_module(oscar_module_label, classnames)

    # returns e.g. 'oscar.apps.dashboard.catalogue',
    # 'yourproject.apps.dashboard.catalogue' or 'dashboard.catalogue',
    # depending on what is set in INSTALLED_APPS
    app_name = _find_registered_app_name(module_label)
    if app_name.startswith("%s." % module_prefix):
        # The entry is obviously an Oscar one, we don't import again
        local_module = None
    else:
        # Attempt to import the classes from the local module
        # e.g. 'yourproject.dashboard.catalogue.forms'
        local_module_label = ".".join(app_name.split(".") + module_label.split(".")[1:])
        local_module = _import_module(local_module_label, classnames)

    if oscar_module is local_module is None:
        # This intentionally doesn't raise an ImportError, because ImportError
        # can get masked in complex circular import scenarios.
        raise ModuleNotFoundError(
            "The module with label '%s' could not be imported. This either"
            "means that it indeed does not exist, or you might have a problem"
            " with a circular import." % module_label
        )

    # return imported classes, giving preference to ones from the local package
    return _pluck_classes([local_module, oscar_module], classnames)


def _import_module(module_label, classnames):
    """
    Imports the module with the given name.
    Returns None if the module doesn't exist, but propagates any import errors.
    """
    try:
        return __import__(module_label, fromlist=classnames)
    except ImportError:
        # There are 2 reasons why there could be an ImportError:
        #
        #  1. Module does not exist. In that case, we ignore the import and
        #     return None
        #  2. Module exists but another ImportError occurred when trying to
        #     import the module. In that case, it is important to propagate the
        #     error.
        #
        # ImportError does not provide easy way to distinguish those two cases.
        # Fortunately, the traceback of the ImportError starts at __import__
        # statement. If the traceback has more than one frame, it means that
        # application was found and ImportError originates within the local app
        __, __, exc_traceback = sys.exc_info()
        frames = traceback.extract_tb(exc_traceback)
        if len(frames) > 1:
            raise


def _pluck_classes(modules, classnames):
    """
    Gets a list of class names and a list of modules to pick from.
    For each class name, will return the class from the first module that has a
    matching class.
    """
    klasses = []
    for classname in classnames:
        klass = None
        for module in modules:
            if hasattr(module, classname):
                klass = getattr(module, classname)
                break
        if not klass:
            packages = [m.__name__ for m in modules if m is not None]
            raise ClassNotFoundError(
                "No class '%s' found in %s" % (classname, ", ".join(packages))
            )
        klasses.append(klass)
    return klasses


def _find_registered_app_name(module_label):
    """
    Given a module label, finds the name of the matching Oscar app from the
    Django app registry.
    """
    from core.application import Config

    app_label = module_label.split(".")[0]
    try:
        app_config = apps.get_app_config(app_label)
    except LookupError:
        raise AppNotFoundError("Couldn't find an app to import %s from" % module_label)
    if not isinstance(app_config, Config):
        raise AppNotFoundError(
            "Couldn't find an Oscar app to import %s from" % module_label
        )
    return app_config.name


def get_profile_class():
    """
    Return the profile model class
    """
    # The AUTH_PROFILE_MODULE setting was deprecated in Django 1.5, but it
    # makes sense for Oscar to continue to use it. Projects built on Django
    # 1.4 are likely to have used a profile class and it's very difficult to
    # upgrade to a single user model. Hence, we should continue to support
    # having a separate profile class even if Django doesn't.
    setting = getattr(settings, "AUTH_PROFILE_MODULE", None)
    if setting is None:
        return None
    app_label, model_name = settings.AUTH_PROFILE_MODULE.split(".")
    return get_model(app_label, model_name)


def get_model(app_label, model_name):
    """
    Fetches a Django model using the app registry.

    This doesn't require that an app with the given app label exists,
    which makes it safe to call when the registry is being populated.
    All other methods to access models might raise an exception about the
    registry not being ready yet.
    Raises LookupError if model isn't found.
    """
    oscar_moved_model = MOVED_MODELS.get(app_label, None)
    if oscar_moved_model:
        if model_name.lower() in oscar_moved_model[1]:
            original_app_label = app_label
            app_label = oscar_moved_model[0]
            warnings.warn(
                "Model %s has recently moved from %s to the application %s, "
                "please update your imports."
                % (model_name, original_app_label, app_label),
                DeprecationWarning,
                stacklevel=2,
            )
    try:
        return apps.get_model(app_label, model_name)
    except AppRegistryNotReady:
        if apps.apps_ready and not apps.models_ready:
            # If this function is called while `apps.populate()` is
            # loading models, ensure that the module that defines the
            # target model has been imported and try looking the model up
            # in the app registry. This effectively emulates
            # `from path.to.app.models import Model` where we use
            # `Model = get_model('app', 'Model')` instead.
            app_config = apps.get_app_config(app_label)
            # `app_config.import_models()` cannot be used here because it
            # would interfere with `apps.populate()`.
            import_module("%s.%s" % (app_config.name, MODELS_MODULE_NAME))
            # In order to account for case-insensitivity of model_name,
            # look up the model through a private API of the app registry.
            return apps.get_registered_model(app_label, model_name)
        else:
            # This must be a different case (e.g. the model really doesn't
            # exist). We just re-raise the exception.
            raise


def is_model_registered(app_label, model_name):
    """
    Checks whether a given model is registered. This is used to only
    register Oscar models if they aren't overridden by a forked app.
    """
    try:
        apps.get_registered_model(app_label, model_name)
    except LookupError:
        return False
    else:
        return True


@lru_cache(maxsize=128)
def cached_import_string(path):
    return import_string(path)

"""
dj-stripe - Django + Stripe Made Easy
"""
import pkg_resources
from django.apps import AppConfig

# from django.db.models.signals import post_migrate

__version__ = pkg_resources.get_distribution("dj-stripe").version


# todo refactor this pr into 2 PRs, a separate one for creating apikey instances and the current one only for fixing djstripe_owner_account field
# todo add a test
# def get_or_create_stripe_keys(**kwargs):
#     """Create Stripe public, secret, and restricted keys for both the modes if provided. If they don't exist already"""
#     from django.conf import settings

#     from djstripe.models import APIKey

#     dict = {
#         "STRIPE_SECRET_KEY": getattr(settings, "STRIPE_SECRET_KEY", ""),
#         "STRIPE_TEST_SECRET_KEY": getattr(settings, "STRIPE_TEST_SECRET_KEY", ""),
#         "STRIPE_LIVE_SECRET_KEY": getattr(settings, "STRIPE_LIVE_SECRET_KEY", ""),
#         "STRIPE_PUBLIC_KEY": getattr(settings, "STRIPE_PUBLIC_KEY", ""),
#         "STRIPE_LIVE_PUBLIC_KEY": getattr(settings, "STRIPE_LIVE_PUBLIC_KEY", ""),
#         "STRIPE_TEST_PUBLIC_KEY": getattr(settings, "STRIPE_TEST_PUBLIC_KEY", ""),
#     }

#     for value in dict.values():
#         if value:
#             APIKey.objects.get_or_create_by_api_key(value)


class DjstripeAppConfig(AppConfig):
    """
    An AppConfig for dj-stripe which loads system checks
    and event handlers once Django is ready.
    """

    name = "djstripe"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        import stripe

        from . import (  # noqa: Register the checks and event handlers
            checks,
            event_handlers,
        )

        # Set app info
        # https://stripe.com/docs/building-plugins#setappinfo
        stripe.set_app_info(
            "dj-stripe",
            version=__version__,
            url="https://github.com/dj-stripe/dj-stripe",
        )

        # # todo import and run this methid somewhere else as doing it in ready is not good pratice.
        # # create stripe keys if they don't exist already
        # # we do not use the post_migrate signal because the user can change the keys whenever they want.
        # post_migrate.connect(get_or_create_stripe_keys, sender=self)
        # print(self.get_model("APIKey"))
        # # todo add a method to create the keys in case migrations are not run, need to check that the apikey model exists for that.

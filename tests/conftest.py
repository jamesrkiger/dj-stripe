import pytest


@pytest.fixture(autouse=True)
def override_stripe_keys(settings):
    settings.STRIPE_TEST_PUBLIC_KEY = ""
    settings.STRIPE_TEST_SECRET_KEY = ""
    settings.STRIPE_TEST_SECRET_KEY = ""

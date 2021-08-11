"""
dj-stripe ApplicationFee model tests
"""
from copy import deepcopy
from unittest.mock import patch

import pytest
from django.test.testcases import TestCase

from djstripe.models import ApplicationFee

from . import (
    FAKE_APPLICATION_FEE,
    FAKE_BALANCE_TRANSACTION,
    FAKE_CARD_AS_PAYMENT_METHOD,
    FAKE_CHARGE_APPLICATION_FEE,
    FAKE_CUSTOMER,
    FAKE_INVOICE,
    FAKE_PAYMENT_INTENT_I,
    FAKE_PRODUCT,
    FAKE_STANDARD_ACCOUNT,
    FAKE_SUBSCRIPTION,
    IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
    AssertStripeFksMixin,
)

pytestmark = pytest.mark.django_db


class TestApplicationFee(AssertStripeFksMixin, TestCase):
    @patch(
        "stripe.Customer.retrieve", return_value=deepcopy(FAKE_CUSTOMER), autospec=True
    )
    @patch(
        "stripe.Account.retrieve",
        return_value=deepcopy(FAKE_STANDARD_ACCOUNT),
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
    )
    @patch(
        "stripe.BalanceTransaction.retrieve",
        return_value=deepcopy(FAKE_BALANCE_TRANSACTION),
        autospec=True,
    )
    @patch(
        "stripe.Charge.retrieve",
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
        return_value=deepcopy(FAKE_CHARGE_APPLICATION_FEE),
    )
    @patch(
        "stripe.Invoice.retrieve", return_value=deepcopy(FAKE_INVOICE), autospec=True
    )
    @patch(
        "stripe.PaymentIntent.retrieve",
        return_value=deepcopy(FAKE_PAYMENT_INTENT_I),
        autospec=True,
    )
    @patch(
        "stripe.PaymentMethod.retrieve",
        return_value=deepcopy(FAKE_CARD_AS_PAYMENT_METHOD),
        autospec=True,
    )
    @patch(
        "stripe.Product.retrieve", return_value=deepcopy(FAKE_PRODUCT), autospec=True
    )
    @patch(
        "stripe.Subscription.retrieve",
        return_value=deepcopy(FAKE_SUBSCRIPTION),
        autospec=True,
    )
    @patch(
        "stripe.ApplicationFee.retrieve",
        return_value=deepcopy(FAKE_APPLICATION_FEE),
        autospec=True,
    )
    def test_sync_from_stripe_data(
        self,
        application_fee_retrieve_mock,
        subscription_retrieve_mock,
        product_retrieve_mock,
        payment_method_retrieve_mock,
        payment_intent_retrieve_mock,
        invoice_retrieve_mock,
        charge_retrieve_mock,
        balance_transaction_retrieve_mock,
        account_retrieve_mock,
        customer_retrieve_mock,
    ):

        application_fee = ApplicationFee.sync_from_stripe_data(
            deepcopy(FAKE_APPLICATION_FEE)
        )

        balance_transaction_retrieve_mock.assert_not_called()
        charge_retrieve_mock.assert_not_called()
        application_fee_retrieve_mock.assert_not_called()

        assert (
            application_fee.balance_transaction.id
            == FAKE_APPLICATION_FEE["balance_transaction"]["id"]
        )
        assert application_fee.charge.id == FAKE_APPLICATION_FEE["charge"]["id"]
        assert application_fee.account.id == FAKE_APPLICATION_FEE["account"]["id"]

        self.assert_fks(
            application_fee,
            expected_blank_fks={
                "djstripe.Charge.dispute",
                "djstripe.Charge.latest_upcominginvoice (related name)",
                "djstripe.Charge.on_behalf_of",
                "djstripe.Charge.source_transfer",
                "djstripe.Charge.transfer",
                "djstripe.Customer.coupon",
                "djstripe.Customer.default_payment_method",
                "djstripe.Customer.subscriber",
                "djstripe.Invoice.default_payment_method",
                "djstripe.Invoice.default_source",
                "djstripe.PaymentIntent.on_behalf_of",
                "djstripe.PaymentIntent.payment_method",
                "djstripe.PaymentIntent.upcominginvoice (related name)",
                "djstripe.Subscription.default_payment_method",
                "djstripe.Subscription.default_source",
                "djstripe.Subscription.pending_setup_intent",
                "djstripe.Subscription.schedule",
            },
        )

    @patch(
        "stripe.Customer.retrieve", return_value=deepcopy(FAKE_CUSTOMER), autospec=True
    )
    @patch(
        "stripe.Account.retrieve",
        return_value=deepcopy(FAKE_STANDARD_ACCOUNT),
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
    )
    @patch(
        "stripe.BalanceTransaction.retrieve",
        return_value=deepcopy(FAKE_BALANCE_TRANSACTION),
        autospec=True,
    )
    @patch(
        "stripe.Charge.retrieve",
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
        return_value=deepcopy(FAKE_CHARGE_APPLICATION_FEE),
    )
    @patch(
        "stripe.Invoice.retrieve", return_value=deepcopy(FAKE_INVOICE), autospec=True
    )
    @patch(
        "stripe.PaymentIntent.retrieve",
        return_value=deepcopy(FAKE_PAYMENT_INTENT_I),
        autospec=True,
    )
    @patch(
        "stripe.PaymentMethod.retrieve",
        return_value=deepcopy(FAKE_CARD_AS_PAYMENT_METHOD),
        autospec=True,
    )
    @patch(
        "stripe.Product.retrieve", return_value=deepcopy(FAKE_PRODUCT), autospec=True
    )
    @patch(
        "stripe.Subscription.retrieve",
        return_value=deepcopy(FAKE_SUBSCRIPTION),
        autospec=True,
    )
    @patch(
        "stripe.ApplicationFee.retrieve",
        return_value=deepcopy(FAKE_APPLICATION_FEE),
        autospec=True,
    )
    def test___str__(
        self,
        application_fee_retrieve_mock,
        subscription_retrieve_mock,
        product_retrieve_mock,
        payment_method_retrieve_mock,
        payment_intent_retrieve_mock,
        invoice_retrieve_mock,
        charge_retrieve_mock,
        balance_transaction_retrieve_mock,
        account_retrieve_mock,
        customer_retrieve_mock,
    ):

        application_fee = ApplicationFee.sync_from_stripe_data(
            deepcopy(FAKE_APPLICATION_FEE)
        )

        assert f"<id={application_fee.id}>" == str(application_fee)

"""
dj-stripe ApplicationFeeRefund model tests
"""
from copy import deepcopy
from unittest.mock import PropertyMock, patch

import pytest
from django.test.testcases import TestCase

from djstripe.models import ApplicationFeeRefund
from djstripe.settings import djstripe_settings

from . import (
    FAKE_APPLICATION_FEE_REFUND,
    FAKE_BALANCE_TRANSACTION_REFUND,
    FAKE_CARD_AS_PAYMENT_METHOD,
    FAKE_CHARGE_REFUNDED,
    FAKE_CUSTOMER,
    FAKE_INVOICE,
    FAKE_PAYMENT_INTENT_I,
    FAKE_PLAN,
    FAKE_PRODUCT,
    FAKE_STANDARD_ACCOUNT,
    FAKE_SUBSCRIPTION,
    IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
    AssertStripeFksMixin,
)

pytestmark = pytest.mark.django_db


class TestApplicationFeeRefund(AssertStripeFksMixin, TestCase):
    @patch(
        "stripe.Account.retrieve",
        return_value=deepcopy(FAKE_STANDARD_ACCOUNT),
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
    )
    @patch(
        "stripe.Invoice.retrieve",
        return_value=deepcopy(FAKE_INVOICE),
        autospec=True,
    )
    @patch(
        "stripe.Customer.retrieve",
        return_value=deepcopy(FAKE_CUSTOMER),
        autospec=True,
    )
    @patch(
        "stripe.PaymentIntent.retrieve",
        autospec=True,
        return_value=deepcopy(FAKE_PAYMENT_INTENT_I),
    )
    @patch(
        "stripe.PaymentMethod.retrieve",
        return_value=deepcopy(FAKE_CARD_AS_PAYMENT_METHOD),
        autospec=True,
    )
    @patch(
        "stripe.Charge.retrieve",
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
        return_value=deepcopy(FAKE_CHARGE_REFUNDED),
    )
    @patch("stripe.Plan.retrieve", return_value=deepcopy(FAKE_PLAN), autospec=True)
    @patch(
        "stripe.Product.retrieve", return_value=deepcopy(FAKE_PRODUCT), autospec=True
    )
    @patch(
        "stripe.Subscription.retrieve",
        return_value=deepcopy(FAKE_SUBSCRIPTION),
        autospec=True,
    )
    @patch(
        "stripe.BalanceTransaction.retrieve",
        return_value=deepcopy(FAKE_BALANCE_TRANSACTION_REFUND),
        autospec=True,
    )
    @patch(
        "stripe.ApplicationFee.retrieve_refund",
        autospec=True,
        return_value=deepcopy(FAKE_APPLICATION_FEE_REFUND),
    )
    def test___str__(
        self,
        application_fee_refund_retrieve_mock,
        balance_transaction_retrieve_mock,
        subscription_retrieve_mock,
        product_retrieve_mock,
        plan_retrieve_mock,
        charge_retrieve_mock,
        paymentmethod_card_retrieve_mock,
        payment_intent_retrieve_mock,
        customer_retrieve_mock,
        invoice_retrieve_mock,
        account_retrieve_mock,
    ):

        application_fee_refund = ApplicationFeeRefund.sync_from_stripe_data(
            deepcopy(FAKE_APPLICATION_FEE_REFUND)
        )
        assert f"<id={application_fee_refund.id}>" == str(application_fee_refund)

    @patch(
        "stripe.Account.retrieve",
        return_value=deepcopy(FAKE_STANDARD_ACCOUNT),
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
    )
    @patch(
        "stripe.Invoice.retrieve",
        return_value=deepcopy(FAKE_INVOICE),
        autospec=True,
    )
    @patch(
        "stripe.Customer.retrieve",
        return_value=deepcopy(FAKE_CUSTOMER),
        autospec=True,
    )
    @patch(
        "stripe.PaymentIntent.retrieve",
        autospec=True,
        return_value=deepcopy(FAKE_PAYMENT_INTENT_I),
    )
    @patch(
        "stripe.PaymentMethod.retrieve",
        return_value=deepcopy(FAKE_CARD_AS_PAYMENT_METHOD),
        autospec=True,
    )
    @patch(
        "stripe.Charge.retrieve",
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
        return_value=deepcopy(FAKE_CHARGE_REFUNDED),
    )
    @patch("stripe.Plan.retrieve", return_value=deepcopy(FAKE_PLAN), autospec=True)
    @patch(
        "stripe.Product.retrieve", return_value=deepcopy(FAKE_PRODUCT), autospec=True
    )
    @patch(
        "stripe.Subscription.retrieve",
        return_value=deepcopy(FAKE_SUBSCRIPTION),
        autospec=True,
    )
    @patch(
        "stripe.BalanceTransaction.retrieve",
        return_value=deepcopy(FAKE_BALANCE_TRANSACTION_REFUND),
        autospec=True,
    )
    @patch(
        "stripe.ApplicationFee.retrieve_refund",
        autospec=True,
        return_value=deepcopy(FAKE_APPLICATION_FEE_REFUND),
    )
    def test_sync_from_stripe_data(
        self,
        application_fee_refund_retrieve_mock,
        balance_transaction_retrieve_mock,
        subscription_retrieve_mock,
        product_retrieve_mock,
        plan_retrieve_mock,
        charge_retrieve_mock,
        paymentmethod_card_retrieve_mock,
        payment_intent_retrieve_mock,
        customer_retrieve_mock,
        invoice_retrieve_mock,
        account_retrieve_mock,
    ):

        application_fee_refund = ApplicationFeeRefund.sync_from_stripe_data(
            deepcopy(FAKE_APPLICATION_FEE_REFUND)
        )
        balance_transaction_retrieve_mock.assert_not_called()
        charge_retrieve_mock.assert_not_called()
        application_fee_refund_retrieve_mock.assert_not_called()

        assert (
            application_fee_refund.balance_transaction.id
            == FAKE_APPLICATION_FEE_REFUND["balance_transaction"]["id"]
        )

        assert application_fee_refund.fee.id == FAKE_APPLICATION_FEE_REFUND["fee"]["id"]

        self.assert_fks(
            application_fee_refund,
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
        "stripe.Account.retrieve",
        return_value=deepcopy(FAKE_STANDARD_ACCOUNT),
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
    )
    @patch(
        "stripe.Invoice.retrieve",
        return_value=deepcopy(FAKE_INVOICE),
        autospec=True,
    )
    @patch(
        "stripe.Customer.retrieve",
        return_value=deepcopy(FAKE_CUSTOMER),
        autospec=True,
    )
    @patch(
        "stripe.PaymentIntent.retrieve",
        autospec=True,
        return_value=deepcopy(FAKE_PAYMENT_INTENT_I),
    )
    @patch(
        "stripe.PaymentMethod.retrieve",
        return_value=deepcopy(FAKE_CARD_AS_PAYMENT_METHOD),
        autospec=True,
    )
    @patch(
        "stripe.Charge.retrieve",
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
        return_value=deepcopy(FAKE_CHARGE_REFUNDED),
    )
    @patch("stripe.Plan.retrieve", return_value=deepcopy(FAKE_PLAN), autospec=True)
    @patch(
        "stripe.Product.retrieve", return_value=deepcopy(FAKE_PRODUCT), autospec=True
    )
    @patch(
        "stripe.Subscription.retrieve",
        return_value=deepcopy(FAKE_SUBSCRIPTION),
        autospec=True,
    )
    @patch(
        "stripe.BalanceTransaction.retrieve",
        return_value=deepcopy(FAKE_BALANCE_TRANSACTION_REFUND),
        autospec=True,
    )
    @patch(
        "stripe.ApplicationFee.retrieve_refund",
        autospec=True,
        return_value=deepcopy(FAKE_APPLICATION_FEE_REFUND),
    )
    def test_api_retrieve(
        self,
        application_fee_refund_retrieve_mock,
        balance_transaction_retrieve_mock,
        subscription_retrieve_mock,
        product_retrieve_mock,
        plan_retrieve_mock,
        charge_retrieve_mock,
        paymentmethod_card_retrieve_mock,
        payment_intent_retrieve_mock,
        customer_retrieve_mock,
        invoice_retrieve_mock,
        account_retrieve_mock,
    ):

        application_fee_refund = ApplicationFeeRefund.sync_from_stripe_data(
            deepcopy(FAKE_APPLICATION_FEE_REFUND)
        )

        application_fee_refund.api_retrieve()

        application_fee_refund_retrieve_mock.assert_called_once_with(
            id=FAKE_APPLICATION_FEE_REFUND["fee"]["id"],
            nested_id=FAKE_APPLICATION_FEE_REFUND["id"],
            api_key=djstripe_settings.STRIPE_SECRET_KEY,
            expand=["balance_transaction", "fee"],
            stripe_account=None,
        )

    # we are returning any value for the ApplicationFee.objects.get as we only need to avoid the ApplicationFee.DoesNotExist error
    @patch(
        "djstripe.models.connect.ApplicationFee.objects.get",
        return_value=5,
    )
    @patch(
        "stripe.ApplicationFee.create_refund",
        autospec=True,
        return_value=deepcopy(FAKE_APPLICATION_FEE_REFUND),
    )
    def test__api_create(
        self,
        application_fee_refund_create_mock,
        application_fee_get_mock,
    ):

        ApplicationFeeRefund._api_create(id=FAKE_APPLICATION_FEE_REFUND["fee"]["id"])

        application_fee_refund_create_mock.assert_called_once_with(
            id=FAKE_APPLICATION_FEE_REFUND["fee"]["id"],
            api_key=djstripe_settings.STRIPE_SECRET_KEY,
        )

    @patch(
        "stripe.ApplicationFee.list_refunds",
        autospec=True,
    )
    def test_api_list(
        self,
        application_fee_refund_list_mock,
    ):
        p = PropertyMock(return_value=deepcopy(FAKE_APPLICATION_FEE_REFUND))
        type(application_fee_refund_list_mock).auto_paging_iter = p

        ApplicationFeeRefund.api_list(id=FAKE_APPLICATION_FEE_REFUND["fee"]["id"])

        application_fee_refund_list_mock.assert_called_once_with(
            id=FAKE_APPLICATION_FEE_REFUND["fee"]["id"],
            api_key=djstripe_settings.STRIPE_SECRET_KEY,
        )

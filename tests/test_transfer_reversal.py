"""
dj-stripe TransferReversal model tests
"""
from copy import deepcopy
from unittest.mock import PropertyMock, patch

import pytest
from django.test.testcases import TestCase

from djstripe.models import TransferReversal
from djstripe.settings import djstripe_settings

from . import (
    FAKE_BALANCE_TRANSACTION_II,
    FAKE_STANDARD_ACCOUNT,
    FAKE_TRANSFER,
    FAKE_TRANSFER_REVERSAL,
    IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
    AssertStripeFksMixin,
)

pytestmark = pytest.mark.django_db


class TestTransferReversalStr:
    @patch(
        "stripe.Account.retrieve",
        return_value=deepcopy(FAKE_STANDARD_ACCOUNT),
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
    )
    @patch(
        "stripe.BalanceTransaction.retrieve",
        return_value=deepcopy(FAKE_BALANCE_TRANSACTION_II),
        autospec=True,
    )
    @patch(
        "stripe.Transfer.retrieve_reversal",
        autospec=True,
        return_value=deepcopy(FAKE_TRANSFER_REVERSAL),
    )
    def test___str__(
        self,
        transfer_reversal_retrieve_mock,
        balance_transaction_retrieve_mock,
        account_retrieve_mock,
    ):

        transfer_reversal = TransferReversal.sync_from_stripe_data(
            deepcopy(FAKE_TRANSFER_REVERSAL)
        )
        assert str(f"{transfer_reversal.transfer}") == str(transfer_reversal)


class TestTransfer(AssertStripeFksMixin, TestCase):
    @patch(
        "stripe.Account.retrieve",
        return_value=deepcopy(FAKE_STANDARD_ACCOUNT),
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
    )
    @patch(
        "stripe.BalanceTransaction.retrieve",
        return_value=deepcopy(FAKE_BALANCE_TRANSACTION_II),
        autospec=True,
    )
    @patch(
        "stripe.Transfer.retrieve_reversal",
        autospec=True,
        return_value=deepcopy(FAKE_TRANSFER_REVERSAL),
    )
    def test_sync_from_stripe_data(
        self,
        transfer_reversal_retrieve_mock,
        balance_transaction_retrieve_mock,
        account_retrieve_mock,
    ):

        transfer_reversal = TransferReversal.sync_from_stripe_data(
            deepcopy(FAKE_TRANSFER_REVERSAL)
        )

        balance_transaction_retrieve_mock.assert_not_called()
        transfer_reversal_retrieve_mock.assert_not_called()

        assert (
            transfer_reversal.balance_transaction.id
            == FAKE_TRANSFER["balance_transaction"]["id"]
        )
        assert transfer_reversal.transfer.id == FAKE_TRANSFER_REVERSAL["transfer"]["id"]

        self.assert_fks(transfer_reversal, expected_blank_fks="")

    @patch(
        "stripe.Account.retrieve",
        return_value=deepcopy(FAKE_STANDARD_ACCOUNT),
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
    )
    @patch(
        "stripe.BalanceTransaction.retrieve",
        return_value=deepcopy(FAKE_BALANCE_TRANSACTION_II),
        autospec=True,
    )
    @patch(
        "stripe.Transfer.retrieve_reversal",
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
        return_value=deepcopy(FAKE_TRANSFER_REVERSAL),
    )
    def test_api_retrieve(
        self,
        transfer_reversal_retrieve_mock,
        balance_transaction_retrieve_mock,
        account_retrieve_mock,
    ):

        transfer_reversal = TransferReversal.sync_from_stripe_data(
            deepcopy(FAKE_TRANSFER_REVERSAL)
        )
        transfer_reversal.api_retrieve()

        transfer_reversal_retrieve_mock.assert_called_once_with(
            id=FAKE_TRANSFER_REVERSAL["transfer"]["id"],
            nested_id=FAKE_TRANSFER_REVERSAL["id"],
            api_key=djstripe_settings.STRIPE_SECRET_KEY,
            expand=["balance_transaction", "transfer"],
            stripe_account=None,
        )

    # we are returning any value for the Transfer.objects.get as we only need to avoid the Transfer.DoesNotExist error
    @patch(
        "djstripe.models.connect.Transfer.objects.get",
        return_value=deepcopy(FAKE_TRANSFER),
    )
    @patch(
        "stripe.Transfer.create_reversal",
        autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED,
        return_value=deepcopy(FAKE_TRANSFER_REVERSAL),
    )
    def test__api_create(self, transfer_reversal_create_mock, transfer_get_mock):

        TransferReversal._api_create(id=FAKE_TRANSFER_REVERSAL["transfer"]["id"])

        transfer_reversal_create_mock.assert_called_once_with(
            id=FAKE_TRANSFER_REVERSAL["transfer"]["id"],
            api_key=djstripe_settings.STRIPE_SECRET_KEY,
        )

    @patch(
        "stripe.Transfer.list_reversals", autospec=IS_STATICMETHOD_AUTOSPEC_SUPPORTED
    )
    def test_api_list(self, transfer_reversal_list_mock):
        p = PropertyMock(return_value=deepcopy(FAKE_TRANSFER_REVERSAL))
        type(transfer_reversal_list_mock).auto_paging_iter = p

        TransferReversal.api_list(id=FAKE_TRANSFER_REVERSAL["transfer"]["id"])

        transfer_reversal_list_mock.assert_called_once_with(
            id=FAKE_TRANSFER_REVERSAL["transfer"]["id"],
            api_key=djstripe_settings.STRIPE_SECRET_KEY,
        )

    def test_is_valid_object(self):
        assert TransferReversal.is_valid_object(deepcopy(FAKE_TRANSFER_REVERSAL))

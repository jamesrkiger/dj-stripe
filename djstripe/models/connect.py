import stripe
from django.db import IntegrityError, models, transaction

from .. import enums
from ..fields import (
    JSONField,
    StripeCurrencyCodeField,
    StripeDecimalCurrencyAmountField,
    StripeEnumField,
    StripeForeignKey,
    StripeIdField,
    StripeQuantumCurrencyAmountField,
)
from ..managers import TransferManager
from ..settings import djstripe_settings
from .base import StripeBaseModel, StripeModel

# todo All These methods need to automatically set the stripe_acct key in stripe retrieval etc.
# todo And all fk retrievals should also use the same stripe_acct

# TODO Test Manually

# The error is that since charge also has a balance transaction field and that the code tries to retrive without a stripe account header!

# ! applicationfee will exist on the platform account
class ApplicationFee(StripeModel):
    """
    When you collect a transaction fee on top of a charge made for your
    user (using Connect), an ApplicationFee is created in your account.

    Stripe documentation: https://stripe.com/docs/api#application_fees
    """

    # expand_fields = ["account", "charge", "balance_transaction"]

    stripe_class = stripe.ApplicationFee
    account = StripeForeignKey(
        "Account",
        on_delete=models.PROTECT,
        related_name="application_fees",
        help_text="ID of the Stripe account this fee was taken from.",
    )
    amount = StripeQuantumCurrencyAmountField(help_text="Amount earned, in cents.")
    amount_refunded = StripeQuantumCurrencyAmountField(
        help_text="Amount in cents refunded (can be less than the amount attribute "
        "on the fee if a partial refund was issued)"
    )
    # TODO application = ...
    balance_transaction = StripeForeignKey(
        "BalanceTransaction",
        on_delete=models.CASCADE,
        help_text="Balance transaction that describes the impact on your account"
        " balance.",
    )
    charge = StripeForeignKey(
        "Charge",
        on_delete=models.CASCADE,
        help_text="The charge that the application fee was taken from.",
    )
    currency = StripeCurrencyCodeField()
    # TODO originating_transaction = ... (refs. both Charge and Transfer)
    refunded = models.BooleanField(
        help_text=(
            "Whether the fee has been fully refunded. If the fee is only "
            "partially refunded, this attribute will still be false."
        )
    )

    # # todo update tests
    # def __str__(self):
    #     return self.human_readable_amount

    # @classmethod
    # def _find_owner_account(cls, data):
    #     return None
    #     from djstripe.models import Account
    #     # ApplicationFee model's owner account is always the platform account.
    #     api_key = data.get("api_key", "")
    #     if api_key:
    #         return Account.get_or_retrieve_for_api_key(api_key)

    # def api_retrieve(self, api_key=None, stripe_account=None):
    #     """
    #     Call the stripe API's retrieve operation for this model.

    #     :param api_key: The api key to use for this request. \
    #         Defaults to djstripe_settings.STRIPE_SECRET_KEY.
    #     :type api_key: string
    #     :param stripe_account: The optional connected account \
    #         for which this request is being made.
    #     :type stripe_account: string
    #     """
    #     # Prefer passed in stripe_account if set.
    #     if not stripe_account:
    #         stripe_account = self._get_stripe_account_id(api_key)
    #     if self.__class__ is ApplicationFee:
    #         stripe_account = None
    #     print("APPLICATION FEE api_retrieve", self, self.id, self.expand_fields, stripe_account)
    #     return self.stripe_class.retrieve(
    #         id=self.id,
    #         api_key=api_key or self.default_api_key,
    #         expand=self.expand_fields,
    #         stripe_account=stripe_account,
    #     )

    #! The webhook for applicationfee is fired on platform accounts but its fields like charge and balancetransaction are on the connected account specified by account.
    #! The other issue is that since the other webhook for charge is a connect webhook, its model field applicationfee is retrieved by the strip_account header of the connected account which is incorrect

    #! The proposed solution is to override application_fee field retrieval by always setting stripe_account key to None
    #! And solution to ensure retrieval of ApplicationFee fields happen by account need to be thought of.

    # ? all webhooks that get fired
    # connect charge.succeeded [evt_1J5V8HQuFmP1Mw5uJre1cCvg]
    # connect payment_intent.succeeded [evt_1J5V8HQuFmP1Mw5un5Tp2UHU]
    # application_fee.created [evt_1J5V8IJSZQVUcJYgkasyxmha]
    # connect payment_intent.created [evt_1J5V8HQuFmP1Mw5utE7sIdme]

    # THis will run whenerv application_fee is about to get saved. So even when charge.aplication_fee needs to be saved as well as the application_fee from the application_fee.created handelr
    def _attach_objects_hook(self, cls, data, current_ids=None):
        """
        Gets called by this object's create and sync methods just before save.
        We use this to retrieve the charge field using the stripe_account
        header set as the account field

        :param cls: The target class for the instantiated object.
        :param data: The data dictionary received from the Stripe API.
        :type data: dict
        :param current_ids: stripe ids of objects that are currently being processed
        :type current_ids: set
        """
        print(f"Attach object hooks invoked by: {cls} {current_ids}")
        # from djstripe.models.core import BalanceTransaction, Charge
        # super()._attach_objects_hook(cls, data, current_ids=current_ids)

        # stripe_account = data.get("account")

        # # retrieve and sync charge
        # charge_data = Charge.stripe_class.retrieve(
        #     id=data.get("charge"),
        #     api_key=self.default_api_key,
        #     expand=getattr(Charge,"expand_fields", None),
        #     stripe_account=stripe_account
        #     )

        # try:
        #     with transaction.atomic():
        #         # charge will also retrieve and create the balancetransaction object
        #         charge = Charge._create_from_stripe_object(charge_data, current_ids=current_ids, stripe_account=stripe_account)

        # except IntegrityError as error:
        #     charge = Charge.objects.get(id=data.get("charge"))

        # # add the retrieved charge instance to the charge model field
        # self.charge = charge

        # print(f"Retrieved and attached {charge.id} to {self}")
        # # retrieve and sync balance_transaction
        # balance_transaction_data = BalanceTransaction.stripe_class.retrieve(
        #     id=data.get("balance_transaction"),
        #     api_key=self.default_api_key,
        #     expand=getattr(BalanceTransaction,"expand_fields", None),
        #     stripe_account=None
        #     )

        # try:
        #     with transaction.atomic():
        #         balance_transaction = BalanceTransaction._create_from_stripe_object(balance_transaction_data, current_ids=current_ids)

        # except IntegrityError as error:
        #     balance_transaction = BalanceTransaction.objects.get(id=data.get("balance_transaction"))

        # # add the retrieved balance transaction instance to the balance transaction model field
        # self.balance_transaction = balance_transaction

    # @classmethod
    # def sync_from_stripe_data(cls, data):
    #     """
    #     Create and sync the charge object so that it can be retrieved correctly
    #     by other webhooks as well as application_fee.* webhooks
    #     """
    #     print("RUNNING SYNC FROM STRIPE DATA")
    #     from djstripe.models.core import Charge

    # stripe_account = data.get("account")

    # # retrieve and sync charge
    # charge_data = Charge.stripe_class.retrieve(
    #         id=cls._id_from_data(data.get("charge")),
    #         api_key=djstripe_settings.STRIPE_SECRET_KEY,
    #         expand=getattr(Charge,"expand_fields", None),
    #         stripe_account=stripe_account
    #     )

    # charge = Charge.sync_from_stripe_data(charge_data)
    # print(f"Created Charge: {charge.id}")
    # try:
    #     with transaction.atomic():
    #         # charge will also retrieve and create the balancetransaction object
    #         charge = Charge._create_from_stripe_object(charge_data, current_ids=current_ids, stripe_account=stripe_account)

    # except IntegrityError as error:
    #     charge = Charge.objects.get(id=data.get("charge"))

    # return super().sync_from_stripe_data(data)

    @classmethod
    def _get_or_create_from_stripe_object(
        cls,
        data,
        field_name="id",
        refetch=True,
        current_ids=None,
        pending_relations=None,
        save=True,
        stripe_account=None,
    ):
        """
        Set the stripe_account to None to ensure application_fee is always retrieved from the
        platform account, which is where it will exist
        """
        print("_get_or_create override", cls, field_name, current_ids)

        # TODO create the charge and balancetransaction objects
        from djstripe.models.core import BalanceTransaction, Charge

        stripe_account = data.get("account")

        # retrieve and sync charge
        charge_data = Charge.stripe_class.retrieve(
            id=cls._id_from_data(data.get("charge")),
            api_key=djstripe_settings.STRIPE_SECRET_KEY,
            expand=getattr(Charge, "expand_fields", None),
            stripe_account=stripe_account,
        )
        print("Creating and syncing Charge")
        try:
            charge = Charge.objects.get(id=data.get("charge"))
        except Charge.DoesNotExist:
            try:
                # with transaction.atomic():
                # charge will also retrieve and create the balancetransaction object
                charge = Charge._create_from_stripe_object(
                    charge_data, current_ids=current_ids, stripe_account=stripe_account
                )

            except IntegrityError as error:
                # Remote possibility that something else (some other webhook) creates
                # the Charge object betwene the first check and the second create query.
                charge = Charge.objects.get(id=data.get("charge"))

        # add the retrieved charge instance to the charge model field
        # self.charge = charge

        print(f"Retrieved and attached {charge.id}")

        return super()._get_or_create_from_stripe_object(
            data=data,
            field_name=field_name,
            refetch=refetch,
            current_ids=current_ids,
            pending_relations=pending_relations,
            save=save,
            stripe_account=None,
        )

    # @classmethod
    # def _create_from_stripe_object(
    #     cls,
    #     data,
    #     current_ids=None,
    #     pending_relations=None,
    #     save=True,
    #     stripe_account=None,
    # ):
    #     """
    #     Set the stripe_account to the id of the Account instance being created.

    #     This ensures that the foreign-key relations that may exist in stripe are
    #     fetched using the appropriate connected account ID.
    #     """
    #     return super()._create_from_stripe_object(
    #         data=data,
    #         current_ids=current_ids,
    #         pending_relations=pending_relations,
    #         save=save,
    #         stripe_account=data["id"] if not stripe_account else stripe_account,
    #     )


class ApplicationFeeRefund(StripeModel):
    """
    ApplicationFeeRefund objects allow you to refund an ApplicationFee that
    has previously been created but not yet refunded.
    Funds will be refunded to the Stripe account from which the fee was
    originally collected.

    Stripe documentation: https://stripe.com/docs/api#fee_refunds
    """

    stripe_class = stripe.ApplicationFeeRefund
    expand_fields = ["balance_transaction", "fee"]
    description = None

    amount = StripeQuantumCurrencyAmountField(help_text="Amount refunded, in cents.")
    balance_transaction = StripeForeignKey(
        "BalanceTransaction",
        on_delete=models.CASCADE,
        help_text="Balance transaction that describes the impact on your account "
        "balance.",
    )
    currency = StripeCurrencyCodeField()
    fee = StripeForeignKey(
        "ApplicationFee",
        on_delete=models.CASCADE,
        related_name="refunds",
        help_text="The application fee that was refunded",
    )

    @classmethod
    def _api_create(cls, api_key=djstripe_settings.STRIPE_SECRET_KEY, **kwargs):
        """
        Call the stripe API's create operation for this model.

        :param api_key: The api key to use for this request. \
            Defaults to djstripe_settings.STRIPE_SECRET_KEY.
        :type api_key: string
        """
        if not kwargs.get("id"):
            raise KeyError("ApplicationFee Object ID is missing")

        try:
            ApplicationFee.objects.get(id=kwargs["id"])
        except ApplicationFee.DoesNotExist:
            raise

        return stripe.ApplicationFee.create_refund(api_key=api_key, **kwargs)

    def api_retrieve(self, api_key=None, stripe_account=None):
        """
        Call the stripe API's retrieve operation for this model.
        :param api_key: The api key to use for this request. \
            Defaults to djstripe_settings.STRIPE_SECRET_KEY.
        :type api_key: string
        :param stripe_account: The optional connected account \
            for which this request is being made.
        :type stripe_account: string
        """
        nested_id = self.id
        id = self.fee.id

        # Prefer passed in stripe_account if set.
        if not stripe_account:
            stripe_account = self._get_stripe_account_id(api_key)

        return stripe.ApplicationFee.retrieve_refund(
            id=id,
            nested_id=nested_id,
            api_key=api_key or self.default_api_key,
            expand=self.expand_fields,
            stripe_account=stripe_account,
        )

    @classmethod
    def api_list(cls, api_key=djstripe_settings.STRIPE_SECRET_KEY, **kwargs):
        """
        Call the stripe API's list operation for this model.
        :param api_key: The api key to use for this request. \
            Defaults to djstripe_settings.STRIPE_SECRET_KEY.
        :type api_key: string
        See Stripe documentation for accepted kwargs for each object.
        :returns: an iterator over all items in the query
        """
        return stripe.ApplicationFee.list_refunds(
            api_key=api_key, **kwargs
        ).auto_paging_iter()


# TODO Add Tests
class CountrySpec(StripeBaseModel):
    """
    Stripe documentation: https://stripe.com/docs/api#country_specs
    """

    stripe_class = stripe.CountrySpec

    id = models.CharField(max_length=2, primary_key=True, serialize=True)

    default_currency = StripeCurrencyCodeField(
        help_text=(
            "The default currency for this country. "
            "This applies to both payment methods and bank accounts."
        )
    )
    supported_bank_account_currencies = JSONField(
        help_text="Currencies that can be accepted in the specific country"
        " (for transfers)."
    )
    supported_payment_currencies = JSONField(
        help_text="Currencies that can be accepted in the specified country"
        " (for payments)."
    )
    supported_payment_methods = JSONField(
        help_text="Payment methods available in the specified country."
    )
    supported_transfer_countries = JSONField(
        help_text="Countries that can accept transfers from the specified country."
    )
    verification_fields = JSONField(
        help_text="Lists the types of verification data needed to keep an account open."
    )

    @classmethod
    def sync_from_stripe_data(cls, data) -> "CountrySpec":
        """
        Syncs this object from the stripe data provided.

        Foreign keys will also be retrieved and synced recursively.

        :param data: stripe object
        :type data: dict
        :rtype: cls
        """
        data_id = data["id"]

        supported_fields = (
            "default_currency",
            "supported_bank_account_currencies",
            "supported_payment_currencies",
            "supported_payment_methods",
            "supported_transfer_countries",
            "verification_fields",
        )

        instance, created = cls.objects.get_or_create(
            id=data_id,
            defaults={k: data[k] for k in supported_fields},
        )

        return instance

    def api_retrieve(self, api_key: str = None, stripe_account=None):
        if api_key is None:
            api_key = djstripe_settings.get_default_api_key(livemode=None)

        return self.stripe_class.retrieve(
            id=self.id,
            api_key=api_key,
            stripe_account=stripe_account,
        )


class Transfer(StripeModel):
    """
    When Stripe sends you money or you initiate a transfer to a bank account,
    debit card, or connected Stripe account, a transfer object will be created.

    Stripe documentation: https://stripe.com/docs/api/python#transfers
    """

    stripe_class = stripe.Transfer
    expand_fields = ["balance_transaction"]
    # expand_fields = ["balance_transaction", "destination", "destination_payment", "source_transaction"]
    stripe_dashboard_item_name = "transfers"

    objects = TransferManager()

    amount = StripeDecimalCurrencyAmountField(help_text="The amount transferred")
    amount_reversed = StripeDecimalCurrencyAmountField(
        null=True,
        blank=True,
        help_text="The amount (as decimal) reversed (can be less than the amount "
        "attribute on the transfer if a partial reversal was issued).",
    )
    balance_transaction = StripeForeignKey(
        "BalanceTransaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Balance transaction that describes the impact on your account"
        " balance.",
    )
    currency = StripeCurrencyCodeField()
    destination = StripeForeignKey(
        "Account",
        on_delete=models.PROTECT,
        related_name="transfers",
        help_text="ID of the Stripe account the transfer was sent to.",
    )
    destination_payment = StripeIdField(
        null=True,
        blank=True,
        help_text="If the destination is a Stripe account, this will be the ID of the "
        "payment that the destination account received for the transfer.",
    )
    reversed = models.BooleanField(
        default=False,
        help_text="Whether or not the transfer has been fully reversed. "
        "If the transfer is only partially reversed, this attribute will still "
        "be false.",
    )
    source_transaction = StripeIdField(
        null=True,
        help_text="ID of the charge (or other transaction) that was used to fund "
        "the transfer. If null, the transfer was funded from the available balance.",
    )
    source_type = StripeEnumField(
        enum=enums.LegacySourceType,
        help_text="The source balance from which this transfer came.",
    )
    transfer_group = models.CharField(
        max_length=255,
        default="",
        blank=True,
        help_text="A string that identifies this transaction as part of a group.",
    )

    @property
    def fee(self):
        if self.balance_transaction:
            return self.balance_transaction.fee

    def __str__(self):
        if self.reversed:
            # Complete Reversal
            return f"{self.human_readable_amount} Reversed"
        elif self.amount_reversed:
            # Partial Reversal
            return f"{self.human_readable_amount} Partially Reversed"
        # No Reversal
        return f"{self.human_readable_amount}"

    def _attach_objects_post_save_hook(self, cls, data, pending_relations=None):
        """
        Iterate over reversals on the Transfer object to create and/or sync
        TransferReversal objects
        """

        super()._attach_objects_post_save_hook(
            cls, data, pending_relations=pending_relations
        )

        for reversals_data in data.get("reversals").auto_paging_iter():
            TransferReversal.sync_from_stripe_data(reversals_data)


class TransferReversal(StripeModel):
    """
    Stripe documentation: https://stripe.com/docs/api#transfer_reversals
    """

    expand_fields = ["balance_transaction", "transfer"]

    # TransferReversal classmethods are derived from
    # and attached to the stripe.Transfer class
    stripe_class = stripe.Transfer

    amount = StripeQuantumCurrencyAmountField(help_text="Amount, in cents.")
    balance_transaction = StripeForeignKey(
        "BalanceTransaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfer_reversals",
        help_text="Balance transaction that describes the impact on your account "
        "balance.",
    )
    currency = StripeCurrencyCodeField()
    transfer = StripeForeignKey(
        "Transfer",
        on_delete=models.CASCADE,
        help_text="The transfer that was reversed.",
        related_name="reversals",
    )

    def __str__(self):
        return str(self.transfer)

    @classmethod
    def _api_create(cls, api_key=djstripe_settings.STRIPE_SECRET_KEY, **kwargs):
        """
        Call the stripe API's create operation for this model.
        :param api_key: The api key to use for this request. \
            Defaults to djstripe_settings.STRIPE_SECRET_KEY.
        :type api_key: string
        """

        if not kwargs.get("id"):
            raise KeyError("Transfer Object ID is missing")

        try:
            Transfer.objects.get(id=kwargs["id"])
        except Transfer.DoesNotExist:
            raise

        return stripe.Transfer.create_reversal(api_key=api_key, **kwargs)

    def api_retrieve(self, api_key=None, stripe_account=None):
        """
        Call the stripe API's retrieve operation for this model.
        :param api_key: The api key to use for this request. \
            Defaults to djstripe_settings.STRIPE_SECRET_KEY.
        :type api_key: string
        :param stripe_account: The optional connected account \
            for which this request is being made.
        :type stripe_account: string
        """
        nested_id = self.id
        id = self.transfer.id

        # Prefer passed in stripe_account if set.
        if not stripe_account:
            stripe_account = self._get_stripe_account_id(api_key)

        return stripe.Transfer.retrieve_reversal(
            id=id,
            nested_id=nested_id,
            api_key=api_key or self.default_api_key,
            expand=self.expand_fields,
            stripe_account=stripe_account,
        )

    @classmethod
    def api_list(cls, api_key=djstripe_settings.STRIPE_SECRET_KEY, **kwargs):
        """
        Call the stripe API's list operation for this model.
        :param api_key: The api key to use for this request. \
            Defaults to djstripe_settings.STRIPE_SECRET_KEY.
        :type api_key: string
        See Stripe documentation for accepted kwargs for each object.
        :returns: an iterator over all items in the query
        """
        return stripe.Transfer.list_reversals(
            api_key=api_key, **kwargs
        ).auto_paging_iter()

    @classmethod
    def is_valid_object(cls, data):
        """
        Returns whether the data is a valid object for the class
        """
        return "object" in data and data["object"] == "transfer_reversal"


# import stripe; stripe.api_key="sk_test_51ItQ7cJSZQVUcJYgHMIKKvkqL6XNUHRI1kQcpoR9yEdOusA5rWpTXpXYnIqHpIvWlu5odQYNBDVwNSYTJN1HmtCC00RvEyLiZW";payment_intent = stripe.PaymentIntent.create(payment_method_types=['card'],amount=1000,currency='usd',application_fee_amount=123,stripe_account='acct_1J5NiOQuFmP1Mw5u', confirm=True, customer='cus_Jipya0TWp92QHK')

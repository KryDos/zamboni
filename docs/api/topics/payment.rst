.. _payment:

========
Payments
========

This API is specific to setting up and processing payments for an app in the
Marketplace.

.. _payment-account-label:

Configuring payment accounts
============================

Payment accounts can be added and listed.

.. note:: Authentication is required.

.. http:post:: /api/v1/payments/account/

    **Request**

    :param account_name: Account name.
    :param companyName: Company name.
    :param vendorName: Vendor name.
    :param financeEmailAddress: Financial email.
    :param supportEmailAddress: Support email.
    :param address1: Address.
    :param address2: Second line of address.
    :param addressCity: City/municipality.
    :param addressState: State/province/region.
    :param addressZipCode: Zip/postal code.
    :param countryIso: Country.
    :param vatNumber: VAT number.

    *the following fields cannot be modified after account creation*

    :param bankAccountPayeeName: Account holder name.
    :param bankAccountNumber: Bank account number.
    :param bankAccountCode: Bank account code.
    :param bankName: Bank name.
    :param bankAddress1: Bank address.
    :param bankAddress2: Second line of bank address.
    :param bankAddressState: Bank state/province/region.
    :param bankAddressZipCode: Bank zip/postal code.
    :param bankAddressIso: Bank country.
    :param adminEmailAddress: Administrative email.
    :param currencyIso: Currency you prefer to be paid in.

    **Response**

    :status code: 201 successfully created.

.. http:put:: /api/v1/payments/account/(int:id)/

    **Request**

    :param account_name: Account name.
    :param companyName: Company name.
    :param vendorName: Vendor name.
    :param financeEmailAddress: Financial email.
    :param supportEmailAddress: Support email.
    :param address1: Address.
    :param address2: Second line of address.
    :param addressCity: City/municipality.
    :param addressState: State/province/region.
    :param addressZipCode: Zip/postal code.
    :param countryIso: Country.
    :param vatNumber: VAT number.

    **Response**

    :status 204: successfully updated.

.. http:delete:: /api/v1/payments/account/(int:id)/

    **Response**

    :status 204: successfully deleted.

.. http:get:: /api/v1/payments/account/

    **Request**

    The standard :ref:`list-query-params-label`.

    **Response**

    :param meta: :ref:`meta-response-label`.
    :param objects: A :ref:`listing <objects-response-label>` of :ref:`accounts <payment-account-response-label>`.

.. _payment-account-response-label:

.. http:get:: /api/v1/payments/account/(int:id)/

    **Response**

    An account object, see below for an example.

    :status 200: successfully completed.

    Example:

    .. code-block:: json

        {
             "account_name": "account",
             "address1": "123 Main St",
             "addressCity": "Byteville",
             "addressPhone": "605-555-1212",
             "addressState": "HX",
             "addressZipCode": "55555",
             "adminEmailAddress": "apps_admin@example.com",
             "companyName": "Example Company",
             "countryIso": "BRA",
             "currencyIso": "EUR",
             "financeEmailAddress": "apps_accounts@example.com",
             "resource_uri": "/api/v1/payments/account/175/",
             "supportEmailAddress": "apps_support@example.com",
             "vendorName": "vendor"
        }

Upsell
======

.. http:post:: /api/v1/payments/upsell/(int:id)/

    Creates an upsell relationship between two apps, a free and premium one.
    Send the URLs for both apps in the post to create the relationship.

    **Request**

    :param free: URL to the free app.
    :param premium: URL to the premium app.

    **Response**

    :status 201: sucessfully created.

.. http:get:: /api/v1/payments/upsell/(int:id)/

    **Response**

    .. code-block:: json

        {"free": "/api/v1/apps/app/1/",
         "premium": "/api/v1/apps/app/2/"}

    :param free: URL to the free app.
    :param premium: URL to the premium app.

.. http:patch:: /api/v1/payments/upsell/(int:id)/

    Alter the upsell from free to premium by passing in new free and premiums.

    **Request**

    :param free: URL to the free app.
    :param premium: URL to the premium app.

    **Response**

    :status 200: sucessfully altered.

.. http:delete:: /api/v1/payments/upsell/(int:id)/

    To delete the upsell relationship.

    **Response**

    :status 204: sucessfully deleted.

Payment accounts
================

.. http:post:: /api/v1/payments/app/

    Creates a relationship between the payment account and the app.

    **Request**

    :param app: URL to the premium app.
    :param account: URL to the account.

    Once created, the app is not changeable.

    **Response**

    :status 201: sucessfully created.
    :param app: URL to the premium app.
    :param account: URL to the account.

.. http:patch:: /api/v1/payments/app/(int:id)/

    Alter the payment account being used.

    **Request**

    :param app: URL to the premium app. Must be unchanged.
    :param account: URL to the account.

    **Response**

    :status 200: sucessfully updated.
    :param app: URL to the premium app.
    :param account: URL to the account.

Preparing payment
=================

Produces the JWT that is passed to `navigator.mozPay`_.

.. note:: Authentication is required.

.. http:post:: /api/v1/webpay/prepare/

    **Request**

    :param string app: the id or slug of the app to be purchased.

    **Response**

    .. code-block:: json

        {
            "app": "337141: Something Something Steamcube!",
            "contribStatusURL": "https://marketplace.firefox.com/api/v1/webpay/status/123/",
            "resource_uri": "",
            "webpayJWT": "eyJhbGciOiAiSFMy... [truncated]",
        }

    :param string webpayJWT: the JWT to pass to `navigator.mozPay`_
    :param string contribStatusURL: the URL to poll for
        :ref:`payment-status-label`.

    :status 201: successfully completed.
    :status 401: not authenticated.
    :status 403: app cannot be purchased. This could be because the app has
        already been purchased.

.. _payment-status-label:

Payment status
==============

.. note:: Authentication is required.

.. http:get:: /api/v1/webpay/status/(string:uuid)/

    **Request**

    :param string uuid: the uuid of the payment. This URL is returned as the
        ``contribStatusURL`` parameter of a call to *prepare*.

    **Response**

    :param string status: ``complete`` or ``incomplete``

    :status 200: request processed, check status for value.
    :status 403: not authorized to view details on that transaction.

Installing
==========

When an app is installed from the Marketplace, call the install API. This will
record the install. If the app is a paid app, it will return the receipt that
to be used on install.

.. http:post:: /api/v1/receipts/install/

    Returns a receipt if the app is paid and a receipt should be installed.

    **Request**:

    :param string app: the id or slug of the app being installed.

    **Response**:

    .. code-block:: json

        {"receipt": "eyJhbGciOiAiUlM1MT...[truncated]"}

    :statuscode 201: successfully completed.
    :statuscode 402: payment required.
    :statuscode 403: app is not public, install not allowed.

Developers
~~~~~~~~~~

Developers of the app will get a special developer receipt that is valid for
24 hours and does not require payment. See also `Test Receipts`_.

Reviewers
~~~~~~~~~

Reviewers should not use this API.

Test Receipts
=============

Returns test receipts for use during testing or development. The returned
receipt will have type `test-receipt`. Only works for hosted apps.

.. http:post:: /api/v1/receipts/test/

    Returns a receipt suitable for testing your app.

    **Request**:

    :param string manifest_url: the fully qualified URL to the manifest, including
        protocol.
    :param string receipt_type: one of ``ok``, ``expired``, ``invalid`` or ``refunded``.

    **Response**:

    .. code-block:: json

        {"receipt": "eyJhbGciOiAiUlM1MT...[truncated]"}

    :status 201: successfully completed.

Pay Tiers
==========

.. http:get:: /api/v1/webpay/prices/

    Gets a list of pay tiers from the Marketplace.

    **Request**

    :param provider: (optional) the payment provider. Current values: *bango*

    The standard :ref:`list-query-params-label`.

    **Response**

    :param meta: :ref:`meta-response-label`.
    :param objects: A :ref:`listing <objects-response-label>` of :ref:`apps <pay-tier-response-label>`.
    :statuscode 200: successfully completed.

.. _pay-tier-response-label:

.. http:get:: /api/v1/webpay/prices/(int:id)/

    **Response**

    .. code-block:: json

        {
            "name": "Tier 1",
            "pricePoint": "1",
            "prices": [{
                "price": "0.99",
                "method": 2,
                "region": 2,
                "tier": 26,
                "provider": 1,
                "currency": "USD",
                "id": 1225
            }, {
                "price": "0.69",
                "method": 2,
                "region": 14,
                "tier": 26,
                "provider": 1,
                "currency": "DE",
                "id": 1226
            }],
            "localized": {},
            "resource_uri": "/api/v1/webpay/prices/1/",
            "created": "2011-09-29T14:15:08",
            "modified": "2013-05-02T14:43:58"
        }

    :param region: a :ref:`region <region-response-label>`.
    :param carrier: a :ref:`carrier <carrier-response-label>`.
    :param localized: see `Localized tier`.
    :param tier: the id of the tier.
    :param method: the payment method.
    :param provider: payment provider, currently only ``1`` is supported.
    :param pricePoint: this is the value used for in-app payments.
    :statuscode 200: successfully completed.


.. _localized-tier-label:

Localized tier
~~~~~~~~~~~~~~

To display a price to your user, it would be nice to know how to display a
price in the app. The Marketplace does some basic work to calculate the locale
of a user. Information that would be useful to show to your user is placed in
the localized field of the result.

A request with the HTTP *Accept-Language* header set to *pt-BR*, means that
*localized* will contain:

    .. code-block:: json

        {
            "localized": {
                "amount": "10.00",
                "currency": "BRL",
                "locale": "R$10,00",
                "region": "Brasil"
            }
        }

The exact same request with an *Accept-Language* header set to *en-US*
returns:

    .. code-block:: json

        {
            "localized": {
                "amount": "0.99",
                "currency": "USD",
                "locale": "$0.99",
                "region": "United States"
            }
        }

If a suitable currency for the region given in the request cannot be found, the
result will be empty. It could be that the currency that the Marketplace will
accept is not the currency of the country. For example, a request with
*Accept-Language* set to *fr* may result in:

    .. code-block:: json

        {
            "localized": {
                "amount": "1.00",
                "currency": "USD",
                "locale": "1,00\xa0$US",
                "region": "Monde entier"
            }
        }

Please note: these are just examples to demonstrate cases. Actual results will
vary depending upon data sent and payment methods in the Marketplace.

Product Icons
=============

Authenticated clients like `WebPay`_ need to display external product images in a
safe way. This API lets WebPay cache and later retrieve icon URLs.

.. note:: All write requests (``POST``, ``PATCH``) require authenticated users to have the
    ``ProductIcon:Create``  permission.


.. http:get:: /api/v1/webpay/product/icon/

    Gets a list of cached product icons.

    **Request**

    :param ext_url: Absolute external URL of product icon that was cached.
    :param ext_size: Height and width pixel value that was declared for this icon.
    :param size: Height and width pixel value that this icon was resized to.

    You may also request :ref:`list-query-params-label`.

    **Response**

    :param meta: :ref:`meta-response-label`.
    :param objects: A :ref:`listing <objects-response-label>` of :ref:`product icons <product-icon-response-label>`.
    :statuscode 200: successfully completed.

.. _product-icon-response-label:

.. http:get:: /api/v1/webpay/product/icon/(int:id)/

    **Response**

    .. code-block:: json

        {
            "url": "http://marketplace-cdn/product-icons/0/1.png",
            "resource_uri": "/api/v1/webpay/product/icon/1/",
            "ext_url": "http://appserver/media/icon.png",
            "ext_size": 64,
            "size": 64
        }

    :param url: Absolute URL of the cached product icon.
    :statuscode 200: successfully completed.

.. http:post:: /api/v1/webpay/product/icon/

    Post a new product icon URL that should be cached.
    This schedules an icon to be processed but does not return any object data.

    **Request**

    :param ext_url: Absolute external URL of product icon that should be cached.
    :param ext_size: Height and width pixel value that was declared for this icon.
    :param size: Height and width pixel value that this icon should be resized to.

    **Response**

    :statuscode 202: New icon accepted. Deferred processing will begin.
    :statuscode 400: Some required fields were missing or invalid.
    :statuscode 401: The API user is unauthorized to cache product icons.


Transaction failure
===================

.. note:: Requires authenticated users to have the Transaction:NotifyFailure
    permission. This API is used by internal clients such as WebPay_.

.. http:patch:: /api/v1/webpay/failure/(int:transaction_id)/

    Notify the app developers that our attempts to call the postback or
    chargebacks URLs from `In-app Payments`_ failed. This will send an
    email to the app developers.

    **Response**

    :status 202: Notification will be sent.
    :statuscode 401: The API user is not authorized to report failures.

.. _CORS: https://developer.mozilla.org/en-US/docs/HTTP/Access_control_CORS
.. _WebPay: https://github.com/mozilla/webpay
.. _In-app Payments: https://developer.mozilla.org/en-US/docs/Apps/Publishing/In-app_payments
.. _navigator.mozPay: https://wiki.mozilla.org/WebAPI/WebPayment

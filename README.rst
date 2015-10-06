python-misfit
=============

.. image:: https://travis-ci.org/orcasgit/python-misfit.svg?branch=master
   :target: https://travis-ci.org/orcasgit/python-misfit
   :alt: Build Status
.. image:: https://coveralls.io/repos/orcasgit/python-misfit/badge.png?branch=master
   :target: https://coveralls.io/r/orcasgit/python-misfit?branch=master
   :alt: Coverage Status
.. image:: https://requires.io/github/orcasgit/python-misfit/requirements.svg?branch=master
   :target: https://requires.io/github/orcasgit/python-misfit/requirements/?branch=master
   :alt: Requirements Status

Misfit API Python Client Implementation

.. _README-Requirements:

Requirements
============

* Python >= 2.6, Python >= 3.2, or PyPy. You can download it from `here <https://www.python.org/>`_
* Pip. If you have Python >= 2.7.9 or >= 3.4 then you already have ``pip``. Otherwise, please follow `these instructions <https://pip.pypa.io/en/latest/installing.html>`_

.. _README-Installing:

Installing
==========

Once you have satisfied the requirements listed above, install by running the
following command from the
`terminal <http://cli.learncodethehardway.org/book/ex1.html>`_: ::

    pip install misfit

.. _README-Installing-End:

Quick Start
===========

.. _README-Quick-Start:

Install with ``pip install misfit``

`Create an app <https://build.misfit.com/apps>`_ with "Application Domain" set to
http://127.0.0.1:8080/. Now use the "App key" and "App secret" in the following
command: ::

    misfit authorize --client_id=<app_key> --client_secret=<app_secret>

That will save the necessary credentials for making further API calls to a file
called "misfit.cfg". These credentials should be kept private. You can use same
the command-line client to access everything in the
`Resource API <https://build.misfit.com/docs/resource>`_. You can also access the
same resources using the Python API: ::

    >>> from misfit import Misfit
    >>> misfit = Misfit(<client_id>, <client_secret>, <access_token>)
    >>> print(misfit.profile())
    {u'gender': u'male', u'birthday': u'1981-07-18', u'userId': u'scrubbed', u'name': u'Brad Pitcher'}

.. _README-Quick-Start-End:

Slow Start
==========

.. _README-Slow-Start:

After you have installed and `created your misfit app <https://build.misfit.com/apps>`_
you can authorize and use the API with your own web server rather than the
built-in CherryPy server like so: ::

    >>> from misfit.auth import MisfitAuth
    >>> auth = MisfitAuth(<client_id>, <client_secret>, redirect_uri=<redirect_uri>)
    >>> auth_url = auth.authorize_url()

Now redirect the user to ``auth_url``. When control returns to your web
server at the endpoint specified in ``<redirect_uri>``, you will receive
``code`` and ``state`` GET params you can pass to the
``fetch_token`` method, which will return ``access_token``, which is
needed for further API calls: ::

    >>> access_token = auth.fetch_token(<code>, <state>)
    >>> from misfit import Misfit
    >>> misfit = Misfit(<client_id>, <client_secret>, <access_token>)
    >>> print(misfit.profile())
    {u'gender': u'male', u'birthday': u'1981-07-18', u'userId': u'scrubbed', u'name': u'Brad Pitcher'}

.. _README-Notifications:

Notifications
=============

This library also includes some basic tools to ease notification handling. To
use Misfit's Notification API with your web application, the first thing you
need to do is set up an endpoint to accept POST requests on the domain you
specified when you created your app, like
``http://example.com/misfit/notification/`` if your application domain is
``http://example.com``.

Now, when you handle the request, just create a ``MisfitNotification``
object with the body of the request as an argument. The
``MisfitNotification`` constructor automatically verifies the signature of
the SNS message so you can feel secure in the knowledge that the message is
legitimate. It will raise ``cryptography.exceptions.InvalidSignature`` if
the signature is not valid.

The ``MisfitNotification`` class handles both subscription confirmation
messages and regular update messages. You can check the type of message by
looking at the ``Type`` attribute, which will be either
``'SubscriptionConfirmation'`` or ``'Notification'``. For a
``Notification`` message, you will find the updates as a list in a
``Message`` attribute. After you process the updates (which can take no
longer than
`15 seconds <http://docs.aws.amazon.com/sns/latest/dg/DeliveryPolicies.html>`_)
make sure to respond with an HTTP status of 200, otherwise SNS may try to
deliver it again. A full workflow should look something like this: ::

    >>> from misfit.notification import MisfitNotification
    >>> notification = MisfitNotification(content)
    >>> if notification.Type == 'Notification':
    >>>    for message in notification.Message:
    >>>        if message.type == 'goals':
    >>>            # Handle goal update
    >>>        # Handle other message types
    >>> # Give an empty response with a 200 status code

Once you have your endpoint up and running, go to your
`app <https://build.misfit.com/apps/>`_ and add your endpoint as a subscription
hook URL, making sure the format is json. Click "Test Endpoint" and if all goes
well, the verification should seamlessly take place. If not, please
`file an issue <https://github.com/orcasgit/python-misfit/issues>`_ and we will
try and help you debug. Now switch on all the resources you would like to
receive and click "Update". Soon you will be receiving Misfit notifications!

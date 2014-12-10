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

Quick Start
===========

Install with :code:`pip install misfit`

[Create an app](https://build.misfit.com/apps) with "Application Domain" set to
http://127.0.0.1:8080/. Now use the "App key" and "App secret" in the following
command: ::
    misfit authorize --client_id=<app_key> --client_secret=<app_secret>

That will save the necessary credentials for making further API calls to a file
called "misfit.cfg". These credentials should be kept private. You can use same
the command-line client to access everything in the
[Resource API](https://build.misfit.com/docs/resource). You can also access the
same resources using the Python API: ::
    >>> from misfit import Misfit
    >>> misfit = Misfit(<client_id>, <client_secret>, <access_token>)
    >>> print(misfit.profile())
    {u'gender': u'male', u'birthday': u'1981-07-18', u'userId': u'scrubbed', u'name': u'Brad Pitcher'}

Slow Start
==========

After you have installed and `created your misfit app<https://build.misfit.com/apps>`_
you can authorize and use the API with your own web server rather than the
built-in CherryPy server like so: ::
    >>> from misfit.auth import MisfitAuth
    >>> auth = MisfitAuth(<client_id>, <client_secret>, redirect_uri=<redirect_uri>)
    >>> auth_url = auth.authorize_url()

Now redirect the user to :code:`auth_url`. When control returns to your web
server at the endpoint specified in :code:`<redirect_uri>`, you will receive
:code:`code` and :code:`state` GET params you can pass to the
:code:`fetch_token` method, which will return :code:`access_token`, which is
needed for further API calls: ::
    >>> access_token = auth.fetch_token(<code>, <state>)
    >>> from misfit import Misfit
    >>> misfit = Misfit(<client_id>, <client_secret>, <access_token>)
    >>> print(misfit.profile())
    {u'gender': u'male', u'birthday': u'1981-07-18', u'userId': u'scrubbed', u'name': u'Brad Pitcher'}

Requirements
============

* Python 2.6+ < 3
* slumber
* docopt
* cherryPy
* requests-oauthlib

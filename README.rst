python-misfit
=============

Misfit API Python Client Implementation

Quick Start
===========

Install with :code:`pip install misfit`

[Create an app](https://build.misfit.com/apps) with "Application Domain" set to
http://127.0.0.1:8080/. Now use the "App key" and "App secret" in the following
command: ::
    misfit authenticate --client_id=<app_key> --client_secret=<app_secret>

That will save the necessary credentials for making further API calls to a file
called "misfit.cfg". These credentials should be kept private. You can use same
the command-line client to access everything in the
[Resource API](https://build.misfit.com/docs/resource). You can also access the
same resources using the Python API: ::
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

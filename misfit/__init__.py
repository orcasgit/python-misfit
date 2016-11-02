"""
Misfit API Python Client Implementation. Facilitates connection to Misfit's
`REST API <https://build.misfit.com/docs/>`_ and retrieving user data.
"""


from .misfit import (
    API_URL,
    Misfit,
    MisfitProfile,
    MisfitDevice,
    MisfitGoal,
    MisfitSummary,
    MisfitSession,
    MisfitSleepDetail,
    MisfitSleep
)

__all__ = ['API_URL', 'Misfit', 'MisfitProfile', 'MisfitDevice', 'MisfitGoal',
           'MisfitSummary', 'MisfitSession', 'MisfitSleepDetail',
           'MisfitSleep']
__title__ = 'misfit'
__author__ = 'ORCAS'
__author_email__ = 'bpitcher@orcasinc.com'
__copyright__ = 'Copyright 2014-2015 ORCAS'
__license__ = 'Apache 2.0'
__version__ = '0.3.2'
__release__ = __version__

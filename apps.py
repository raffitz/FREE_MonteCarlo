'''Module implementing pi calculation through Monte Carlo simulation'''

from django.apps import AppConfig


# pylint: disable=invalid-name
class dev_MonteCarloConfig(AppConfig):
    '''Inherit django base class, assigning a name to the app'''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dev_MonteCarlo'

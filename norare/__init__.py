import collections

from pyramid.config import Configurator


from clld.interfaces import IMapMarker, IValueSet, IValue, IDomainElement
from clldutils.svg import pie, icon, data_url

# we must make sure custom models are known at database initialization!
from norare import models


_ = lambda s: s
_('Parameter')
_('Parameters')
_('Unitparameter')
_('Unitparameters')
_('Contribution')
_('Contributions')

#
# FIXME: forward Unit to Value
#

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clld.web.app')
    config.include('clld_markdown_plugin')
    config.include('clldmpg')
    return config.make_wsgi_app()

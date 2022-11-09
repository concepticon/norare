from clld.web.util.helpers import get_referents


def source_detail_html(context=None, request=None, **kw):
    return {'referents': get_referents(context)}

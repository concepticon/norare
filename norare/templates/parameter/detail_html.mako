<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%! from clld.web.util import concepticon %>
<%block name="title">${_('Parameter')} ${ctx.name}</%block>

<h2>${_('Parameter')} ${ctx.name} ${concepticon.link(req, id=ctx.id)}</h2>

<div class="alert alert-info">${ctx.description}</div>

${request.get_datatable('unitvalues', h.models.UnitValue, parameter=ctx).render()}

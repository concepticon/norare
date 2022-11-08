<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${_('Parameter')} ${ctx.name}</%block>



<h2>${_('Parameter')} ${ctx.name}</h2>

% if ctx.description:
<p>${ctx.description}</p>
% endif

${request.get_datatable('unitvalues', h.models.UnitValue, parameter=ctx).render()}
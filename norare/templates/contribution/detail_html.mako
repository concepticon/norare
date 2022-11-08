<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>
<%! from clld_markdown_plugin import markdown %>

<h2>${_('Contribution')} ${ctx.name}</h2>

<div>${markdown(req, ctx.description)|n}</div>

<% dt = request.get_datatable('unitparameters', h.models.UnitParameter, contribution=ctx) %>
% if dt:
<div>
    ${dt.render()}
</div>
% endif

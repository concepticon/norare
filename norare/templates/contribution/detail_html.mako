<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>
<%! from clld_markdown_plugin import markdown %>

<%def name="sidebar()">
    <div class="well">
        <h3>Source</h3>
        <dl>
            % for ref in ctx.references:
                <dt>${h.link(req, ref.source)}</dt>
                <dd>${ref.source.bibtex().text()}</dd>
            % endfor
        </dl>
    </div>
</%def>

<h2>${_('Contribution')} ${ctx.name}</h2>

<div>${markdown(req, ctx.description)|n}</div>

<h3>Variables</h3>

<% dt = request.get_datatable('unitparameters', h.models.UnitParameter, contribution=ctx) %>
% if dt:
<div>
    ${dt.render()}
</div>
% endif

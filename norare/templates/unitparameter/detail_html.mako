<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "unitparameters" %>
<%! from clld_markdown_plugin import markdown %>

<%def name="sidebar()">
    <div class="well">
        <table class="table table-condensed">
            <tbody>
            <tr>
                <th>Language:</th>
                <td>${h.link(req, ctx.language)}</td>
            </tr>
            <tr>
                <th>Category:</th>
                <td>${ctx.category}</td>
            </tr>
            <tr>
                <th>Result:</th>
                <td>${ctx.result}</td>
            </tr>
            <tr>
                <th>Method:</th>
                <td>${ctx.method}</td>
            </tr>
            <tr>
                <th>Type:</th>
                <td>${ctx.type} (${ctx.format_datatype()})</td>
            </tr>
            </tbody>
        </table>
    </div>

    <div class="well">
        <h3>Dataset</h3>
        <p>${h.link(req, ctx.dataset)}</p>
        <div>${markdown(req, ctx.dataset.description)|n}</div>
    </div>
</%def>

<h2>${_('Unitparameter')} ${ctx.id.split('-')[-1]}</h2>

<div>${markdown(req, ctx.description)|n}</div>

<div>
    <% dt = request.registry.getUtility(h.interfaces.IDataTable, 'unitvalues'); dt = dt(request, h.models.UnitValue, unitparameter=ctx) %>
    ${dt.render()}
</div>

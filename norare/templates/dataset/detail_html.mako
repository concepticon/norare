<%inherit file="../home_comp.mako"/>
<%! from clld_markdown_plugin import markdown %>

<%def name="sidebar()">
    <div class="well">
        <h3>How to cite</h3>
        <p>
            More information on how to use the data can be found in a study published in Behavior Research Methods.
            If you use the data assembled here, we ask you kindly to cite the study.
        </p>
        <blockquote>
            ${req.dataset.jsondata['citation']|n}
        </blockquote>
    </div>
</%def>

<h1>NoRaRe</h1>

<img src="${req.static_url('norare:static/norare-logo.svg')}" style="width: 25%; float: left; margin-right: 1em;">
<p class="lead">
    Welcome to NoRaRe, the cross-linguistic database of <strong>No</strong>rms, <strong>Ra</strong>tings, and <strong>Re</strong>lations
    of Words and Concepts.
</p>
<p>
    This web application serves as a light-weight interface to quickly browse the Database of Cross-Linguistic
    Norms, Ratings, and Relations for Words and Concepts (NoRaRe). The database can be understood as an expansion
    of the
    ${h.external_link('https://concepticon.clld.org', label='Concepticon project')}
    which links concept lists used in the literature in historical linguistics,
    linguistics typology, and psycholinguistics to unique concept sets. While Concepticon links concept lists
    to concept sets, NoRaRe adds information on specific concept and word properties as they are provided in
    different datasets that have been published along with studies in linguistics and psychology.
</p>
<div style="width: 100%; text-align: center">
    <a href="${req.route_url('unitparameters')}">
        <img width="50%" src="${ctx.jsondata['wordcloud']}" class="img-polaroid">
    </a>
</div>

<h3>Funding</h3>
${markdown(req, req.dataset.jsondata['grants'])|n}
<img width="200px" src="${req.static_url('norare:static/eu-logo.png')}"/>

<%inherit file="home_comp.mako"/>

<h3>${_('Downloads')}</h3>

<div class="alert alert-info">
    <p>
        The NoRaRe web application serves the latest
        ${h.external_link('https://github.com/concepticon/norare-cldf/releases', label=_('released version'))}
        of
        ${h.external_link('https://github.com/concepticon/norare-cldf', label='concepticon/norare-cldf')}.
        All released version are accessible via
        <a href="https://doi.org/">
            <img src="https://zenodo.org/badge/DOI/ .svg" alt="DOI">
        </a>
        <br/>
        on ZENODO as well.
    </p>
</div>
<h4>How to cite</h4>
<p>If you use this data, please cite</p>
<blockquote>
    ${req.dataset.jsondata['citation']}
</blockquote>
<p>as well as the exact released version of the dataset.</p>

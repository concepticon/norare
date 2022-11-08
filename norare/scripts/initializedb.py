import itertools
import collections

from pycldf import Sources
from clldutils.misc import nfilter, slug
from clldutils.color import qualitative_colors
from clld.cliutil import Data, bibtex2source
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib import bibtex
from csvw.metadata import Datatype
from cldfviz.text import CLDFMarkdownLink


import norare
from norare import models


def main(args):
    data = Data()
    data.add(
        common.Dataset,
        norare.__name__,
        id=norare.__name__,
        name=args.cldf.properties['dc:title'],
        domain='norare.clld.org',

        publisher_name="Max Planck Institute for Evolutionary Anthropology",
        publisher_place="Leipzig",
        publisher_url="https://www.eva.mpg.de",
        license="http://creativecommons.org/licenses/by/4.0/",
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'},

    )

    def fname_to_component(ml):
        if ml.is_cldf_link:
            ml.url = "{}#cldf:{}".format(ml.component(cldf=args.cldf), ml.objid)
        return ml

    for rec in bibtex.Database.from_file(args.cldf.bibpath, lowercase=True):
        data.add(common.Source, rec.id, _obj=bibtex2source(rec))

    for c in args.cldf.iter_rows('ContributionTable', 'id', 'name', 'description'):
        contrib = data.add(
            models.NorareDataset,
            c['id'],
            id=c['id'],
            name=c['name'],
            description=CLDFMarkdownLink.replace(c['description'], fname_to_component),
            citation=c['Citation'],
            year=c['Year'],
            url=c['URL'],
            alias=c['Alias'],
        )
        for ord, author in enumerate(c['Contributor'], start=1):
            if ',' in author:
                assert author.count(',') == 1
                last, first = [s.strip() for s in author.split(',')]
            else:
                comps = [s.strip() for s in author.split()]
                last = comps[-1]
                first = ' '.join(comps[:-1])
            aid = slug(last + first)
            contributor = data['Contributor'].get(aid)
            if not contributor:
                contributor = data.add(
                    common.Contributor,
                    aid,
                    id=aid,
                    name='{} {}'.format(first, last)
                )
            DBSession.add(common.ContributionContributor(
                contributor=contributor,
                contribution=contrib,
                ord=ord))
        for src in c['Source']:
            DBSession.add(common.ContributionReference(
                contribution=contrib,
                source=data['Source'][src]))

    for lang in args.cldf.iter_rows('LanguageTable', 'id', 'glottocode', 'name', 'latitude', 'longitude'):
        data.add(
            common.Language,
            lang['id'],
            id=lang['id'],
            name=lang['name'],
            latitude=lang['latitude'],
            longitude=lang['longitude'],
        )

    refs = collections.defaultdict(list)

    for param in args.cldf.iter_rows('ParameterTable', 'id', 'name'):
        data.add(
            models.Conceptset,
            param['id'],
            id=param['id'],
            name='{} [{}]'.format(param['name'], param['id']),
            description=param['Description'],
            glosses_english = '; '.join(param['glosses'].get('english', [])),
            glosses_german = '; '.join(param['glosses'].get('german', [])),
            glosses_french = '; '.join(param['glosses'].get('french', [])),
            glosses_spanish = '; '.join(param['glosses'].get('spanish', [])),
            glosses_chinese = '; '.join(param['glosses'].get('chinese', [])),
            glosses_russian = '; '.join(param['glosses'].get('russian', [])),
            glosses_portuguese = '; '.join(param['glosses'].get('portuguese', [])),
        )

    dtypes = {}
    for variable in args.cldf.iter_rows('variables.csv'):
        # ID,Dataset_ID,Language_ID,Name,Note,Other,Source,Category,Structure,Rating,Tag,Datatype
        v = data.add(
            models.Variable,
            variable['ID'],
            id=variable['ID'],
            #name=,
            category=variable['Category'],
            other=variable['Other'],
            structure=variable['Structure'],
            rating=variable['Rating'],
            tag=variable['Tag'],
            description=CLDFMarkdownLink.replace(variable['Note'], fname_to_component),
            dataset=data['NorareDataset'][variable['Dataset_ID']],
            jsondata=variable['Datatype'],
        )
        DBSession.flush()
        dt = Datatype.fromvalue(variable['Datatype'])
        dtypes[variable['ID']] = dt
        if (dt.base == 'string' and dt.format) or dt.base == 'boolean':
            # Create UnitParameterDomain objects!
            opts = dt.format.split('|') if dt.format else ['1', '0']
            for i, opt in enumerate(opts, start=1):
                data.add(
                    common.UnitDomainElement,
                    '{}-{}'.format(v.id, i),
                    id='{}-{}'.format(v.id, i),
                    name=opt,
                    unitparameter_pk=v.pk,
                    ord=i
                )

    for form in args.cldf.iter_rows('FormTable', 'id', 'form', 'languageReference', 'parameterReference', 'contributionReference', 'source'):
        vsid = (form['languageReference'], form['parameterReference'], form['contributionReference'])
        vs = data['ValueSet'].get(vsid)
        if not vs:
            vs = data.add(
                common.ValueSet,
                vsid,
                id='-'.join(vsid),
                language=data['Language'][form['languageReference']],
                parameter=data['Conceptset'][form['parameterReference']],
                contribution=data['NorareDataset'][form['contributionReference']],
            )
        #for ref in form.get('source', []):
        #    sid, pages = Sources.parse(ref)
        #    refs[(vsid, sid)].append(pages)
        word = data.add(
            common.Unit,
            form['id'],
            id=form['id'],
            name=form['form'],
            language=data['Language'][form['languageReference']],
        )
        models.Concept(
            id=form['id'],
            name=form['form'],
            valueset=vs,
            word=word,
        )

    for v in args.cldf.iter_rows('norare.csv'):
        variable = data['Variable'][v['Variable_ID']]
        dt = dtypes[v['Variable_ID']]
        try:
            n = dt.parse(v['Value'])
        except:
            print(v['Value'], v)
            raise
        uv = common.UnitValue(
            id=v['ID'],
            name=v['Value'],
            unit=data['Unit'][v['Unit_ID']],
            unitparameter=variable,
            #contribution=,
        )
        if dt.base not in ['string', 'boolean', 'json']:
            # A numeric value.
            uv.number = n
        DBSession.add(uv)


    #for (vsid, sid), pages in refs.items():
    #    DBSession.add(common.ValueSetReference(
    #        valueset=data['ValueSet'][vsid],
    #        source=data['Source'][sid],
    #        description='; '.join(nfilter(pages))
    #    ))



def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """

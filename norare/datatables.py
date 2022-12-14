import json

from sqlalchemy.orm import joinedload
from clld.web import datatables
from clld.web.datatables.base import LinkCol, Col, LinkToMapCol, RefsCol, DetailsRowLinkCol
from clld.web.datatables.unitvalue import Unitvalues
from clld.web.datatables.contribution import Contributions
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.unitparameter import Unitparameters
from clld.web.datatables.value import Values
from clld.db.models import common
from clld.db.util import get_distinct_values
from clld.web.util.htmllib import HTML
from clld_markdown_plugin import markdown

from norare import models


class VariableCol(Col):
    def __init__(self, dt, name, **kw):
        Col.__init__(self, dt, name, **kw)
        self.model_col = getattr(models.Variable, self.name)
        self.choices = get_distinct_values(self.model_col)

    def search(self, qs):
        return getattr(models.Variable, self.name) == qs

    def format(self, item):
        obj = self.get_obj(item)
        if self.name != 'category':
            return getattr(obj, self.name)
        return HTML.div(
            getattr(obj, self.name),
            class_='dt-full-cell {}'.format(obj.category))


class WordCol(Col):
    def format(self, item):
        return item.unit.name


class ValueCol(Col):
    def format(self, item):
        if self.csvw and self.csvw.valueUrl:
            return HTML.a(item.name, href=self.csvw.valueUrl.expand(Value=item.name))
        if self.csvw and self.csvw.datatype.base == 'json':
            return HTML.pre(json.dumps(json.loads(item.name), indent=2))
        return item.name


class Norare(Unitvalues):
    __constraints__ = Unitvalues.__constraints__ + [common.Parameter]

    def base_query(self, query):
        if self.parameter:
            query = query\
                .join(common.Unit, common.UnitValue.unit_pk == common.Unit.pk)\
                .join(models.Concept, common.Unit.pk == models.Concept.word_pk)\
                .join(common.ValueSet, models.Concept.valueset_pk == common.ValueSet.pk)\
                .join(common.Parameter, common.ValueSet.parameter_pk == common.Parameter.pk)\
                .join(common.UnitValue.unitparameter)
            query = query.filter(common.Parameter.pk == self.parameter.pk)
            return query.options(joinedload(common.UnitValue.unitparameter))
        if self.unitparameter:
            query = query \
                .join(common.Unit, common.UnitValue.unit_pk == common.Unit.pk) \
                .join(models.Concept, common.Unit.pk == models.Concept.word_pk) \
                .join(common.ValueSet, models.Concept.valueset_pk == common.ValueSet.pk) \
                .join(common.Parameter, common.ValueSet.parameter_pk == common.Parameter.pk) \
                .join(common.UnitValue.unitparameter)\
                .filter(common.UnitValue.unitparameter_pk == self.unitparameter.pk)
            return query.options(
                joinedload(common.UnitValue.unitparameter),
                joinedload(common.UnitValue.unit).joinedload(common.Unit.concept),
            )
        return Unitvalues.base_query(self, query)
    #    return query.options(
    #        joinedload(common.UnitValue.unit).joinedload(common.Unit.concept).joinedload(common.Value.valueset).joinedload(common.ValueSet.parameter)
    #    )

    def col_defs(self):
        if self.unitparameter and self.unitparameter.datatype.base not in ['string', 'boolean', 'json']:
            res = [Col(self, 'number', model_col=models.Norare.number, sTitle='Value', format=lambda i: i.number)]
        else:
            res = [ValueCol(self, 'name', sTitle='Value', csvw=self.unitparameter.csvwcolumn if self.unitparameter else None)]
            if self.unitparameter and self.unitparameter.domain:
                res[0].choices = [de.name for de in self.unitparameter.domain]
        res.append(WordCol(self, 'word', model_col=common.Unit.name))

        if self.parameter:
            res.extend([
                LinkCol(self, 'variable', get_object=lambda i: i.unitparameter),
                VariableCol(self, 'category',get_object=lambda i: i.unitparameter),
                VariableCol(self, 'type',get_object=lambda i: i.unitparameter),
                VariableCol(self, 'result',get_object=lambda i: i.unitparameter),
                # add language
            ])
        else:
            res.append(
                LinkCol(
                    self,
                    'concept',
                    model_col=common.Parameter.name,
                    get_object=lambda i: i.unit.concept.valueset.parameter)
            )
        return res


class DescriptionCol(Col):
    __kw__ = dict(bSortable=False, bSearchable=False)

    def format(self, item):
        return markdown(self.dt.req, item.description)


class Datasets(Contributions):
    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            DescriptionCol(self, 'description'),
            RefsCol(self, 'source'),
        ]

    def get_options(self):
        return {'iDisplayLength': 150}


class Conceptsets(Parameters):
    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            DetailsRowLinkCol(self, '#', button_text='definition'),
            Col(self, 'glosses_english', sTitle='English Glosses', model_col=models.Conceptset.glosses_english),
            Col(self, 'glosses_german', sTitle='German Glosses', model_col=models.Conceptset.glosses_german),
            Col(self, 'glosses_french', sTitle='French Glosses', model_col=models.Conceptset.glosses_french),
            Col(self, 'glosses_spanish', sTitle='Spanish Glosses', model_col=models.Conceptset.glosses_spanish),
            Col(self, 'glosses_chinese', sTitle='Chinese Glosses', model_col=models.Conceptset.glosses_chinese),
            Col(self, 'glosses_russian', sTitle='Russian Glosses', model_col=models.Conceptset.glosses_russian),
            Col(self, 'glosses_portuguese', sTitle='Portuguese Glosses', model_col=models.Conceptset.glosses_portuguese),
        ]


class Variables(Unitparameters):
    __constraints__ = [common.Contribution]

    def base_query(self, query):
        query = query.join(models.Variable.dataset).join(models.Variable.language)
        if self.contribution:
            query = query.filter(models.Variable.dataset_pk == self.contribution.pk)
        return query

    def col_defs(self):
        return [
            LinkCol(self, 'id'),
            LinkCol(
                self,
                'language',
                choices=get_distinct_values(common.Language.name),
                model_col=common.Language.name,
                get_object=lambda i: i.language),
            VariableCol(self, 'category'),
            VariableCol(self, 'type'),
            VariableCol(self, 'result'),
        ]


class Words(Values):
    def base_query(self, query):
        if self.language:
            return query\
                .join(common.Value.valueset)\
                .join(common.ValueSet.contribution) \
                .join(common.ValueSet.parameter)\
                .join(common.ValueSet.language)\
                .filter(common.Language.pk == self.language.pk)
        return Values.base_query(self, query)

    def col_defs(self):
        return [
            Col(self, 'name'),
            LinkCol(
                self,
                'parameter',
                sTitle=self.req.translate('Parameter'),
                model_col=common.Parameter.name,
                get_object=lambda i: i.valueset.parameter),
            LinkCol(
                self,
                'contribution',
                sTitle=self.req.translate('Contribution'),
                model_col=common.Contribution.name,
                get_object=lambda i: i.valueset.contribution),
        ]


def includeme(config):
    config.register_datatable('unitvalues', Norare)
    config.register_datatable('contributions', Datasets)
    config.register_datatable('parameters', Conceptsets)
    config.register_datatable('unitparameters', Variables)
    config.register_datatable('values', Words)

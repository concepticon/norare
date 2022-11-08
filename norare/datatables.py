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
        return getattr(self.get_obj(item), self.name)


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
        return Unitvalues.base_query(self, query)
    #    return query.options(
    #        joinedload(common.UnitValue.unit).joinedload(common.Unit.concept).joinedload(common.Value.valueset).joinedload(common.ValueSet.parameter)
    #    )

    def col_defs(self):
        res = [Col(self, 'name')] + Unitvalues.col_defs(self)[1:]
        if self.parameter:
            res.extend([
                LinkCol(self, 'variable', get_object=lambda i: i.unitparameter),
                VariableCol(self, 'category',get_object=lambda i: i.unitparameter),
                VariableCol(self, 'structure',get_object=lambda i: i.unitparameter),
                VariableCol(self, 'tag',get_object=lambda i: i.unitparameter),
                # add language
            ])
        else:
            res.append(
                LinkCol(self, 'concept', get_object=lambda i: i.unit.concept.valueset.parameter)
            )
        return res


class DescriptionCol(Col):
    __kw__ = dict(bSortable=False, bSearchable=False)

    def format(self, item):
        return markdown(self.dt.req, item.description)


class Datasets(Contributions):
    def col_defs(self):
        res = Contributions.col_defs(self)[:-1]
        res.insert(1, DescriptionCol(self, 'description'))
        res.append(RefsCol(self, 'source'))
        return res

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
        query = query.join(models.Variable.dataset)
        if self.contribution:
            query = query.filter(models.Variable.dataset_pk == self.contribution.pk)
        return query

    def col_defs(self):
        return [
            LinkCol(self, 'id'),
            VariableCol(self, 'category'),
            VariableCol(self, 'structure'),
            VariableCol(self, 'tag'),
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

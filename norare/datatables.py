from sqlalchemy.orm import joinedload
from clld.web import datatables
from clld.web.datatables.base import LinkCol, Col, LinkToMapCol
from clld.web.datatables.unitvalue import Unitvalues
from clld.web.datatables.contribution import Contributions
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.unitparameter import Unitparameters
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
        res = Contributions.col_defs(self)
        res.insert(1, DescriptionCol(self, 'description'))
        return res

    def get_options(self):
        return {'iDisplayLength': 150}


class Conceptsets(Parameters):
    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            Col(self, 'glosses_english', model_col=models.Conceptset.glosses_english),
            Col(self, 'glosses_german', model_col=models.Conceptset.glosses_german),
            Col(self, 'glosses_french', model_col=models.Conceptset.glosses_french),
            Col(self, 'glosses_spanish', model_col=models.Conceptset.glosses_spanish),
            Col(self, 'glosses_chinese', model_col=models.Conceptset.glosses_chinese),
            Col(self, 'glosses_russian', model_col=models.Conceptset.glosses_russian),
            Col(self, 'glosses_portuguese', model_col=models.Conceptset.glosses_portuguese),
            # DetailsRowLink to open definition!
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


def includeme(config):
    config.register_datatable('unitvalues', Norare)
    config.register_datatable('contributions', Datasets)
    config.register_datatable('parameters', Conceptsets)
    config.register_datatable('unitparameters', Variables)

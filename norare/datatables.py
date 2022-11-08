from sqlalchemy.orm import joinedload
from clld.web import datatables
from clld.web.datatables.base import LinkCol, Col, LinkToMapCol
from clld.web.datatables.unitvalue import Unitvalues
from clld.web.datatables.contribution import Contributions
from clld.web.datatables.parameter import Parameters
from clld.db.models import common
from clld.db.util import get_distinct_values
from clld_markdown_plugin import markdown

from norare import models


class CategoryCol(Col):
    def search(self, qs):
        return models.Variable.category == qs

    def order(self):
        return models.Variable.category

    def format(self, item):
        return self.get_obj(item).category


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
        res = Unitvalues.col_defs(self)
        if self.parameter:
            # add variable (and dataset?), word, datatype,
            # Variable.category as choice column!
            res.extend([
                LinkCol(self, 'variable', get_object=lambda i: i.unitparameter),
                CategoryCol(
                    self,
                    'category',
                    model_col=models.Variable.category,
                    get_object=lambda i: i.unitparameter,
                    choices=get_distinct_values(models.Variable.category)),
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


def includeme(config):
    config.register_datatable('unitvalues', Norare)
    config.register_datatable('contributions', Datasets)
    config.register_datatable('parameters', Conceptsets)

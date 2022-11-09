from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    Float,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from csvw import metadata

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models import common

#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------

@implementer(interfaces.IParameter)
class Conceptset(CustomModelMixin, common.Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    concepticon_id = Column(Unicode)
    glosses_english = Column(Unicode)
    glosses_german = Column(Unicode)
    glosses_french = Column(Unicode)
    glosses_spanish = Column(Unicode)
    glosses_chinese = Column(Unicode)
    glosses_russian = Column(Unicode)
    glosses_portuguese = Column(Unicode)


@implementer(interfaces.IValue)
class Concept(CustomModelMixin, common.Value):
    """A word as used within a dataset."""
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)

    word_pk = Column(Integer, ForeignKey('unit.pk'))
    word = relationship(common.Unit, backref=backref('concept', uselist=False))

#
# Dataset -> Contribution
#

@implementer(interfaces.IContribution)
class NorareDataset(CustomModelMixin, common.Contribution):
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
    # ID,Name,Description,Contributor,Citation,Year,Source,URL,Alias
    citation = Column(Unicode)
    year = Column(Integer)
    url = Column(Unicode)
    alias = Column(Unicode)

#
# Form -> Unit
#

#
# unit-parameter -> UnitParameter
# - relationship(Contribution)
#
@implementer(interfaces.IUnitParameter)
class Variable(CustomModelMixin, common.UnitParameter):
    pk = Column(Integer, ForeignKey('unitparameter.pk'), primary_key=True)

    dataset_pk = Column(Integer, ForeignKey('noraredataset.pk'))
    dataset = relationship(NorareDataset, backref='variables')
    language_pk = Column(Integer, ForeignKey('language.pk'))
    language = relationship(common.Language, backref='variables')
    category = Column(Unicode)
    other = Column(Unicode)
    structure = Column(Unicode)
    rating = Column(Unicode)
    tag = Column(Unicode)
    # types: bool, number, string (categorical), json

    @property
    def csvwcolumn(self):
        return metadata.Column.fromvalue(self.jsondata)

    @property
    def datatype(self):
        return self.csvwcolumn.datatype


@implementer(interfaces.IUnitValue)
class Norare(CustomModelMixin, common.UnitValue):
    pk = Column(Integer, ForeignKey('unitvalue.pk'), primary_key=True)
    #
    number = Column(Float)

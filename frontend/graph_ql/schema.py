import graphene
from graph_ql.query import Query
from graph_ql.typesdefs import Bills, Members

schema = graphene.Schema(
    query = Query, types=[Bills, Members]
)
from experta import Fact, Field


class PruneNode(Fact):
    node_id = Field(str)
    reason = Field(str)


class ValidCargo(Fact):
    node_id = Field(str)

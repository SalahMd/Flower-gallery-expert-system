from experta import Fact, Field


class PruneNode(Fact):
    node_id = Field(str)
    reason = Field(str)


class ValidCargo(Fact):
    node_id = Field(str)


class InvalidCargo(Fact):
    node_id = Field(str)
    reason = Field(str)


class ValidMove(Fact):
    node_id = Field(str)


class InvalidMove(Fact):
    node_id = Field(str)
    reason = Field(str)


class ValidLoad(Fact):
    node_id = Field(str)


class InvalidLoad(Fact):
    node_id = Field(str)
    reason = Field(str)


class ValidUnload(Fact):
    node_id = Field(str)


class InvalidUnload(Fact):
    node_id = Field(str)
    reason = Field(str)

from experta import Fact, Field


class CargoItem(Fact):
    node_id = Field(str)
    flower_type = Field(str)
    color = Field(str)
    quantity = Field(int)


class MaxCapacity(Fact):
    value = Field(int)


class TotalCargoCount(Fact):
    node_id = Field(str)
    count = Field(int)


class MixedCargo(Fact):
    node_id = Field(str)


class OverCapacity(Fact):
    node_id = Field(str)

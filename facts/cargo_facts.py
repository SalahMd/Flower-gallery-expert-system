from experta import Fact, Field


class CargoItem(Fact):
    node_id = Field(str)
    flower_type = Field(str)
    color = Field(str)
    quantity = Field(int)


class CargoFlowerType(Fact):
    node_id = Field(str)
    flower_type = Field(str)


class CargoColor(Fact):
    node_id = Field(str)
    color = Field(str)


class CargoFlowerTypeCount(Fact):
    node_id = Field(str)
    count = Field(int)


class CargoColorCount(Fact):
    node_id = Field(str)
    count = Field(int)


class MaxCapacity(Fact):
    value = Field(int)


class TotalCargoCount(Fact):
    node_id = Field(str)
    count = Field(int)


class MixedCargo(Fact):
    node_id = Field(str)


class OverCapacity(Fact):
    node_id = Field(str)


class CargoMatchesPavilion(Fact):
    node_id = Field(str)
    pavilion_id = Field(str)


class CargoMatchesPavilionColor(Fact):
    node_id = Field(str)
    pavilion_id = Field(str)
    color = Field(str)


class CargoMatchesPavilionFlower(Fact):
    node_id = Field(str)
    pavilion_id = Field(str)
    flower_type = Field(str)

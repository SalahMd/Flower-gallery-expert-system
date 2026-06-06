from experta import Fact, Field


class Grid(Fact):
    rows = Field(int)
    cols = Field(int)


class Warehouse(Fact):
    row = Field(int)
    col = Field(int)


class WarehouseStock(Fact):
    flower_type = Field(str)
    color = Field(str)


class Pavilion(Fact):
    id = Field(str)
    row = Field(int)
    col = Field(int)


class PavilionNeed(Fact):
    pavilion_id = Field(str)
    flower_type = Field(str)
    color = Field(str)
    quantity = Field(int)


class PavilionBouquetTotal(Fact):
    pavilion_id = Field(str)
    total = Field(int)

from experta import Fact, Field


class Grid(Fact):
    rows = Field(int)
    cols = Field(int)


class Cell(Fact):
    row = Field(int)
    col = Field(int)


class NeighborCell(Fact):
    row = Field(int)
    col = Field(int)
    direction = Field(str)
    next_row = Field(int)
    next_col = Field(int)


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


class FlowerKind(Fact):
    flower_type = Field(str)


class FlowerColor(Fact):
    color = Field(str)


class Bouquet(Fact):
    flower_type = Field(str)
    color = Field(str)


class PavilionNeed(Fact):
    pavilion_id = Field(str)
    flower_type = Field(str)
    color = Field(str)
    quantity = Field(int)


class PavilionBouquetTotal(Fact):
    pavilion_id = Field(str)
    total = Field(int)


class PavilionColorNeedTotal(Fact):
    pavilion_id = Field(str)
    color = Field(str)
    total = Field(int)


class PavilionFlowerNeedTotal(Fact):
    pavilion_id = Field(str)
    flower_type = Field(str)
    total = Field(int)

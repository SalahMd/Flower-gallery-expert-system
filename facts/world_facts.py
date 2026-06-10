from experta import Fact, Field


class Grid(Fact):
    rows = Field(int, mandatory=True)
    cols = Field(int, mandatory=True)


class Cell(Fact):
    row = Field(int, mandatory=True)
    col = Field(int, mandatory=True)


class NeighborCell(Fact):
    from_row = Field(int, mandatory=True)
    from_col = Field(int, mandatory=True)
    direction = Field(str, mandatory=True)
    to_row = Field(int, mandatory=True)
    to_col = Field(int, mandatory=True)


class Warehouse(Fact):
    row = Field(int, mandatory=True)
    col = Field(int, mandatory=True)


class WarehouseStock(Fact):
    flower_type = Field(str, mandatory=True)
    color = Field(str, mandatory=True)


class Pavilion(Fact):
    id = Field(str, mandatory=True)
    row = Field(int, mandatory=True)
    col = Field(int, mandatory=True)


class FlowerKind(Fact):
    name = Field(str, mandatory=True)


class FlowerColor(Fact):
    name = Field(str, mandatory=True)


class Bouquet(Fact):
    flower_type = Field(str, mandatory=True)
    color = Field(str, mandatory=True)


class PavilionNeed(Fact):
    pavilion_id = Field(str, mandatory=True)
    flower_type = Field(str, mandatory=True)
    color = Field(str, mandatory=True)
    quantity = Field(int, mandatory=True)


class PavilionBouquetTotal(Fact):
    pavilion_id = Field(str, mandatory=True)
    total = Field(int, mandatory=True)


class PavilionColorNeedTotal(Fact):
    pavilion_id = Field(str, mandatory=True)
    color = Field(str, mandatory=True)
    total = Field(int, mandatory=True)


class PavilionFlowerNeedTotal(Fact):
    pavilion_id = Field(str, mandatory=True)
    flower_type = Field(str, mandatory=True)
    total = Field(int, mandatory=True)
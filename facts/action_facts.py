from experta import Fact, Field


class MoveAction(Fact):
    parent_id = Field(str)
    child_id = Field(str)
    direction = Field(str)
    row = Field(int)
    col = Field(int)
    cost = Field(int)


class LoadAction(Fact):
    parent_id = Field(str)
    child_id = Field(str)
    flower_type = Field(str)
    color = Field(str)
    quantity = Field(int)
    cost = Field(int)


class UnloadBouquetAction(Fact):
    parent_id = Field(str)
    child_id = Field(str)
    pavilion_id = Field(str)
    flower_type = Field(str)
    color = Field(str)
    quantity = Field(int)
    cost = Field(int)


class UnloadColorAction(Fact):
    parent_id = Field(str)
    child_id = Field(str)
    pavilion_id = Field(str)
    color = Field(str)
    quantity = Field(int)
    cost = Field(int)


class UnloadPavilionAction(Fact):
    parent_id = Field(str)
    child_id = Field(str)
    pavilion_id = Field(str)
    quantity = Field(int)
    cost = Field(int)

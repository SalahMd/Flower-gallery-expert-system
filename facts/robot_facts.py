from experta import Fact, Field


class RobotPosition(Fact):
    node_id = Field(str)
    row = Field(int)
    col = Field(int)


class RobotState(Fact):
    node_id = Field(str)
    row = Field(int)
    col = Field(int)


class AtWarehouse(Fact):
    node_id = Field(str)


class AtPavilion(Fact):
    node_id = Field(str)
    pavilion_id = Field(str)


class RobotCapacity(Fact):
    value = Field(int)


class RobotEmpty(Fact):
    node_id = Field(str)


class RobotHasCargo(Fact):
    node_id = Field(str)

from experta import *
 
from models.state import State
from models.grid import Grid
from models.robot import Robot

class Robot(Fact):
    pass

class Grid(Fact):
    pass

class SearchNode(Fact):
    pass

class GoalReached(Fact):
    pass

class ConstraintViolation(Fact):
    pass

class FlowerEngineBase(KnowledgeEngine):

    def __init__(self):
        super().__init__()
        self._nodes_generated: int = 0
        self._nodes_expanded: int = 0
        self._goal_state: State | None = None
 
 
    @property
    def nodes_generated(self) -> int:
        return self._nodes_generated
 
    @property
    def nodes_expanded(self) -> int:
        return self._nodes_expanded
 
    @property
    def goal_state(self) -> State | None:
        return self._goal_state
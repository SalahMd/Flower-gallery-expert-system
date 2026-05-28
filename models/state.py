from dataclasses import dataclass

from models.grid import Grid
from models.robot import Robot


@dataclass
class State:
    grid: Grid
    robot: Robot
    g_cost: float = 0
    h_cost: float = 0
    parent: object = None
    action: str = "START"

    def f_cost(self):
        return self.g_cost + self.h_cost

    def is_goal(self):
        for p in self.grid.pavilions:
            if not p.is_satisfied:
                return False
        return True

    def solution_path(self):
        path = []
        node = self

        while node is not None:
            path.append(node)
            node = node.parent

        path.reverse()
        return path

    def __repr__(self):
        return (
            f"State(action={self.action}, "
            f"g={self.g_cost}, h={self.h_cost}, "
            f"robot={self.robot.position}, "
            f"goal={self.is_goal()})"
        )
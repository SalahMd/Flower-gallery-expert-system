from experta import KnowledgeEngine,Rule, AS, NOT, MATCH, TEST
from facts.search_facts import (
    Phase, CurrentNode, SearchNode, MoveGenerated, PendingSuccessor,
    StateCopy, ExpandVisited, ExpandStarted, NodeCounter,
)
from facts.robot_facts import RobotState
from facts.world_facts import Grid


class MovementRules(KnowledgeEngine):

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(ExpandVisited(node_id=MATCH.nid)),
        RobotState(node_id=MATCH.nid, row=MATCH.row, col=MATCH.col),
        Grid(rows=MATCH.rows, cols=MATCH.cols),
        NOT(MoveGenerated(parent_id=MATCH.nid, direction="up")),
        TEST(lambda row: row > 0),
    )
    def generate_move_up(self, nid):
        self.declare(ExpandStarted(node_id=nid))
        self.declare(MoveGenerated(parent_id=nid, direction="up"))
        self.declare(PendingSuccessor(slot="up", parent_id=nid))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(ExpandVisited(node_id=MATCH.nid)),
        RobotState(node_id=MATCH.nid, row=MATCH.row, col=MATCH.col),
        Grid(rows=MATCH.rows, cols=MATCH.cols),
        NOT(MoveGenerated(parent_id=MATCH.nid, direction="down")),
        TEST(lambda row, rows: row < rows - 1),
    )
    def generate_move_down(self, nid):
        self.declare(ExpandStarted(node_id=nid))
        self.declare(MoveGenerated(parent_id=nid, direction="down"))
        self.declare(PendingSuccessor(slot="down", parent_id=nid))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(ExpandVisited(node_id=MATCH.nid)),
        RobotState(node_id=MATCH.nid, row=MATCH.row, col=MATCH.col),
        Grid(rows=MATCH.rows, cols=MATCH.cols),
        NOT(MoveGenerated(parent_id=MATCH.nid, direction="left")),
        TEST(lambda col: col > 0),
    )
    def generate_move_left(self, nid):
        self.declare(ExpandStarted(node_id=nid))
        self.declare(MoveGenerated(parent_id=nid, direction="left"))
        self.declare(PendingSuccessor(slot="left", parent_id=nid))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(ExpandVisited(node_id=MATCH.nid)),
        RobotState(node_id=MATCH.nid, row=MATCH.row, col=MATCH.col),
        Grid(rows=MATCH.rows, cols=MATCH.cols),
        NOT(MoveGenerated(parent_id=MATCH.nid, direction="right")),
        TEST(lambda col, cols: col < cols - 1),
    )
    def generate_move_right(self, nid):
        self.declare(ExpandStarted(node_id=nid))
        self.declare(MoveGenerated(parent_id=nid, direction="right"))
        self.declare(PendingSuccessor(slot="right", parent_id=nid))

    @Rule(
        AS.ps << PendingSuccessor(slot="up", parent_id=MATCH.pid),
        AS.mg << MoveGenerated(parent_id=MATCH.pid, direction="up"),
        SearchNode(node_id=MATCH.pid, g_cost=MATCH.g),
        RobotState(node_id=MATCH.pid, row=MATCH.row, col=MATCH.col),
        AS.nc << NodeCounter(value=MATCH.v),
    )
    def apply_move_up(self, ps, mg, pid, g, row, col, nc, v):
        self.retract(ps)
        self.retract(mg)
        self.retract(nc)
        new_id = f"n{v}"
        self.declare(NodeCounter(value=v + 1))
        new_row = row - 1
        new_g = g + 1
        self.declare(SearchNode(
            node_id=new_id, parent_id=pid, action="move_up",
            g_cost=new_g, h_cost=0, f_cost=new_g,
        ))
        self.declare(RobotState(node_id=new_id, row=new_row, col=col))
        self.declare(StateCopy(parent_id=pid, child_id=new_id))

    @Rule(
        AS.ps << PendingSuccessor(slot="down", parent_id=MATCH.pid),
        AS.mg << MoveGenerated(parent_id=MATCH.pid, direction="down"),
        SearchNode(node_id=MATCH.pid, g_cost=MATCH.g),
        RobotState(node_id=MATCH.pid, row=MATCH.row, col=MATCH.col),
        AS.nc << NodeCounter(value=MATCH.v),
    )
    def apply_move_down(self, ps, mg, pid, g, row, col, nc, v):
        self.retract(ps)
        self.retract(mg)
        self.retract(nc)
        new_id = f"n{v}"
        self.declare(NodeCounter(value=v + 1))
        new_row = row + 1
        new_g = g + 1
        self.declare(SearchNode(
            node_id=new_id, parent_id=pid, action="move_down",
            g_cost=new_g, h_cost=0, f_cost=new_g,
        ))
        self.declare(RobotState(node_id=new_id, row=new_row, col=col))
        self.declare(StateCopy(parent_id=pid, child_id=new_id))

    @Rule(
        AS.ps << PendingSuccessor(slot="left", parent_id=MATCH.pid),
        AS.mg << MoveGenerated(parent_id=MATCH.pid, direction="left"),
        SearchNode(node_id=MATCH.pid, g_cost=MATCH.g),
        RobotState(node_id=MATCH.pid, row=MATCH.row, col=MATCH.col),
        AS.nc << NodeCounter(value=MATCH.v),
    )
    def apply_move_left(self, ps, mg, pid, g, row, col, nc, v):
        self.retract(ps)
        self.retract(mg)
        self.retract(nc)
        new_id = f"n{v}"
        self.declare(NodeCounter(value=v + 1))
        new_col = col - 1
        new_g = g + 1
        self.declare(SearchNode(
            node_id=new_id, parent_id=pid, action="move_left",
            g_cost=new_g, h_cost=0, f_cost=new_g,
        ))
        self.declare(RobotState(node_id=new_id, row=row, col=new_col))
        self.declare(StateCopy(parent_id=pid, child_id=new_id))

    @Rule(
        AS.ps << PendingSuccessor(slot="right", parent_id=MATCH.pid),
        AS.mg << MoveGenerated(parent_id=MATCH.pid, direction="right"),
        SearchNode(node_id=MATCH.pid, g_cost=MATCH.g),
        RobotState(node_id=MATCH.pid, row=MATCH.row, col=MATCH.col),
        AS.nc << NodeCounter(value=MATCH.v),
    )
    def apply_move_right(self, ps, mg, pid, g, row, col, nc, v):
        self.retract(ps)
        self.retract(mg)
        self.retract(nc)
        new_id = f"n{v}"
        self.declare(NodeCounter(value=v + 1))
        new_col = col + 1
        new_g = g + 1
        self.declare(SearchNode(
            node_id=new_id, parent_id=pid, action="move_right",
            g_cost=new_g, h_cost=0, f_cost=new_g,
        ))
        self.declare(RobotState(node_id=new_id, row=row, col=new_col))
        self.declare(StateCopy(parent_id=pid, child_id=new_id))

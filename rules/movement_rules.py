from experta import KnowledgeEngine, Rule, AS, NOT, MATCH
from facts.search_facts import (
    Phase, CurrentNode, SearchNode, MoveGenerated, PendingSuccessor,
    StateCopy, ExpandVisited, ExpandStarted, NodeCounter,
)
from facts.robot_facts import RobotState
from facts.world_facts import NeighborCell


class MovementRules(KnowledgeEngine):

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(ExpandVisited(node_id=MATCH.nid)),
        RobotState(node_id=MATCH.nid, row=MATCH.row, col=MATCH.col),
        NeighborCell(
            row=MATCH.row,
            col=MATCH.col,
            direction=MATCH.direction,
            next_row=MATCH.next_row,
            next_col=MATCH.next_col,
        ),
        NOT(MoveGenerated(parent_id=MATCH.nid, direction=MATCH.direction)),
    )
    def generate_move(self, nid, row, col, direction, next_row, next_col):
        self.declare(ExpandStarted(node_id=nid))
        self.declare(MoveGenerated(parent_id=nid, direction=direction, row=next_row, col=next_col))
        self.declare(PendingSuccessor(slot=f"move_{direction}", parent_id=nid))

    @Rule(
        AS.ps << PendingSuccessor(slot=MATCH.slot, parent_id=MATCH.pid),
        MoveGenerated(parent_id=MATCH.pid, direction=MATCH.direction, row=MATCH.next_row, col=MATCH.next_col),
        SearchNode(node_id=MATCH.pid, g_cost=MATCH.g),
        AS.nc << NodeCounter(value=MATCH.v),
    )
    def apply_move(self, ps, pid, direction, next_row, next_col, g, nc, v, slot):
        new_id = f"n{v}"
        self.retract(ps)
        self.retract(nc)
        self.declare(NodeCounter(value=v + 1))
        self.declare(SearchNode(
            node_id=new_id,
            parent_id=pid,
            action=f"move_{direction}",
            g_cost=g + 1,
            h_cost=0,
            f_cost=g + 1,
        ))
        self.declare(RobotState(node_id=new_id, row=next_row, col=next_col))
        self.declare(StateCopy(parent_id=pid, child_id=new_id))

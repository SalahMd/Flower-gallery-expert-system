from experta import KnowledgeEngine, Rule, AS, NOT, MATCH, TEST
from facts.search_facts import (
    Phase, CurrentNode, SearchNode, PendingSuccessor,
    MoveGenerated, ExpandVisited, ExpandStarted,
    NodeCounter, StateCopy,
)
from facts.robot_facts import RobotState
from facts.world_facts import NeighborCell, Warehouse, Pavilion
from facts.robot_facts import AtWarehouse, AtPavilion


class MovementRules(KnowledgeEngine):

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(ExpandVisited(node_id=MATCH.nid)),
        RobotState(node_id=MATCH.nid, row=MATCH.r, col=MATCH.c),
        NeighborCell(from_row=MATCH.r, from_col=MATCH.c, direction=MATCH.d, to_row=MATCH.tr, to_col=MATCH.tc),
        NOT(MoveGenerated(parent_id=MATCH.nid, direction=MATCH.d)),
    )
    def generate_move(self, nid, r, c, d, tr, tc):
        self.declare(ExpandStarted(node_id=nid))
        self.declare(MoveGenerated(parent_id=nid, direction=d))
        self.declare(PendingSuccessor(slot=f"move_{d}", parent_id=nid))
        print(f"[MOVE GEN] node={nid}, dir={d}, to=({tr},{tc})")

    @Rule(
        AS.ps << PendingSuccessor(slot=MATCH.slot, parent_id=MATCH.pid),
        MoveGenerated(parent_id=MATCH.pid, direction=MATCH.d),
        SearchNode(node_id=MATCH.pid, g_cost=MATCH.g),
        RobotState(node_id=MATCH.pid, row=MATCH.r, col=MATCH.c),
        NeighborCell(from_row=MATCH.r, from_col=MATCH.c, direction=MATCH.d, to_row=MATCH.tr, to_col=MATCH.tc),
        AS.nc << NodeCounter(value=MATCH.v),
        TEST(lambda slot, d: slot == f"move_{d}"),
    )
    def apply_move(self, ps, pid, d, g, r, c, tr, tc, nc, v, slot):
        new_id = f"n{v}"
        self.retract(ps)
        self.retract(nc)
        self.declare(NodeCounter(value=v + 1))
        self.declare(SearchNode(
            node_id=new_id,
            parent_id=pid,
            action=f"move_{d}",
            g_cost=g + 1,
            h_cost=0,
            f_cost=g + 1,
        ))
        self.declare(RobotState(node_id=new_id, row=tr, col=tc))
        self.declare(StateCopy(parent_id=pid, child_id=new_id))
        print(f"[MOVE APPLY] new_id={new_id}, parent={pid}, dir={d}, to=({tr},{tc})")

    @Rule(
        StateCopy(parent_id=MATCH.pid, child_id=MATCH.cid),
        RobotState(node_id=MATCH.cid, row=MATCH.row, col=MATCH.col),
        Warehouse(row=MATCH.row, col=MATCH.col),
        NOT(AtWarehouse(node_id=MATCH.cid)),
        salience=25,
    )
    def move_at_warehouse(self, pid, cid, row, col):
        self.declare(AtWarehouse(node_id=cid))

    @Rule(
        StateCopy(parent_id=MATCH.pid, child_id=MATCH.cid),
        RobotState(node_id=MATCH.cid, row=MATCH.row, col=MATCH.col),
        Pavilion(id=MATCH.pav_id, row=MATCH.row, col=MATCH.col),
        NOT(AtPavilion(node_id=MATCH.cid, pavilion_id=MATCH.pav_id)),
        salience=25,
    )
    def move_at_pavilion(self, pid, cid, pav_id, row, col):
        self.declare(AtPavilion(node_id=cid, pavilion_id=pav_id))
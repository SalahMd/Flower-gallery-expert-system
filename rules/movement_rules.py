from experta import KnowledgeEngine, Rule, AS, NOT, MATCH, TEST
from facts.cargo_facts import CargoItem, TotalCargoCount
from facts.search_facts import *
from facts.robot_facts import RobotState
from facts.world_facts import NeighborCell, PavilionNeed, Warehouse, Pavilion
from facts.robot_facts import AtWarehouse, AtPavilion


class MovementRules:

# Robot is empty → only moves that bring it closer to the warehouse are valid
    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(ExpandVisited(node_id=MATCH.nid)),
        TotalCargoCount(node_id=MATCH.nid, count=0),
        NOT(AtWarehouse(node_id=MATCH.nid)),
        RobotState(node_id=MATCH.nid, row=MATCH.r, col=MATCH.c),
        NeighborCell(from_row=MATCH.r, from_col=MATCH.c, direction=MATCH.d,
                    to_row=MATCH.tr, to_col=MATCH.tc),
        Warehouse(row=MATCH.wh_r, col=MATCH.wh_c),
        NOT(MoveGenerated(parent_id=MATCH.nid, direction=MATCH.d)),
        TEST(lambda r, c, tr, tc, wh_r, wh_c:
            (abs(tr - wh_r) + abs(tc - wh_c)) < (abs(r - wh_r) + abs(c - wh_c))),
    )
    def generate_move_empty(self, nid, r, c, d, tr, tc, wh_r, wh_c):
        self.declare(ExpandStarted(node_id=nid))
        self.declare(MoveGenerated(parent_id=nid, direction=d))
        self.declare(PendingSuccessor(slot=f"move_{d}", parent_id=nid))

    # Robot has cargo → only moves toward a pavilion that needs what it carries
    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(ExpandVisited(node_id=MATCH.nid)),
        TotalCargoCount(node_id=MATCH.nid, count=MATCH.cnt),
        TEST(lambda cnt: cnt > 0),
        RobotState(node_id=MATCH.nid, row=MATCH.r, col=MATCH.c),
        CargoItem(node_id=MATCH.nid, flower_type=MATCH.ft, color=MATCH.col),
        NOT(Delivered(node_id=MATCH.nid, pavilion_id=MATCH.pav,
                    flower_type=MATCH.ft, color=MATCH.col)),
        PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col),
        Pavilion(id=MATCH.pav, row=MATCH.pav_r, col=MATCH.pav_c),
        NeighborCell(from_row=MATCH.r, from_col=MATCH.c, direction=MATCH.d,
                    to_row=MATCH.tr, to_col=MATCH.tc),
        NOT(MoveGenerated(parent_id=MATCH.nid, direction=MATCH.d)),
        TEST(lambda r, c, tr, tc, pav_r, pav_c:
            (abs(tr - pav_r) + abs(tc - pav_c)) < (abs(r - pav_r) + abs(c - pav_c))),
    )
    def generate_move_loaded(self, nid, r, c, d, tr, tc, ft, col, pav, pav_r, pav_c, cnt):
        self.declare(ExpandStarted(node_id=nid))
        self.declare(MoveGenerated(parent_id=nid, direction=d))
        self.declare(PendingSuccessor(slot=f"move_{d}", parent_id=nid))

    @Rule(
        AS.ps << PendingSuccessor(slot=MATCH.slot, parent_id=MATCH.pid),
        MoveGenerated(parent_id=MATCH.pid, direction=MATCH.d),
        SearchNode(node_id=MATCH.pid, g_cost=MATCH.g),
        RobotState(node_id=MATCH.pid, row=MATCH.r, col=MATCH.c),
        NeighborCell(from_row=MATCH.r, from_col=MATCH.c, direction=MATCH.d, to_row=MATCH.tr, to_col=MATCH.tc),
        AS.nc << NodeCounter(value=MATCH.v),
        TEST(lambda slot, d: slot == f"move_{d}"),
        salience=100,
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
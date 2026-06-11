from experta import KnowledgeEngine, Rule, AS, NOT, MATCH, TEST
from facts.search_facts import *
from facts.robot_facts import AtWarehouse, RobotState
from facts.cargo_facts import MaxCapacity, TotalCargoCount, CargoItem
from facts.world_facts import WarehouseStock, PavilionNeed
from facts.search_facts import Delivered


class LoadingRules(KnowledgeEngine):

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        CargoItem(node_id=MATCH.nid),
        WarehouseStock(flower_type=MATCH.ft, color=MATCH.col),
        NOT(CargoItem(node_id=MATCH.nid, flower_type=MATCH.ft)),
        NOT(CargoItem(node_id=MATCH.nid, color=MATCH.col)),
        NOT(LoadBlocked(parent_id=MATCH.nid, flower_type=MATCH.ft, color=MATCH.col)),
        salience=15,
    )
    def block_incompatible_load(self, nid, ft, col):
        self.declare(LoadBlocked(parent_id=nid, flower_type=ft, color=col))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(ExpandVisited(node_id=MATCH.nid)),
        AtWarehouse(node_id=MATCH.nid),
        CargoItem(node_id=MATCH.nid, flower_type=MATCH.ft),
        WarehouseStock(flower_type=MATCH.ft, color=MATCH.col),
        PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col),
        NOT(Delivered(node_id=MATCH.nid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
        NOT(LoadGenerated(parent_id=MATCH.nid, flower_type=MATCH.ft, color=MATCH.col)),
        NOT(LoadBlocked(parent_id=MATCH.nid, flower_type=MATCH.ft, color=MATCH.col)),
        TotalCargoCount(node_id=MATCH.nid, count=MATCH.current_count),
        MaxCapacity(value=MATCH.cap),
        TEST(lambda current_count, cap: current_count < cap),
        salience=12,
    )
    def generate_load_same_type(self, nid, ft, col, current_count, cap):
        self.declare(ExpandStarted(node_id=nid))
        self.declare(LoadGenerated(parent_id=nid, flower_type=ft, color=col))
        self.declare(PendingSuccessor(slot=f"load_{ft}_{col}", parent_id=nid))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(ExpandVisited(node_id=MATCH.nid)),
        AtWarehouse(node_id=MATCH.nid),
        WarehouseStock(flower_type=MATCH.ft, color=MATCH.col),
        PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col),
        NOT(Delivered(node_id=MATCH.nid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
        NOT(LoadGenerated(parent_id=MATCH.nid, flower_type=MATCH.ft, color=MATCH.col)),
        NOT(LoadBlocked(parent_id=MATCH.nid, flower_type=MATCH.ft, color=MATCH.col)),
        TotalCargoCount(node_id=MATCH.nid, count=MATCH.current_count),
        MaxCapacity(value=MATCH.cap),
        TEST(lambda current_count, cap: current_count < cap),
        salience=8,
    )
    def generate_load(self, nid, ft, col, current_count, cap):
        self.declare(ExpandStarted(node_id=nid))
        self.declare(LoadGenerated(parent_id=nid, flower_type=ft, color=col))
        self.declare(PendingSuccessor(slot=f"load_{ft}_{col}", parent_id=nid))

    @Rule(
        AS.ps << PendingSuccessor(slot=MATCH.slot, parent_id=MATCH.pid),
        LoadGenerated(parent_id=MATCH.pid, flower_type=MATCH.ft, color=MATCH.col),
        SearchNode(node_id=MATCH.pid, g_cost=MATCH.g),
        RobotState(node_id=MATCH.pid, row=MATCH.r, col=MATCH.c),
        TotalCargoCount(node_id=MATCH.pid, count=MATCH.current_count),
        MaxCapacity(value=MATCH.cap),
        AS.nc << NodeCounter(value=MATCH.v),
        TEST(lambda current_count, cap: current_count < cap),
        TEST(lambda slot, ft, col: slot == f"load_{ft}_{col}"),
        salience=100,
    )
    def apply_load(self, ps, pid, ft, col, g, r, c, current_count, cap, nc, v, slot):
        new_id = f"n{v}"
        self.retract(ps)
        self.retract(nc)
        self.declare(NodeCounter(value=v + 1))
        self.declare(SearchNode(
            node_id=new_id,
            parent_id=pid,
            action=f"load_{ft}_{col}",
            g_cost=g + 1,
            h_cost=0,
            f_cost=g + 1,
        ))
        self.declare(RobotState(node_id=new_id, row=r, col=c))
        self.declare(LoadApply(parent_id=pid, child_id=new_id, flower_type=ft, color=col))

    @Rule(AS.lb << LoadBlocked(parent_id=MATCH.pid), ExpandCleanup(parent_id=MATCH.pid), salience=5)
    def cleanup_load_blocked(self, lb, pid):
        self.retract(lb)
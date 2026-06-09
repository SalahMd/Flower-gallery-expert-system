from experta import KnowledgeEngine, Rule, AS, NOT, MATCH, TEST
from facts.search_facts import (
    Phase, CurrentNode, SearchNode, LoadGenerated, PendingSuccessor,
    LoadApply, ExpandVisited, ExpandStarted, NodeCounter,
)
from facts.robot_facts import AtWarehouse, RobotState
from facts.cargo_facts import MaxCapacity, TotalCargoCount
from facts.world_facts import WarehouseStock, PavilionNeed


class LoadingRules(KnowledgeEngine):

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(ExpandVisited(node_id=MATCH.nid)),
        AtWarehouse(node_id=MATCH.nid),
        WarehouseStock(flower_type=MATCH.ft, color=MATCH.col),
        PavilionNeed(flower_type=MATCH.ft, color=MATCH.col),
        NOT(LoadGenerated(parent_id=MATCH.nid, flower_type=MATCH.ft, color=MATCH.col)),
        TotalCargoCount(node_id=MATCH.nid, count=MATCH.current_count),
        MaxCapacity(value=MATCH.cap),
        TEST(lambda current_count, cap: current_count < cap),
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
    )
    def apply_load(self, ps, pid, ft, col, g, r, c, current_count, cap, nc, v, slot):
        new_id = f"n{v}"
        self.retract(ps)
        self.retract(nc)
        self.declare(NodeCounter(value=v + 1))
        self.declare(SearchNode(node_id=new_id, parent_id=pid, action=f"load_{ft}_{col}", g_cost=g+1, h_cost=0, f_cost=g+1))
        self.declare(RobotState(node_id=new_id, row=r, col=c))
        self.declare(LoadApply(parent_id=pid, child_id=new_id, flower_type=ft, color=col))

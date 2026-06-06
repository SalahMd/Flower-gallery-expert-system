from experta import KnowledgeEngine, Rule, AS, NOT, MATCH, TEST
from facts.search_facts import SearchNode, OpenNode, ClosedNode
from facts.constraint_facts import PruneNode
from facts.cargo_facts import CargoItem, TotalCargoCount, MaxCapacity, MixedCargo, OverCapacity
from facts.constraint_facts import ValidCargo
from facts.constraint_facts import PruneNode
from facts.cargo_facts import MixedCargo, OverCapacity 
from facts.constraint_facts import ValidCargo 


class ConstraintRules (KnowledgeEngine):

    @Rule(
        SearchNode(node_id=MATCH.nid),
        CargoItem(node_id=MATCH.nid, flower_type=MATCH.ft1, color=MATCH.col1),
        CargoItem(node_id=MATCH.nid, flower_type=MATCH.ft2, color=MATCH.col2),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        TEST(lambda ft1, ft2, col1, col2: ft1 != ft2 and col1 != col2),
        NOT(MixedCargo(node_id=MATCH.nid)),
    )
    def flag_mixed_cargo(self, nid):
        self.declare(MixedCargo(node_id=nid))

    @Rule(
        AS.sn << SearchNode(node_id=MATCH.nid),
        MixedCargo(node_id=MATCH.nid),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        NOT(PruneNode(node_id=MATCH.nid, reason="mixed")),
    )
    def prune_mixed(self, sn, nid):
        self.declare(PruneNode(node_id=nid, reason="mixed"))
        self.retract(sn)

    @Rule(
        SearchNode(node_id=MATCH.nid),
        TotalCargoCount(node_id=MATCH.nid, count=MATCH.count),
        MaxCapacity(value=MATCH.cap),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        TEST(lambda count, cap: count > cap),
        NOT(OverCapacity(node_id=MATCH.nid)),
    )
    def flag_over_capacity(self, nid):
        self.declare(OverCapacity(node_id=nid))

    @Rule(
        AS.sn << SearchNode(node_id=MATCH.nid),
        OverCapacity(node_id=MATCH.nid),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        NOT(PruneNode(node_id=MATCH.nid, reason="capacity")),
    )
    def prune_capacity(self, sn, nid):
        self.declare(PruneNode(node_id=nid, reason="capacity"))
        self.retract(sn)

    @Rule(
        SearchNode(node_id=MATCH.nid),
        CargoItem(node_id=MATCH.nid),
        NOT(MixedCargo(node_id=MATCH.nid)),
        NOT(OverCapacity(node_id=MATCH.nid)),
        NOT(ValidCargo(node_id=MATCH.nid)),
    )
    def flag_valid_cargo(self, nid):
        self.declare(ValidCargo(node_id=nid))

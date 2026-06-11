
from experta import *
from facts.robot_facts import RobotState
from facts.search_facts import SearchNode, OpenNode, ClosedNode, Phase
from facts.constraint_facts import PruneNode, ValidCargo
from facts.cargo_facts import *


class ConstraintRules(KnowledgeEngine):

    @Rule(
        Phase(name="score"),
        SearchNode(node_id=MATCH.nid),
        CargoItem(node_id=MATCH.nid, flower_type=MATCH.ft1, color=MATCH.col1),
        CargoItem(node_id=MATCH.nid, flower_type=MATCH.ft2, color=MATCH.col2),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        TEST(lambda ft1, ft2, col1, col2:
             not (ft1 == ft2 and col1 == col2) and ft1 != ft2 and col1 != col2),
        NOT(MixedCargo(node_id=MATCH.nid)),
        salience=25,
    )
    def flag_mixed_cargo(self, nid, ft1, col1, ft2, col2):
        self.declare(MixedCargo(node_id=nid))
    
    @Rule(
        Phase(name="score"),
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
        Phase(name="score"),
        SearchNode(node_id=MATCH.nid),
        TotalCargoCount(node_id=MATCH.nid, count=MATCH.count),
        MaxCapacity(value=MATCH.cap),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        TEST(lambda count, cap: count > cap),
        NOT(OverCapacity(node_id=MATCH.nid)),
    )
    def flag_over_capacity(self, nid, count, cap):
        self.declare(OverCapacity(node_id=nid))

    @Rule(
        Phase(name="score"),
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
        TotalCargoCount(node_id=MATCH.nid, count=MATCH.cnt),
        NOT(MixedCargo(node_id=MATCH.nid)),
        NOT(OverCapacity(node_id=MATCH.nid)),
        NOT(ValidCargo(node_id=MATCH.nid)),
        TEST(lambda cnt: cnt == 0),
        salience=5,
    )
    def flag_valid_empty(self, nid, cnt):
        self.declare(ValidCargo(node_id=nid))

    @Rule(
        SearchNode(node_id=MATCH.nid),
        TotalCargoCount(node_id=MATCH.nid, count=MATCH.cnt),
        CargoItem(node_id=MATCH.nid),
        NOT(MixedCargo(node_id=MATCH.nid)),
        NOT(OverCapacity(node_id=MATCH.nid)),
        NOT(ValidCargo(node_id=MATCH.nid)),
        TEST(lambda cnt: cnt > 0),
        salience=5,
    )
    def flag_valid_cargo(self, nid, cnt):
        self.declare(ValidCargo(node_id=nid))


    @Rule(
    AS.ci << CargoItem(node_id=MATCH.nid),
    PruneNode(node_id=MATCH.nid),
    NOT(OpenNode(node_id=MATCH.nid)),
    NOT(ClosedNode(node_id=MATCH.nid)),
    salience=50,
)
    def cleanup_pruned_cargo(self, ci, nid):
        self.retract(ci)

    @Rule(
        AS.rs << RobotState(node_id=MATCH.nid),
        PruneNode(node_id=MATCH.nid),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        salience=50,
    )
    def cleanup_pruned_robotstate(self, rs, nid):
        self.retract(rs)


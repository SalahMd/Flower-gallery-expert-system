from experta import KnowledgeEngine, Rule, AS, NOT, MATCH, TEST
from facts.search_facts import (
    SearchNode, OpenNode, ClosedNode, ClosedPosSig,
    CargoSnap, DelSnap, StateReady, Phase,
)
from facts.robot_facts import RobotState
from facts.cargo_facts import CargoItem, TotalCargoCount
from facts.search_facts import Delivered
from facts.constraint_facts import PruneNode


class SearchRules(KnowledgeEngine):

    @Rule(
        SearchNode(node_id=MATCH.nid),
        CargoItem(node_id=MATCH.nid, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty),
        NOT(CargoSnap(node_id=MATCH.nid, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty)),
        salience=5,
    )
    def snap_cargo(self, nid, ft, col, qty):
        self.declare(CargoSnap(node_id=nid, flower_type=ft, color=col, quantity=qty))

    @Rule(
        SearchNode(node_id=MATCH.nid),
        RobotState(node_id=MATCH.nid),
        TotalCargoCount(node_id=MATCH.nid, count=MATCH.cnt),
        NOT(CargoItem(node_id=MATCH.nid)),
        NOT(StateReady(node_id=MATCH.nid)),
        salience=5,
    )
    def snap_empty_ready(self, nid, cnt):
        self.declare(StateReady(node_id=nid))

    @Rule(
        SearchNode(node_id=MATCH.nid),
        RobotState(node_id=MATCH.nid),
        NOT(StateReady(node_id=MATCH.nid)),
        NOT(CargoItem(node_id=MATCH.nid, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty)
            & NOT(CargoSnap(
                node_id=MATCH.nid,
                flower_type=MATCH.ft,
                color=MATCH.col,
                quantity=MATCH.qty,
            ))),
        CargoItem(node_id=MATCH.nid),
        salience=6,
    )
    def mark_state_ready(self, nid):
        self.declare(StateReady(node_id=nid))

    @Rule(
        Delivered(node_id=MATCH.nid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col),
        NOT(DelSnap(node_id=MATCH.nid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
        salience=5,
    )
    def snap_delivered(self, nid, pav, ft, col):
        self.declare(DelSnap(node_id=nid, pavilion_id=pav, flower_type=ft, color=col))

    @Rule(
        ClosedNode(node_id=MATCH.nid),
        RobotState(node_id=MATCH.nid, row=MATCH.row, col=MATCH.col),
        SearchNode(node_id=MATCH.nid, g_cost=MATCH.g),
        TotalCargoCount(node_id=MATCH.nid, count=MATCH.cnt),
        StateReady(node_id=MATCH.nid),
        NOT(ClosedPosSig(node_id=MATCH.nid)),
        NOT(CargoItem(node_id=MATCH.nid, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty)
            & NOT(CargoSnap(
                node_id=MATCH.nid,
                flower_type=MATCH.ft,
                color=MATCH.col,
                quantity=MATCH.qty,
            ))),
        NOT(Delivered(node_id=MATCH.nid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)
            & NOT(DelSnap(
                node_id=MATCH.nid,
                pavilion_id=MATCH.pav,
                flower_type=MATCH.ft,
                color=MATCH.col,
            ))),
        salience=50,
    )
    def record_closed_sig(self, nid, row, col, g, cnt):
        self.declare(ClosedPosSig(row=row, col=col, cargo_total=cnt, node_id=nid, g_cost=g))

    # keep the open entry with the better (lower) f/g, drop the worse one
    @Rule(
        AS.on << OpenNode(node_id=MATCH.nid, f_cost=MATCH.f_new, g_cost=MATCH.g_new),
        AS.ob << OpenNode(node_id=MATCH.nid, f_cost=MATCH.f_old, g_cost=MATCH.g_old),
        TEST(lambda f_new, f_old, g_new, g_old:
             (f_new, g_new) != (f_old, g_old) and
             (f_new < f_old or (f_new == f_old and g_new < g_old))),
        salience=80,
    )
    def keep_better_open(self, on, ob, nid, f_new, f_old):
        self.retract(ob)

    @Rule(
        AS.on << OpenNode(node_id=MATCH.nid, f_cost=MATCH.f_new, g_cost=MATCH.g_new),
        AS.ob << OpenNode(node_id=MATCH.nid, f_cost=MATCH.f_old, g_cost=MATCH.g_old),
        TEST(lambda f_new, f_old, g_new, g_old:
             (f_new, g_new) != (f_old, g_old) and
             (f_new > f_old or (f_new == f_old and g_new > g_old))),
        salience=80,
    )
    def drop_worse_open_dup(self, on, ob, nid, f_new, f_old):
        self.retract(on)

    @Rule(
        Phase(name="score"),
        SearchNode(node_id=MATCH.nid, g_cost=MATCH.g),
        RobotState(node_id=MATCH.nid, row=MATCH.r, col=MATCH.c),
        TotalCargoCount(node_id=MATCH.nid, count=MATCH.cnt),
        StateReady(node_id=MATCH.nid),
        ClosedPosSig(row=MATCH.r, col=MATCH.c, cargo_total=MATCH.cnt, node_id=MATCH.old_id, g_cost=MATCH.old_g),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        NOT(PruneNode(node_id=MATCH.nid)),
        NOT(CargoSnap(node_id=MATCH.nid) & NOT(CargoSnap(
            node_id=MATCH.old_id,
            flower_type=MATCH.ft,
            color=MATCH.col,
            quantity=MATCH.qty,
        ))),
        NOT(CargoSnap(node_id=MATCH.old_id) & NOT(CargoSnap(
            node_id=MATCH.nid,
            flower_type=MATCH.ft,
            color=MATCH.col,
            quantity=MATCH.qty,
        ))),
        NOT(DelSnap(node_id=MATCH.nid) & NOT(DelSnap(
            node_id=MATCH.old_id,
            pavilion_id=MATCH.pav,
            flower_type=MATCH.ft,
            color=MATCH.col,
        ))),
        NOT(DelSnap(node_id=MATCH.old_id) & NOT(DelSnap(
            node_id=MATCH.nid,
            pavilion_id=MATCH.pav,
            flower_type=MATCH.ft,
            color=MATCH.col,
        ))),
        TEST(lambda g, old_g: g >= old_g),
        salience=36,
    )
    def prune_dominated_state(self, nid, g, old_g):
        self.declare(PruneNode(node_id=nid, reason="dominated"))
        print(f"[PRUNE DOM] node={nid}, g={g} >= old_g={old_g}")

    @Rule(
        AS.sn << SearchNode(node_id=MATCH.nid),
        PruneNode(node_id=MATCH.nid, reason="dominated"),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        salience=40,
    )
    def drop_dominated_node(self, sn, nid):
        self.retract(sn)
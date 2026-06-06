from experta import KnowledgeEngine, Rule, AS, NOT, MATCH, TEST
from facts.search_facts import (
    SearchNode, OpenNode, ClosedNode, NodeCounter, ClosedPosSig,
    CargoSnap, DelSnap, StateReady, NotBest,
)
from facts.robot_facts import RobotState
from facts.cargo_facts import CargoItem, TotalCargoCount
from facts.search_facts import Delivered


class SearchRules(KnowledgeEngine):

    @Rule(
        SearchNode(node_id=MATCH.nid),
        CargoItem(
            node_id=MATCH.nid, flower_type=MATCH.ft,
            color=MATCH.col, quantity=MATCH.qty,
        ),
        NOT(CargoSnap(
            node_id=MATCH.nid, flower_type=MATCH.ft,
            color=MATCH.col, quantity=MATCH.qty,
        )),
        salience=5,
    )
    def snap_cargo(self, nid, ft, col, qty):
        self.declare(CargoSnap(
            node_id=nid, flower_type=ft, color=col, quantity=qty,
        ))

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

    # FIX BUG 6a: was NOT(CargoItem(...), NOT(CargoSnap(...))) — invalid experta pattern
    # Replaced with a helper that checks the sets directly in Python
    @Rule(
        SearchNode(node_id=MATCH.nid),
        RobotState(node_id=MATCH.nid),
        NOT(StateReady(node_id=MATCH.nid)),
        salience=6,
    )
    def all_cargo_snapped(self, nid):
        if self._all_cargo_snapped(nid):
            self.declare(StateReady(node_id=nid))

    def _all_cargo_snapped(self, node_id):
        cargo_items = set()
        cargo_snaps = set()
        for fact in self.facts.values():
            if isinstance(fact, CargoItem) and fact["node_id"] == node_id:
                cargo_items.add((fact["flower_type"], fact["color"], fact["quantity"]))
            if isinstance(fact, CargoSnap) and fact["node_id"] == node_id:
                cargo_snaps.add((fact["flower_type"], fact["color"], fact["quantity"]))
        return cargo_items == cargo_snaps

    @Rule(
        Delivered(
            node_id=MATCH.nid, pavilion_id=MATCH.pav,
            flower_type=MATCH.ft, color=MATCH.col,
        ),
        NOT(DelSnap(
            node_id=MATCH.nid, pavilion_id=MATCH.pav,
            flower_type=MATCH.ft, color=MATCH.col,
        )),
        salience=5,
    )
    def snap_delivered(self, nid, pav, ft, col):
        self.declare(DelSnap(
            node_id=nid, pavilion_id=pav, flower_type=ft, color=col,
        ))

    @Rule(
        ClosedNode(node_id=MATCH.nid),
        RobotState(node_id=MATCH.nid, row=MATCH.row, col=MATCH.col),
        SearchNode(node_id=MATCH.nid, g_cost=MATCH.g),
        TotalCargoCount(node_id=MATCH.nid, count=MATCH.cnt),
        StateReady(node_id=MATCH.nid),
        NOT(ClosedPosSig(
            row=MATCH.row, col=MATCH.col, cargo_total=MATCH.cnt, node_id=MATCH.nid,
        )),
        salience=50,
    )
    def record_closed_sig(self, nid, row, col, g, cnt):
        self.declare(ClosedPosSig(
            row=row, col=col, cargo_total=cnt, node_id=nid, g_cost=g,
        ))

    # FIX BUG 6b: was four NOT(A, NOT(B)) patterns for cargo and delivery symmetry
    # Replaced with a single helper that compares the two nodes' cargo and delivered sets
    @Rule(
        AS.sn << SearchNode(node_id=MATCH.n2, g_cost=MATCH.g2),
        StateReady(node_id=MATCH.n2),
        SearchNode(node_id=MATCH.n1, g_cost=MATCH.g1),
        ClosedNode(node_id=MATCH.n1),
        RobotState(node_id=MATCH.n2, row=MATCH.row, col=MATCH.col),
        RobotState(node_id=MATCH.n1, row=MATCH.row, col=MATCH.col),
        TotalCargoCount(node_id=MATCH.n2, count=MATCH.t),
        TotalCargoCount(node_id=MATCH.n1, count=MATCH.t),
        NOT(OpenNode(node_id=MATCH.n2)),
        NOT(ClosedNode(node_id=MATCH.n2)),
        TEST(lambda g1, g2, n1, n2: n1 != n2 and g2 >= g1),
        salience=40,
    )
    def prune_duplicate_state(self, sn, n2, n1, g1, g2):
        if self._same_cargo(n1, n2) and self._same_delivered(n1, n2):
            self.declare(NotBest(node_id=n2, eliminated_by=n1))
            self.retract(sn)

    def _same_cargo(self, n1, n2):
        def cargo_set(nid):
            return {
                (f["flower_type"], f["color"], f["quantity"])
                for f in self.facts.values()
                if isinstance(f, CargoSnap) and f["node_id"] == nid
            }
        return cargo_set(n1) == cargo_set(n2)

    def _same_delivered(self, n1, n2):
        def del_set(nid):
            return {
                (f["pavilion_id"], f["flower_type"], f["color"])
                for f in self.facts.values()
                if isinstance(f, DelSnap) and f["node_id"] == nid
            }
        return del_set(n1) == del_set(n2)

    @Rule(
        AS.on << OpenNode(node_id=MATCH.nid, f_cost=MATCH.f_new, g_cost=MATCH.g_new),
        AS.ob << OpenNode(node_id=MATCH.nid, f_cost=MATCH.f_old, g_cost=MATCH.g_old),
        TEST(lambda f_new, f_old, g_new, g_old: (f_new, g_new) != (f_old, g_old) and (f_new < f_old or (f_new == f_old and g_new < g_old))),
        salience=80,
    )
    def keep_better_open(self, on, ob):
        self.retract(ob)

    @Rule(
        AS.on << OpenNode(node_id=MATCH.nid, f_cost=MATCH.f_new, g_cost=MATCH.g_new),
        AS.ob << OpenNode(node_id=MATCH.nid, f_cost=MATCH.f_old, g_cost=MATCH.g_old),
        TEST(lambda f_new, f_old, g_new, g_old: (f_new, g_new) != (f_old, g_old) and (f_new > f_old or (f_new == f_old and g_new > g_old))),
        salience=80,
    )
    def drop_worse_open_dup(self, on, ob):
        self.retract(on)
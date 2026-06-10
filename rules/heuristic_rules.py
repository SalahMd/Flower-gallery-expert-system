from experta import KnowledgeEngine, Rule, AS, NOT, MATCH
from facts.search_facts import (
    Phase, SearchNode, OpenNode, PendingH, HProcessed,
    UnsatisfiedNeed, Delivered, ClosedNode, StateReady,
)
from facts.cargo_facts import TotalCargoCount
from facts.robot_facts import RobotState, AtWarehouse
from facts.world_facts import PavilionNeed, Pavilion, Warehouse


class HeuristicRules(KnowledgeEngine):

    @Rule(
        Phase(name="score"),
        SearchNode(node_id=MATCH.nid),
        StateReady(node_id=MATCH.nid),
        TotalCargoCount(node_id=MATCH.nid),
        NOT(ClosedNode(node_id=MATCH.nid)),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(PendingH(node_id=MATCH.nid)),
        salience=20,
    )
    def init_h(self, nid):
        self.declare(PendingH(node_id=nid, value=0))

    @Rule(
        Phase(name="score"),
        SearchNode(node_id=MATCH.nid),
        PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col),
        Delivered(node_id=MATCH.nid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col),
        NOT(HProcessed(node_id=MATCH.nid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
        salience=15,
    )
    def skip_delivered_need(self, nid, pav, ft, col):
        self.declare(HProcessed(node_id=nid, pavilion_id=pav, flower_type=ft, color=col))

    @Rule(
        Phase(name="score"),
        AS.ph << PendingH(node_id=MATCH.nid, value=MATCH.current_h),
        RobotState(node_id=MATCH.nid, row=MATCH.rr, col=MATCH.rc),
        PavilionNeed(pavilion_id=MATCH.pav_id, flower_type=MATCH.ft, color=MATCH.col),
        Pavilion(id=MATCH.pav_id, row=MATCH.pr, col=MATCH.pc),
        NOT(Delivered(node_id=MATCH.nid, pavilion_id=MATCH.pav_id, flower_type=MATCH.ft, color=MATCH.col)),
        NOT(HProcessed(node_id=MATCH.nid, pavilion_id=MATCH.pav_id, flower_type=MATCH.ft, color=MATCH.col)),
        salience=10,
    )
    def add_need_distance(self, ph, nid, current_h, rr, rc, pav_id, ft, col, pr, pc):
        dist = abs(rr - pr) + abs(rc - pc)
        need_cost = dist + 1
        new_h = current_h if current_h > need_cost else need_cost
        self.retract(ph)
        self.declare(PendingH(node_id=nid, value=new_h))
        self.declare(HProcessed(node_id=nid, pavilion_id=pav_id, flower_type=ft, color=col))
        self.declare(UnsatisfiedNeed(node_id=nid, pavilion_id=pav_id, flower_type=ft, color=col))

    @Rule(
        Phase(name="score"),
        AS.ph << PendingH(node_id=MATCH.nid, value=MATCH.h_val),
        AS.sn << SearchNode(node_id=MATCH.nid, g_cost=MATCH.g, parent_id=MATCH.pid, action=MATCH.act),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(UnsatisfiedNeed(node_id=MATCH.nid)),
        salience=8,
    )
    def h_done_zero(self, ph, sn, nid, h_val, g, pid, act):
        self.retract(ph)
        self.retract(sn)
        self.declare(SearchNode(node_id=nid, parent_id=pid, action=act, g_cost=g, h_cost=0, f_cost=g))
        self.declare(OpenNode(node_id=nid, f_cost=g, g_cost=g))
        print(f"[H ZERO] node={nid}, g={g}, f={g}")

    @Rule(
        Phase(name="score"),
        AS.ph << PendingH(node_id=MATCH.nid, value=MATCH.h_val),
        AS.sn << SearchNode(node_id=MATCH.nid, g_cost=MATCH.g, parent_id=MATCH.pid, action=MATCH.act),
        NOT(OpenNode(node_id=MATCH.nid)),
        UnsatisfiedNeed(node_id=MATCH.nid),
        AtWarehouse(node_id=MATCH.nid),
        salience=8,
    )
    def h_done_at_warehouse(self, ph, sn, nid, h_val, g, pid, act):
        self.retract(ph)
        self.retract(sn)
        self.declare(SearchNode(node_id=nid, parent_id=pid, action=act, g_cost=g, h_cost=h_val, f_cost=g + h_val))
        self.declare(OpenNode(node_id=nid, f_cost=g + h_val, g_cost=g))
        print(f"[H WH] node={nid}, h={h_val}, g={g}, f={g + h_val}")

    @Rule(
        Phase(name="score"),
        AS.ph << PendingH(node_id=MATCH.nid, value=MATCH.h_val),
        AS.sn << SearchNode(node_id=MATCH.nid, g_cost=MATCH.g, parent_id=MATCH.pid, action=MATCH.act),
        RobotState(node_id=MATCH.nid, row=MATCH.rr, col=MATCH.rc),
        Warehouse(row=MATCH.whr, col=MATCH.whc),
        NOT(OpenNode(node_id=MATCH.nid)),
        UnsatisfiedNeed(node_id=MATCH.nid),
        NOT(AtWarehouse(node_id=MATCH.nid)),
        salience=8,
    )
    def h_done_with_wh(self, ph, sn, nid, h_val, g, pid, act, rr, rc, whr, whc):
        dist_to_wh = abs(rr - whr) + abs(rc - whc)
        final_h = h_val + dist_to_wh
        self.retract(ph)
        self.retract(sn)
        self.declare(SearchNode(node_id=nid, parent_id=pid, action=act, g_cost=g, h_cost=final_h, f_cost=g + final_h))
        self.declare(OpenNode(node_id=nid, f_cost=g + final_h, g_cost=g))
        print(f"[H FULL] node={nid}, h={final_h}, g={g}, f={g + final_h}")

    @Rule(
        Phase(name="score"),
        AS.us << UnsatisfiedNeed(node_id=MATCH.nid),
        OpenNode(node_id=MATCH.nid),
        salience=3,
    )
    def cleanup_unsatisfied(self, us, nid):
        self.retract(us)

    @Rule(
        Phase(name="score"),
        AS.hp << HProcessed(node_id=MATCH.nid),
        OpenNode(node_id=MATCH.nid),
        salience=3,
    )
    def cleanup_h_processed(self, hp, nid):
        self.retract(hp)
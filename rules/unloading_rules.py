from experta import KnowledgeEngine,Rule, AS, NOT, MATCH, TEST
from facts.search_facts import (
    Phase, CurrentNode, SearchNode, PendingSuccessor,
    UnloadColorGenerated, UnloadPavilionGenerated,
    UnloadColorApply, UnloadPavilionApply, Delivered,
    PavilionNeedUnmet, PavilionHasExtraCargo, ExpandVisited, ExpandStarted, NodeCounter,
)
from facts.robot_facts import AtPavilion, RobotState
from facts.cargo_facts import CargoItem
from facts.world_facts import PavilionNeed


class UnloadingRules(KnowledgeEngine):

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(ExpandVisited(node_id=MATCH.nid)),
        AtPavilion(node_id=MATCH.nid, pavilion_id=MATCH.pav),
        PavilionNeed(
            pavilion_id=MATCH.pav, flower_type=MATCH.ft,
            color=MATCH.col, quantity=MATCH.needed,
        ),
        CargoItem(
            node_id=MATCH.nid, flower_type=MATCH.ft,
            color=MATCH.col, quantity=MATCH.carried,
        ),
        NOT(UnloadColorGenerated(
            parent_id=MATCH.nid, pavilion_id=MATCH.pav,
            flower_type=MATCH.ft, color=MATCH.col,
        )),
        NOT(Delivered(
            node_id=MATCH.nid, pavilion_id=MATCH.pav,
            flower_type=MATCH.ft, color=MATCH.col,
        )),
        TEST(lambda carried, needed: carried >= needed),
    )
    def generate_unload_color(self, nid, pav, ft, col):
        self.declare(ExpandStarted(node_id=nid))
        self.declare(UnloadColorGenerated(
            parent_id=nid, pavilion_id=pav,
            flower_type=ft, color=col,
        ))
        self.declare(PendingSuccessor(
            slot=f"unload_{pav}_{ft}_{col}", parent_id=nid,
        ))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        AtPavilion(node_id=MATCH.nid, pavilion_id=MATCH.pav),
        PavilionNeed(
            pavilion_id=MATCH.pav, flower_type=MATCH.ft,
            color=MATCH.col, quantity=MATCH.needed,
        ),
        NOT(Delivered(
            node_id=MATCH.nid, pavilion_id=MATCH.pav,
            flower_type=MATCH.ft, color=MATCH.col,
        )),
        NOT(CargoItem(
            node_id=MATCH.nid, flower_type=MATCH.ft, color=MATCH.col,
        )),
        salience=10,   # <-- was missing, defaulted to 0
    )
    def mark_need_unmet_missing(self, nid, pav):
        self.declare(PavilionNeedUnmet(node_id=nid, pavilion_id=pav))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        AtPavilion(node_id=MATCH.nid, pavilion_id=MATCH.pav),
        PavilionNeed(
            pavilion_id=MATCH.pav, flower_type=MATCH.ft,
            color=MATCH.col, quantity=MATCH.needed,
        ),
        CargoItem(
            node_id=MATCH.nid, flower_type=MATCH.ft,
            color=MATCH.col, quantity=MATCH.carried,
        ),
        NOT(Delivered(
            node_id=MATCH.nid, pavilion_id=MATCH.pav,
            flower_type=MATCH.ft, color=MATCH.col,
        )),
        TEST(lambda carried, needed: carried < needed),
        salience=10,   # <-- was missing, defaulted to 0
    )
    def mark_need_unmet_short(self, nid, pav):
        self.declare(PavilionNeedUnmet(node_id=nid, pavilion_id=pav))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        AtPavilion(node_id=MATCH.nid, pavilion_id=MATCH.pav),
        CargoItem(
            node_id=MATCH.nid, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty,
        ),
        NOT(PavilionNeed(
            pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col,
        )),
        salience=10,   # <-- was missing, defaulted to 0
    )
    def mark_extra_cargo(self, nid, pav):
        self.declare(PavilionHasExtraCargo(node_id=nid, pavilion_id=pav))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(ExpandVisited(node_id=MATCH.nid)),
        AtPavilion(node_id=MATCH.nid, pavilion_id=MATCH.pav),
        NOT(UnloadPavilionGenerated(parent_id=MATCH.nid, pavilion_id=MATCH.pav)),
        NOT(PavilionNeedUnmet(node_id=MATCH.nid, pavilion_id=MATCH.pav)),
        NOT(PavilionHasExtraCargo(node_id=MATCH.nid, pavilion_id=MATCH.pav)),
        salience=1,    # <-- fires after all guards above (salience=10) are settled
    )
    def generate_unload_pavilion(self, nid, pav):
        self.declare(ExpandStarted(node_id=nid))
        self.declare(UnloadPavilionGenerated(parent_id=nid, pavilion_id=pav))
        self.declare(PendingSuccessor(slot=f"unload_all_{pav}", parent_id=nid))
    @Rule(
        AS.ps << PendingSuccessor(slot=MATCH.slot, parent_id=MATCH.pid),
        AS.ug << UnloadColorGenerated(
            parent_id=MATCH.pid, pavilion_id=MATCH.pav,
            flower_type=MATCH.ft, color=MATCH.col,
        ),
        SearchNode(node_id=MATCH.pid, g_cost=MATCH.g),
        RobotState(node_id=MATCH.pid, row=MATCH.r, col=MATCH.c),
        AS.nc << NodeCounter(value=MATCH.v),
    )
    def apply_unload_color(self, ps, ug, pid, pav, ft, col, g, r, c, nc, v, slot):
        self.retract(ps)
        self.retract(ug)
        self.retract(nc)
        new_id = f"n{v}"
        self.declare(NodeCounter(value=v + 1))
        new_g = g + 1
        self.declare(SearchNode(
            node_id=new_id, parent_id=pid,
            action=f"unload_{ft}_{col}_at_{pav}",
            g_cost=new_g, h_cost=0, f_cost=new_g,
        ))
        self.declare(RobotState(node_id=new_id, row=r, col=c))
        self.declare(UnloadColorApply(
            parent_id=pid, child_id=new_id,
            pavilion_id=pav, flower_type=ft, color=col,
        ))

    @Rule(
        AS.ps << PendingSuccessor(slot=MATCH.slot, parent_id=MATCH.pid),
        AS.up << UnloadPavilionGenerated(parent_id=MATCH.pid, pavilion_id=MATCH.pav),
        SearchNode(node_id=MATCH.pid, g_cost=MATCH.g),
        RobotState(node_id=MATCH.pid, row=MATCH.r, col=MATCH.c),
        AS.nc << NodeCounter(value=MATCH.v),
    )
    def apply_unload_pavilion(self, ps, up, pid, pav, g, r, c, nc, v, slot):
        self.retract(ps)
        self.retract(up)
        self.retract(nc)
        new_id = f"n{v}"
        self.declare(NodeCounter(value=v + 1))
        new_g = g + 1
        self.declare(SearchNode(
            node_id=new_id, parent_id=pid,
            action=f"unload_all_at_{pav}",
            g_cost=new_g, h_cost=0, f_cost=new_g,
        ))
        self.declare(RobotState(node_id=new_id, row=r, col=c))
        self.declare(UnloadPavilionApply(
            parent_id=pid, child_id=new_id, pavilion_id=pav,
        ))

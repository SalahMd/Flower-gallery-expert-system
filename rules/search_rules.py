from experta import KnowledgeEngine, Rule, AS, NOT, MATCH, TEST
from facts.search_facts import *
from facts.robot_facts import RobotState
from facts.cargo_facts import CargoItem, TotalCargoCount
from facts.constraint_facts import PruneNode


class SearchRules(KnowledgeEngine):

    # ------------------------------------------------------------------ #
    #  Signature accumulation — build StateSig one item at a time        #
    # ------------------------------------------------------------------ #

    @Rule(
        Phase(name="score"),
        SearchNode(node_id=MATCH.nid),
        RobotState(node_id=MATCH.nid),
        NOT(StateSig(node_id=MATCH.nid)),
        NOT(SigAccum(node_id=MATCH.nid)),
        salience=15,
    )
    def start_sig_accum(self, nid):
        self.declare(SigAccum(node_id=nid, cargo="", delivered=""))

    @Rule(
        Phase(name="score"),
        AS.acc << SigAccum(node_id=MATCH.nid, cargo=MATCH.c, delivered=MATCH.d),
        CargoItem(
            node_id=MATCH.nid,
            flower_type=MATCH.ft,
            color=MATCH.col,
            quantity=MATCH.qty,
        ),
        NOT(SigCargoItem(
            node_id=MATCH.nid,
            flower_type=MATCH.ft,
            color=MATCH.col,
            quantity=MATCH.qty,
        )),
        NOT(StateSig(node_id=MATCH.nid)),
        salience=14,
    )
    def accum_cargo_item(self, acc, nid, c, d, ft, col, qty):
        self.retract(acc)
        self.declare(SigAccum(node_id=nid, cargo=c + f"|{ft},{col},{qty}", delivered=d))
        self.declare(SigCargoItem(node_id=nid, flower_type=ft, color=col, quantity=qty))

    @Rule(
        Phase(name="score"),
        AS.acc << SigAccum(node_id=MATCH.nid, cargo=MATCH.c, delivered=MATCH.d),
        Delivered(
            node_id=MATCH.nid,
            pavilion_id=MATCH.pav,
            flower_type=MATCH.ft,
            color=MATCH.col,
        ),
        NOT(SigDeliveredItem(
            node_id=MATCH.nid,
            pavilion_id=MATCH.pav,
            flower_type=MATCH.ft,
            color=MATCH.col,
        )),
        NOT(StateSig(node_id=MATCH.nid)),
        salience=14,
    )
    def accum_delivered_item(self, acc, nid, c, d, pav, ft, col):
        self.retract(acc)
        self.declare(SigAccum(node_id=nid, cargo=c, delivered=d + f"|{pav},{ft},{col}"))
        self.declare(SigDeliveredItem(node_id=nid, pavilion_id=pav, flower_type=ft, color=col))

    @Rule(
        Phase(name="score"),
        AS.acc << SigAccum(node_id=MATCH.nid, cargo=MATCH.c, delivered=MATCH.d),
        NOT(StateSig(node_id=MATCH.nid)),
        salience=13,
    )
    def finalize_sig(self, acc, nid, c, d):
        self.retract(acc)
        self.declare(StateSig(node_id=nid, cargo=c, delivered=d))
        self.declare(StateReady(node_id=nid))

    @Rule(
        AS.sci << SigCargoItem(node_id=MATCH.nid),
        StateSig(node_id=MATCH.nid),
        salience=12,
    )
    def cleanup_sig_cargo_item(self, sci, nid):
        self.retract(sci)

    @Rule(
        AS.sdi << SigDeliveredItem(node_id=MATCH.nid),
        StateSig(node_id=MATCH.nid),
        salience=12,
    )
    def cleanup_sig_delivered_item(self, sdi, nid):
        self.retract(sdi)

    # ------------------------------------------------------------------ #
    #  Domination pruning — prune if closed node has same state at       #
    #  equal or lower cost                                                #
    # ------------------------------------------------------------------ #

    @Rule(
        Phase(name="score"),
        SearchNode(node_id=MATCH.nid, g_cost=MATCH.g),
        RobotState(node_id=MATCH.nid, row=MATCH.r, col=MATCH.c),
        StateSig(node_id=MATCH.nid, cargo=MATCH.cargo, delivered=MATCH.delivered),
        ClosedPosSig(
            row=MATCH.r, col=MATCH.c,
            cargo=MATCH.cargo, delivered=MATCH.delivered,
            g_cost=MATCH.old_g,
        ),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        NOT(PruneNode(node_id=MATCH.nid)),
        TEST(lambda g, old_g: g >= old_g),
        salience=36,
    )
    def prune_dominated_by_closed(self, nid, g):
        self.declare(PruneNode(node_id=nid, reason="dominated"))

    @Rule(
        Phase(name="score"),
        SearchNode(node_id=MATCH.nid, g_cost=MATCH.g),
        RobotState(node_id=MATCH.nid, row=MATCH.r, col=MATCH.c),
        StateSig(node_id=MATCH.nid, cargo=MATCH.cargo, delivered=MATCH.delivered),
        OpenNode(node_id=MATCH.old_id, g_cost=MATCH.old_g),
        StateSig(node_id=MATCH.old_id, cargo=MATCH.cargo, delivered=MATCH.delivered),
        RobotState(node_id=MATCH.old_id, row=MATCH.r, col=MATCH.c),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        NOT(PruneNode(node_id=MATCH.nid)),
        TEST(lambda nid, old_id, g, old_g: nid != old_id and g >= old_g),
        salience=37,
    )
    def prune_dominated_by_open(self, nid, g):
        self.declare(PruneNode(node_id=nid, reason="open_dup"))

    @Rule(
        Phase(name="score"),
        SearchNode(node_id=MATCH.nid, g_cost=MATCH.g),
        RobotState(node_id=MATCH.nid, row=MATCH.r, col=MATCH.c),
        StateSig(node_id=MATCH.nid, cargo=MATCH.cargo, delivered=MATCH.delivered),
        AS.on << OpenNode(node_id=MATCH.old_id, g_cost=MATCH.old_g),
        StateSig(node_id=MATCH.old_id, cargo=MATCH.cargo, delivered=MATCH.delivered),
        RobotState(node_id=MATCH.old_id, row=MATCH.r, col=MATCH.c),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        NOT(PruneNode(node_id=MATCH.nid)),
        TEST(lambda nid, old_id, g, old_g: nid != old_id and g < old_g),
        salience=38,
    )
    def replace_worse_open(self, nid, on, old_id):
        self.retract(on)

    # ------------------------------------------------------------------ #
    #  Record closed signature for future domination checks              #
    # ------------------------------------------------------------------ #

    @Rule(
        Phase(name="score"),
        ClosedNode(node_id=MATCH.nid),
        RobotState(node_id=MATCH.nid, row=MATCH.r, col=MATCH.c),
        SearchNode(node_id=MATCH.nid, g_cost=MATCH.g),
        StateSig(node_id=MATCH.nid, cargo=MATCH.cargo, delivered=MATCH.delivered),
        NOT(ClosedPosSig(node_id=MATCH.nid)),
        salience=50,
    )
    def record_closed_sig(self, nid, r, c, g, cargo, delivered):
        self.declare(ClosedPosSig(
            node_id=nid, row=r, col=c, g_cost=g,
            cargo=cargo, delivered=delivered,
        ))

    # ------------------------------------------------------------------ #
    #  Open-list dedup — keep only best (lowest f then g) per node       #
    # ------------------------------------------------------------------ #

    @Rule(
        AS.worse << OpenNode(node_id=MATCH.nid, f_cost=MATCH.fw, g_cost=MATCH.gw),
        OpenNode(node_id=MATCH.nid, f_cost=MATCH.fb, g_cost=MATCH.gb),
        TEST(lambda fw, fb, gw, gb:
             (fw, gw) != (fb, gb) and (fb < fw or (fb == fw and gb < gw))),
        salience=80,
    )
    def drop_worse_open(self, worse, nid):
        self.retract(worse)

    # ------------------------------------------------------------------ #
    #  Drop pruned nodes from the search graph                           #
    # ------------------------------------------------------------------ #

    @Rule(
        AS.sn << SearchNode(node_id=MATCH.nid),
        PruneNode(node_id=MATCH.nid),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        salience=40,
    )
    def drop_pruned_node(self, sn, nid):
        self.retract(sn)
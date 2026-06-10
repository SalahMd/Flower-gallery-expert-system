from experta import KnowledgeEngine, Rule, AS, NOT, MATCH
from facts.search_facts import (
    Phase, CurrentNode, GoalNode,
    NeedUnmet, NeedUnmetChecked, GoalCheckDone, Delivered,
)
from facts.world_facts import PavilionNeed


class GoalRules(KnowledgeEngine):

    @Rule(
        Phase(name="check_goal"),
        CurrentNode(node_id=MATCH.nid),
        PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col),
        NOT(Delivered(node_id=MATCH.nid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
        NOT(NeedUnmetChecked(node_id=MATCH.nid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
        salience=30,
    )
    def mark_need_unmet(self, nid, pav, ft, col):
        self.declare(NeedUnmet(node_id=nid, pavilion_id=pav, flower_type=ft, color=col))
        self.declare(NeedUnmetChecked(node_id=nid, pavilion_id=pav, flower_type=ft, color=col))
        print(f"[GOAL CHECK] node={nid}, unmet={pav} {ft}-{col}")

    @Rule(
        Phase(name="check_goal"),
        CurrentNode(node_id=MATCH.nid),
        PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col),
        Delivered(node_id=MATCH.nid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col),
        NOT(NeedUnmetChecked(node_id=MATCH.nid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
        salience=30,
    )
    def mark_need_met(self, nid, pav, ft, col):
        self.declare(NeedUnmetChecked(node_id=nid, pavilion_id=pav, flower_type=ft, color=col))

    # all needs checked, none unmet -> goal
    @Rule(
        AS.ph << Phase(name="check_goal"),
        CurrentNode(node_id=MATCH.nid),
        NOT(GoalCheckDone(node_id=MATCH.nid)),
        NOT(NeedUnmet(node_id=MATCH.nid)),
        NOT(PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)
            & NOT(NeedUnmetChecked(
                node_id=MATCH.nid,
                pavilion_id=MATCH.pav,
                flower_type=MATCH.ft,
                color=MATCH.col,
            ))),
        salience=8,
    )
    def reach_goal(self, ph, nid):
        self.declare(GoalCheckDone(node_id=nid))
        self.declare(GoalNode(node_id=nid))
        self.retract(ph)
        print(f"GOAL FOUND: {nid}")

    # at least one need unmet -> expand
    @Rule(
        AS.ph << Phase(name="check_goal"),
        CurrentNode(node_id=MATCH.nid),
        NeedUnmet(node_id=MATCH.nid),
        NOT(GoalCheckDone(node_id=MATCH.nid)),
        salience=5,
    )
    def not_goal_yet(self, ph, nid):
        self.declare(GoalCheckDone(node_id=nid))
        self.retract(ph)
        self.declare(Phase(name="expand"))
        print(f"[PHASE] check_goal -> expand, node={nid}")

    @Rule(AS.nu << NeedUnmet(node_id=MATCH.nid), GoalCheckDone(node_id=MATCH.nid), salience=2)
    def cleanup_need_unmet(self, nu, nid):
        self.retract(nu)

    @Rule(AS.nc << NeedUnmetChecked(node_id=MATCH.nid), GoalCheckDone(node_id=MATCH.nid), salience=2)
    def cleanup_need_unmet_checked(self, nc, nid):
        self.retract(nc)
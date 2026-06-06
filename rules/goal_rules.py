from experta import KnowledgeEngine, Rule, AS, NOT, MATCH
from facts.search_facts import Phase, CurrentNode, GoalNode, Delivered
from facts.world_facts import PavilionNeed


class GoalRules(KnowledgeEngine):

    @Rule(
        AS.ph << Phase(name="check_goal"),
        CurrentNode(node_id=MATCH.nid),
        PavilionNeed(
            pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col,
        ),
        NOT(Delivered(
            node_id=MATCH.nid, pavilion_id=MATCH.pav,
            flower_type=MATCH.ft, color=MATCH.col,
        )),
        salience=50,
    )
    def need_expand(self, ph, nid, pav, ft, col):
        self.retract(ph)
        self.declare(Phase(name="expand"))

    @Rule(
        Phase(name="check_goal"),
        CurrentNode(node_id=MATCH.nid),
        NOT(GoalNode()),
        salience=100,
    )
    def reach_goal(self, nid):
        if self._all_delivered(nid):
            self.declare(GoalNode(node_id=nid))

    def _all_delivered(self, nid):
        needs = {
            (f["pavilion_id"], f["flower_type"], f["color"])
            for f in self.facts.values() if isinstance(f, PavilionNeed)
        }
        delivered = {
            (f["pavilion_id"], f["flower_type"], f["color"])
            for f in self.facts.values()
            if isinstance(f, Delivered) and f["node_id"] == nid
        }
        return needs <= delivered
from experta import KnowledgeEngine, Rule, AS, NOT, MATCH
from facts.search_facts import Phase, CurrentNode, GoalNode, Delivered
from facts.world_facts import PavilionNeed


class GoalRules(KnowledgeEngine):

    @Rule(
        Phase(name="check_goal"),
        CurrentNode(node_id=MATCH.nid),
        PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col),
        NOT(Delivered(node_id=MATCH.nid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
        salience=200,
    )
    def need_expand(self, ph, nid, pav, ft, col):
        print("GOAL NOT YET")
        self.retract(ph)
        self.declare(Phase(name="expand"))


    @Rule(
        Phase(name="check_goal"),
        CurrentNode(node_id=MATCH.nid),
        NOT(
            PavilionNeed(
                pavilion_id=MATCH.pav,
                flower_type=MATCH.ft,
                color=MATCH.col
            ) & NOT(
                Delivered(
                    node_id=MATCH.nid,
                    pavilion_id=MATCH.pav,
                    flower_type=MATCH.ft,
                    color=MATCH.col
                )
            )
        ),
    )
    def reach_goal(self, nid):
        print("GOAL FOUND:", nid)
        self.declare(GoalNode(node_id=nid))

    @Rule(
    Phase(name="check_goal"),
    CurrentNode(node_id=MATCH.nid),
    PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col),
    NOT(Delivered(node_id=MATCH.nid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
)
    def still_not_goal(self, ph, nid):
        print("GOAL NOT YET")
        self.retract(ph)
        self.declare(Phase(name="expand"))    
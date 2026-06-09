from experta import KnowledgeEngine, Rule, AS, NOT, MATCH, TEST
from facts.search_facts import (
    SearchNode, OpenNode, ClosedNode, CurrentNode, GoalNode,
    SearchStopped, Phase, PendingSuccessor, MoveGenerated, LoadGenerated,
    UnloadColorGenerated, UnloadPavilionGenerated, ExpandCleanup, ExpandVisited,
    ExpandStarted, NeedScore, PendingH, NotBest,
)
from rules.movement_rules import MovementRules
from rules.loading_rules import LoadingRules
from rules.unloading_rules import UnloadingRules
from rules.transition_rules import TransitionRules
from rules.constraint_rules import ConstraintRules
from rules.heuristic_rules import HeuristicRules
from rules.goal_rules import GoalRules
from rules.search_rules import SearchRules
from rules.output_rules import OutputRules


class AStarEngine(
    MovementRules,
    LoadingRules,
    UnloadingRules,
    TransitionRules,
    ConstraintRules,
    HeuristicRules,
    GoalRules,
    SearchRules,
    OutputRules,
    KnowledgeEngine,
):

    @Rule(
        Phase(name="select"),
        OpenNode(node_id=MATCH.worse, f_cost=MATCH.f1, g_cost=MATCH.g1),
        OpenNode(node_id=MATCH.better, f_cost=MATCH.f2, g_cost=MATCH.g2),
        TEST(lambda worse, better, f1, g1, f2, g2:
             worse != better and (f2 < f1 or (f2 == f1 and g2 < g1))),
        NOT(NotBest(node_id=MATCH.worse, eliminated_by=MATCH.better)),
        salience=30,
    )
    def mark_not_best_open(self, worse, better, f1, g1, f2, g2):
        self.declare(NotBest(node_id=worse, eliminated_by=better))

    # if the node that eliminated 'worse' is itself gone, the NotBest fact is stale
    @Rule(
        AS.nb << NotBest(node_id=MATCH.nid, eliminated_by=MATCH.best),
        NOT(OpenNode(node_id=MATCH.best)),
        salience=25,
    )
    def cleanup_stale_not_best(self, nb, nid, best):
        self.retract(nb)

    # select the single best open node (no NotBest fact means nothing beats it)
    @Rule(
        AS.ph << Phase(name="select"),
        AS.best << OpenNode(node_id=MATCH.nid, f_cost=MATCH.f, g_cost=MATCH.g),
        NOT(NotBest(node_id=MATCH.nid)),
        NOT(GoalNode()),
        salience=10,
    )
    def select_best_open(self, ph, best, nid, f, g):
        self.retract(best)
        self.retract(ph)
        self.declare(ClosedNode(node_id=nid))
        self.declare(CurrentNode(node_id=nid))
        self.declare(Phase(name="check_goal"))
        print(f"[SELECT] best node={nid}")

    @Rule(AS.ph << Phase(name="select"), NOT(OpenNode()), NOT(GoalNode()), salience=1)
    def stop_when_open_empty(self, ph):
        self.retract(ph)

    @Rule(AS.ph << Phase(name="check_goal"), GoalNode(node_id=MATCH.nid), salience=200)
    def goal_reached_halt(self, ph, nid):
        self.retract(ph)
        print(f"[GOAL HIT] node={nid}")

    # --- expansion cleanup triggers ---

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(PendingSuccessor(parent_id=MATCH.nid)),
        MoveGenerated(parent_id=MATCH.nid),
        NOT(ExpandCleanup(parent_id=MATCH.nid)),
        salience=-10,
    )
    def start_expand_cleanup_moves(self, nid):
        self.declare(ExpandCleanup(parent_id=nid))
        self.declare(ExpandVisited(node_id=nid))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(PendingSuccessor(parent_id=MATCH.nid)),
        LoadGenerated(parent_id=MATCH.nid),
        NOT(ExpandCleanup(parent_id=MATCH.nid)),
        salience=-10,
    )
    def start_expand_cleanup_loads(self, nid):
        self.declare(ExpandCleanup(parent_id=nid))
        self.declare(ExpandVisited(node_id=nid))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(PendingSuccessor(parent_id=MATCH.nid)),
        UnloadColorGenerated(parent_id=MATCH.nid),
        NOT(ExpandCleanup(parent_id=MATCH.nid)),
        salience=-10,
    )
    def start_expand_cleanup_unload_color(self, nid):
        self.declare(ExpandCleanup(parent_id=nid))
        self.declare(ExpandVisited(node_id=nid))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(PendingSuccessor(parent_id=MATCH.nid)),
        UnloadPavilionGenerated(parent_id=MATCH.nid),
        NOT(ExpandCleanup(parent_id=MATCH.nid)),
        salience=-10,
    )
    def start_expand_cleanup_unload_pav(self, nid):
        self.declare(ExpandCleanup(parent_id=nid))
        self.declare(ExpandVisited(node_id=nid))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        ExpandStarted(node_id=MATCH.nid),
        NOT(PendingSuccessor(parent_id=MATCH.nid)),
        NOT(MoveGenerated(parent_id=MATCH.nid)),
        NOT(LoadGenerated(parent_id=MATCH.nid)),
        NOT(UnloadColorGenerated(parent_id=MATCH.nid)),
        NOT(UnloadPavilionGenerated(parent_id=MATCH.nid)),
        NOT(ExpandCleanup(parent_id=MATCH.nid)),
        salience=-10,
    )
    def start_expand_cleanup_idle(self, nid):
        self.declare(ExpandCleanup(parent_id=nid))
        self.declare(ExpandVisited(node_id=nid))

    # clean up generator marker facts once expansion is wrapping up
    @Rule(AS.m << MoveGenerated(parent_id=MATCH.nid), ExpandCleanup(parent_id=MATCH.nid), salience=10)
    def cleanup_move_marker(self, m, nid):
        self.retract(m)

    @Rule(AS.lg << LoadGenerated(parent_id=MATCH.nid), ExpandCleanup(parent_id=MATCH.nid), salience=10)
    def cleanup_load_marker(self, lg, nid):
        self.retract(lg)

    @Rule(AS.uc << UnloadColorGenerated(parent_id=MATCH.nid), ExpandCleanup(parent_id=MATCH.nid), salience=10)
    def cleanup_unload_color_marker(self, uc, nid):
        self.retract(uc)

    @Rule(AS.up << UnloadPavilionGenerated(parent_id=MATCH.nid), ExpandCleanup(parent_id=MATCH.nid), salience=10)
    def cleanup_unload_pav_marker(self, up, nid):
        self.retract(up)

    @Rule(
        AS.ph << Phase(name="expand"),
        AS.cn << CurrentNode(node_id=MATCH.nid),
        AS.ec << ExpandCleanup(parent_id=MATCH.nid),
        NOT(MoveGenerated(parent_id=MATCH.nid)),
        NOT(LoadGenerated(parent_id=MATCH.nid)),
        NOT(UnloadColorGenerated(parent_id=MATCH.nid)),
        NOT(UnloadPavilionGenerated(parent_id=MATCH.nid)),
        salience=90,
    )
    def expansion_done(self, ph, cn, ec, nid):
        self.retract(ec)
        self.retract(ph)
        self.retract(cn)
        self.declare(Phase(name="score"))
        print(f"[PHASE] expand → score")


    @Rule(
        Phase(name="score"),
        SearchNode(node_id=MATCH.nid),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        NOT(NeedScore(node_id=MATCH.nid)),
        salience=110,
    )
    def flag_need_score(self, nid):
        self.declare(NeedScore(node_id=nid))

    @Rule(AS.ns << NeedScore(node_id=MATCH.nid), OpenNode(node_id=MATCH.nid), salience=60)
    def need_score_done(self, ns, nid):
        self.retract(ns)

    @Rule(AS.ns << NeedScore(node_id=MATCH.nid), NOT(SearchNode(node_id=MATCH.nid)), salience=70)
    def need_score_orphan_cleanup(self, ns, nid):
        self.retract(ns)

    @Rule(AS.ph << Phase(name="score"), NOT(PendingH()), NOT(NeedScore()), NOT(GoalNode()), salience=5)
    def scoring_done(self, ph):
        self.retract(ph)
        self.declare(Phase(name="select"))
        print(f"[PHASE] score → select")

    def run_astar(self, initial_facts, max_steps=500000):
        self.reset()
        self.declare(*initial_facts)
        self.declare(Phase(name="select"))
        self.run(max_steps)
        self.declare(SearchStopped(max_steps=max_steps))
        self.run(300)
        return None, None
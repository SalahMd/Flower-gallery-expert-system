from experta import KnowledgeEngine, Rule, AS, NOT, MATCH, TEST
import engine
from facts.constraint_facts import PruneNode
from facts.search_facts import *
from rules.movement_rules import MovementRules
from rules.loading_rules import LoadingRules
from rules.unloading_rules import UnloadingRules
from rules.transition_rules import TransitionRules
from rules.constraint_rules import ConstraintRules
from rules.heuristic_rules import HeuristicRules
from rules.goal_rules import GoalRules
from rules.output_rules import OutputRules
from rules.search_rules import SearchRules
from utils.score_node import ScoredNode


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
    OpenNode(node_id=MATCH.nid, f_cost=MATCH.f, g_cost=MATCH.g),
    SearchStrategy(name=MATCH.strategy),
    NOT(BestOpen()),
    salience=25,
)
    def first_best_open(self, nid, f, g, strategy):
        self.declare(BestOpen(node_id=nid, f_cost=f, g_cost=g))

    @Rule(
        Phase(name="select"),
        OpenNode(node_id=MATCH.nid, f_cost=MATCH.f, g_cost=MATCH.g),
        AS.bo << BestOpen(node_id=MATCH.bid, f_cost=MATCH.bf, g_cost=MATCH.bg),
        SearchStrategy(name=MATCH.strategy),
        TEST(lambda nid, bid, f, bf, g, bg, strategy: (
            nid != bid and (
                (strategy == "dfs" and (g > bg or (g == bg and f < bf)))
                or
                (strategy == "astar" and (f < bf or (f == bf and g > bg)))
            )
        )),
        salience=24,
    )
    def improve_best_open(self, nid, f, g, bo, bid, bf, bg, strategy):
        self.retract(bo)
        self.declare(BestOpen(node_id=nid, f_cost=f, g_cost=g))

    @Rule(
        AS.ph << Phase(name="select"),
        AS.bo << BestOpen(node_id=MATCH.nid, f_cost=MATCH.f, g_cost=MATCH.g),
        AS.best << OpenNode(node_id=MATCH.nid, f_cost=MATCH.f, g_cost=MATCH.g),
        NOT(GoalNode()),
        salience=10,
    )
    def select_best_open(self, ph, bo, best, nid, f, g):
        self.retract(best)
        self.retract(bo)
        self.retract(ph)
        self.declare(ClosedNode(node_id=nid))
        self.declare(CurrentNode(node_id=nid))
        self.declare(Phase(name="check_goal"))
        print(f"best node={nid}, f={f}, g={g}")

    @Rule(AS.bo << BestOpen(), NOT(Phase(name="select")), salience=1)
    def cleanup_best_open(self, bo):
        self.retract(bo)

    @Rule(
        AS.ph << Phase(name="select"),
        NOT(OpenNode()),
        NOT(GoalNode()),
        salience=1,
    )
    def stop_when_open_empty(self, ph):
        self.retract(ph)
        print("open list exhausted - no solution found")

    @Rule(
        AS.ph << Phase(name="check_goal"),
        GoalNode(node_id=MATCH.nid),
        salience=200,
    )
    def goal_reached_halt(self, ph, nid):
        self.retract(ph)

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

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(ExpandStarted(node_id=MATCH.nid)),
        NOT(PendingSuccessor(parent_id=MATCH.nid)),
        NOT(ExpandCleanup(parent_id=MATCH.nid)),
        salience=-20,
    )
    def start_expand_cleanup_no_successors(self, nid):
        self.declare(ExpandCleanup(parent_id=nid))
        self.declare(ExpandVisited(node_id=nid))

    @Rule(
        AS.m << MoveGenerated(parent_id=MATCH.nid),
        ExpandCleanup(parent_id=MATCH.nid),
        salience=10,
    )
    def cleanup_move_marker(self, m, nid):
        self.retract(m)

    @Rule(
        AS.lg << LoadGenerated(parent_id=MATCH.nid),
        ExpandCleanup(parent_id=MATCH.nid),
        salience=10,
    )
    def cleanup_load_marker(self, lg, nid):
        self.retract(lg)

    @Rule(
        AS.uc << UnloadColorGenerated(parent_id=MATCH.nid),
        ExpandCleanup(parent_id=MATCH.nid),
        salience=10,
    )
    def cleanup_unload_color_marker(self, uc, nid):
        self.retract(uc)

    @Rule(
        AS.up << UnloadPavilionGenerated(parent_id=MATCH.nid),
        ExpandCleanup(parent_id=MATCH.nid),
        salience=10,
    )
    def cleanup_unload_pav_marker(self, up, nid):
        self.retract(up)

    @Rule(
        AS.es << ExpandStarted(node_id=MATCH.nid),
        ExpandCleanup(parent_id=MATCH.nid),
        salience=10,
    )
    def cleanup_expand_started(self, es, nid):
        self.retract(es)

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
        print(f"expand -> score, node={nid}")

    @Rule(
        Phase(name="score"),
        AS.sn << SearchNode(
            node_id=MATCH.nid,
            parent_id=MATCH.pid,
            action=MATCH.act,
            g_cost=MATCH.g,
        ),
        StateReady(node_id=MATCH.nid),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        NOT(PruneNode(node_id=MATCH.nid)),
        NOT(ScoredNode(node_id=MATCH.nid)),
        salience=110,
    )
    def score_node(self, sn, nid, pid, act, g):
        h = self.compute_h(nid)
        f = g + h
        self.retract(sn)
        self.declare(ScoredNode(node_id=nid))
        self.declare(SearchNode(
            node_id=nid, parent_id=pid, action=act,
            g_cost=g, h_cost=h, f_cost=f,
        ))
        self.declare(OpenNode(node_id=nid, f_cost=f, g_cost=g))
        print(f"{nid} g={g} h={h} f={f}")

    @Rule(
        AS.sc << ScoredNode(node_id=MATCH.nid),
        OpenNode(node_id=MATCH.nid),
        salience=60,
    )
    def cleanup_scored_node(self, sc, nid):
        self.retract(sc)

    @Rule(
        AS.ph << Phase(name="score"),
        NOT(ScoredNode()),
        NOT(PruneNode()),  
        NOT(GoalNode()),
        salience=5,
    )
    def scoring_done(self, ph):
        self.retract(ph)
        self.declare(Phase(name="select"))

    @Rule(
        AS.gcd << GoalCheckDone(node_id=MATCH.nid),
        NOT(Phase(name="check_goal")),
        NOT(Phase(name="expand")),
        salience=2,
    )
    def cleanup_goal_check_done(self, gcd, nid):
        self.retract(gcd)

    @Rule(
        AS.pn << NeedUnmet(node_id=MATCH.nid),
        NOT(Phase(name="check_goal")),
        salience=2,
    )
    def cleanup_stale_need_unmet(self, pn, nid):
        self.retract(pn)

    @Rule(
        AS.pnc << NeedUnmetChecked(node_id=MATCH.nid),
        NOT(Phase(name="check_goal")),
        salience=2,
    )
    def cleanup_stale_need_unmet_checked(self, pnc, nid):
        self.retract(pnc)


    @Rule(GoalNode(), NOT(SearchStopped()), salience=1000)
    def mark_search_done(self):
        self.declare(SearchStopped(max_steps=0))

    @Rule(GoalNode(), AS.ph << Phase(name=MATCH.p), salience=500)
    def halt_on_goal(self, ph, p):
        self.retract(ph)
    @Rule(
        Phase(name="score"),
        SearchNode(node_id=MATCH.nid, g_cost=MATCH.g),
        MaxDepth(depth=MATCH.max_d),
        StateReady(node_id=MATCH.nid),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        NOT(PruneNode(node_id=MATCH.nid)),
        NOT(ScoredNode(node_id=MATCH.nid)),
        TEST(lambda g, max_d: g > max_d),
        salience=120,
    )
    def prune_deep_node(self, nid, g, max_d):
        self.declare(PruneNode(node_id=nid))
        print(f"{nid} exceeds max_depth (g={g} > max_d={max_d})")
    @Rule(SearchStopped(), AS.ph << Phase(name=MATCH.p), salience=500)
        
    def halt_on_stop(self, ph, p):
        self.retract(ph)


    def _has_fact(self, name):
        for f in self.facts.values():
            if type(f).__name__ == name:
                return True
        return False

    def run_astar(self, initial_facts, max_depth=50, max_steps=500000, strategy="astar"):
        self.reset()
        self.declare(*initial_facts)
        self.declare(Phase(name="select"))
        self.declare(MaxDepth(depth=max_depth))
        self.declare(SearchStrategy(name=strategy))
        used = 0
        chunk = 100
        while used < max_steps:
            self.run(chunk)
            used += chunk
            if self._has_fact("GoalNode") or self._has_fact("SearchStopped"):
                break
        if not self._has_fact("SearchStopped"):
            self.declare(SearchStopped(max_steps=used))
        goal_id = None
        for f in self.facts.values():
            if type(f).__name__ == "GoalNode":
                goal_id = f["node_id"]
                break
        self.run(500)
        if goal_id:
            print(f"GOAL FOUND: {goal_id}  steps={used}")
        else:
            print(f"NO GOAL  steps={used}")
        return goal_id, used
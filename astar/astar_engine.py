from experta import KnowledgeEngine, Rule, AS, NOT, MATCH, TEST

from facts.search_facts import (
    SearchNode, OpenNode, ClosedNode, CurrentNode, GoalNode,
    Phase, PendingSuccessor, MoveGenerated, LoadGenerated,
    UnloadColorGenerated, UnloadPavilionGenerated, ExpandCleanup, ExpandVisited,
    ExpandStarted, NeedScore, PendingH,
)

from rules.movement_rules import MovementRules
from rules.loading_rules import LoadingRules
from rules.unloading_rules import UnloadingRules
from rules.transition_rules import TransitionRules
from rules.constraint_rules import ConstraintRules
from rules.heuristic_rules import HeuristicRules
from rules.goal_rules import GoalRules
from rules.search_rules import SearchRules


class AStarEngine(
    MovementRules,
    LoadingRules,
    UnloadingRules,
    TransitionRules,
    ConstraintRules,
    HeuristicRules,
    GoalRules,
    SearchRules,
    KnowledgeEngine,
):

    @Rule(
        AS.ph << Phase(name="select"),
        NOT(GoalNode()),
        salience=10,
    )
    def select_best_open(self, ph):
        open_nodes = [f for f in self.facts.values() if isinstance(f, OpenNode)]
        print(f"\n[SELECT] open list has {len(open_nodes)} nodes: "
              f"{[(f['node_id'], f['f_cost'], f['g_cost']) for f in open_nodes]}")

        best = None
        for f in self.facts.values():
            if isinstance(f, OpenNode):
                if (best is None
                        or f["f_cost"] < best["f_cost"]
                        or (f["f_cost"] == best["f_cost"] and f["g_cost"] < best["g_cost"])):
                    best = f

        if best is None:
            print("[SELECT] *** OPEN LIST EMPTY - no solution possible ***")
            self.retract(ph)
            return

        nid = best["node_id"]
        print(f"[SELECT] picking node={nid}  f={best['f_cost']}  g={best['g_cost']}")
        self.retract(best)
        self.retract(ph)
        self.declare(ClosedNode(node_id=nid))
        self.declare(CurrentNode(node_id=nid))
        self.declare(Phase(name="check_goal"))

    @Rule(
        AS.ph << Phase(name="check_goal"),
        GoalNode(node_id=MATCH.nid),
        salience=200,
    )
    def goal_reached_halt(self, ph, nid):
        print(f"[GOAL] reached node={nid}")
        self.retract(ph)

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(PendingSuccessor(parent_id=MATCH.nid)),
        MoveGenerated(parent_id=MATCH.nid),
        NOT(ExpandCleanup(parent_id=MATCH.nid)),
        salience=100,
    )
    def start_expand_cleanup_moves(self, nid):
        print(f"[EXPAND CLEANUP] moves done for {nid}")
        self.declare(ExpandCleanup(parent_id=nid))
        self.declare(ExpandVisited(node_id=nid))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(PendingSuccessor(parent_id=MATCH.nid)),
        LoadGenerated(parent_id=MATCH.nid),
        NOT(ExpandCleanup(parent_id=MATCH.nid)),
        salience=100,
    )
    def start_expand_cleanup_loads(self, nid):
        print(f"[EXPAND CLEANUP] loads done for {nid}")
        self.declare(ExpandCleanup(parent_id=nid))
        self.declare(ExpandVisited(node_id=nid))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(PendingSuccessor(parent_id=MATCH.nid)),
        UnloadColorGenerated(parent_id=MATCH.nid),
        NOT(ExpandCleanup(parent_id=MATCH.nid)),
        salience=100,
    )
    def start_expand_cleanup_unload_color(self, nid):
        print(f"[EXPAND CLEANUP] unload-color done for {nid}")
        self.declare(ExpandCleanup(parent_id=nid))
        self.declare(ExpandVisited(node_id=nid))

    @Rule(
        Phase(name="expand"),
        CurrentNode(node_id=MATCH.nid),
        NOT(PendingSuccessor(parent_id=MATCH.nid)),
        UnloadPavilionGenerated(parent_id=MATCH.nid),
        NOT(ExpandCleanup(parent_id=MATCH.nid)),
        salience=100,
    )
    def start_expand_cleanup_unload_pav(self, nid):
        print(f"[EXPAND CLEANUP] unload-pav done for {nid}")
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
        salience=100,
    )
    def start_expand_cleanup_idle(self, nid):
        print(f"[EXPAND CLEANUP] idle (no successors) for {nid}")
        self.declare(ExpandCleanup(parent_id=nid))
        self.declare(ExpandVisited(node_id=nid))

    @Rule(
        AS.m << MoveGenerated(parent_id=MATCH.nid),
        ExpandCleanup(parent_id=MATCH.nid),
        salience=10,
    )
    def cleanup_move_marker(self, m):
        self.retract(m)

    @Rule(
        AS.lg << LoadGenerated(parent_id=MATCH.nid),
        ExpandCleanup(parent_id=MATCH.nid),
        salience=10,
    )
    def cleanup_load_marker(self, lg):
        self.retract(lg)

    @Rule(
        AS.uc << UnloadColorGenerated(parent_id=MATCH.nid),
        ExpandCleanup(parent_id=MATCH.nid),
        salience=10,
    )
    def cleanup_unload_color_marker(self, uc):
        self.retract(uc)

    @Rule(
        AS.up << UnloadPavilionGenerated(parent_id=MATCH.nid),
        ExpandCleanup(parent_id=MATCH.nid),
        salience=10,
    )
    def cleanup_unload_pav_marker(self, up):
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
        children = [f for f in self.facts.values()
                    if isinstance(f, SearchNode) and f["node_id"] != nid
                    and f["parent_id"] == nid]
        print(f"[EXPAND DONE] node={nid}  generated {len(children)} children: "
              f"{[f['node_id'] for f in children]}")
        self.retract(ec)
        self.retract(ph)
        self.retract(cn)
        self.declare(Phase(name="score"))

    @Rule(
        Phase(name="score"),
        SearchNode(node_id=MATCH.nid),
        NOT(OpenNode(node_id=MATCH.nid)),
        NOT(ClosedNode(node_id=MATCH.nid)),
        NOT(NeedScore(node_id=MATCH.nid)),
        salience=110,
    )
    def flag_need_score(self, nid):
        print(f"[SCORE] flagging node={nid} for scoring")
        self.declare(NeedScore(node_id=nid))

    @Rule(
        AS.ns << NeedScore(node_id=MATCH.nid),
        OpenNode(node_id=MATCH.nid),
        salience=60,
    )
    def need_score_done(self, ns, nid):
        print(f"[SCORE] node={nid} scored -> OpenNode exists, NeedScore cleaned")
        self.retract(ns)

    @Rule(
        AS.ns << NeedScore(node_id=MATCH.nid),
        NOT(SearchNode(node_id=MATCH.nid)),
        salience=70,
    )
    def need_score_orphan_cleanup(self, ns, nid):
        print(f"[SCORE] node={nid} was PRUNED, cleaning orphan NeedScore")
        self.retract(ns)

    @Rule(
        AS.ph << Phase(name="score"),
        NOT(PendingH()),
        NOT(NeedScore()),
        NOT(GoalNode()),
        salience=5,
    )
    def scoring_done(self, ph):
        open_now = [f for f in self.facts.values() if isinstance(f, OpenNode)]
        print(f"[SCORE DONE] -> back to select. Open list now: "
              f"{[(f['node_id'], f['f_cost']) for f in open_now]}")
        self.retract(ph)
        self.declare(Phase(name="select"))

    def run_astar(self, initial_facts, max_steps=150000):
        self.reset()
        for fact in initial_facts:
            self.declare(fact)
        self.declare(Phase(name="select"))

        print("\n" + "="*60)
        print("INITIAL FACTS")
        print("="*60)
        for fid, fact in self.facts.items():
            print(f"  [{fid}] {type(fact).__name__}: {dict(fact)}")

        print("\n" + "="*60)
        print("RUNNING ENGINE")
        print("="*60)

        for step in range(max_steps):
            if any(type(f).__name__ == "GoalNode" for f in self.facts.values()):
                print(f"\n[RUN] GoalNode detected at step {step}")
                break
            before = len(self.facts)
            self.run(steps=1)
            after = len(self.facts)
            if after == before:
                print(f"\n[RUN] ENGINE STALLED at step {step} - working memory frozen")
                print("\nFull WM at stall:")
                for fid, fact in self.facts.items():
                    print(f"  [{fid}] {type(fact).__name__}: {dict(fact)}")
                break
        else:
            print(f"[RUN] max_steps={max_steps} reached")

        return self._extract_solution()

    def _extract_solution(self):
        goal = None
        for fact in self.facts.values():
            if type(fact).__name__ == "GoalNode":
                goal = fact
                break
        if goal is None:
            print("\n[EXTRACT] No GoalNode in WM -> returning None")
            return None, []

        path = []
        visited = set()
        nid = goal["node_id"]

        while nid and nid not in visited:
            visited.add(nid)
            for fact in self.facts.values():
                if type(fact).__name__ == "SearchNode" and fact["node_id"] == nid:
                    path.append(fact)
                    parent = fact["parent_id"]
                    nid = parent if parent != nid else None
                    break
            else:
                break

        path.reverse()
        return goal["node_id"], path

    def get_all_nodes(self):
        return [f for f in self.facts.values() if type(f).__name__ == "SearchNode"]
from experta import KnowledgeEngine, Rule, AS, NOT, MATCH
from facts.search_facts import *
class OutputRules(KnowledgeEngine):

    @Rule(
        SearchStopped(),
        GoalNode(node_id=MATCH.goal),
        NOT(OutputBacktrack(node_id=MATCH.goal)),
        salience=100,
    )
    def seed_backtrack(self, goal):
        self.declare(OutputBacktrack(node_id=goal, parent_id=goal))

    @Rule(
        SearchStopped(),
        GoalNode(node_id=MATCH.goal),
        AS.ob << OutputBacktrack(node_id=MATCH.cur, parent_id=MATCH.cur),
        SearchNode(node_id=MATCH.cur, parent_id=MATCH.pid, action=MATCH.act, g_cost=MATCH.g, h_cost=MATCH.h, f_cost=MATCH.f),
        NOT(OutputBacktrack(node_id=MATCH.pid)),
        salience=95,
    )
    def walk_backtrack(self, ob, goal, cur, pid, act, g, h, f):
        self.retract(ob)
        self.declare(OutputBacktrack(node_id=pid, parent_id=pid))
        self.declare(NodePrinted(node_id=cur))
        print(f"{cur}  action={act}  g={g}  h={h}  f={f}")

    @Rule(
        SearchStopped(),
        GoalNode(node_id=MATCH.goal),
        AS.ob << OutputBacktrack(node_id=MATCH.cur, parent_id=MATCH.cur),
        SearchNode(node_id=MATCH.cur, parent_id=MATCH.cur, action=MATCH.act, g_cost=MATCH.g, h_cost=MATCH.h, f_cost=MATCH.f),
        salience=94,
    )
    def finish_backtrack(self, ob, goal, cur, act, g, h, f):
        self.retract(ob)
        self.declare(NodePrinted(node_id=cur))
        print(f"\nSOLUTION PATH")
        print(f"{cur}  action={act}  g={g}  h={h}  f={f}")

    @Rule(
        SearchStopped(),
        NOT(NodePrinted(node_id="tree_header")),
        salience=50,
    )
    def print_tree_header(self):
        self.declare(NodePrinted(node_id="tree_header"))
        print("\nSEARCH TREE")

    @Rule(
        SearchStopped(),
        SearchNode(node_id=MATCH.nid, parent_id=MATCH.pid, action=MATCH.act, g_cost=MATCH.g, h_cost=MATCH.h, f_cost=MATCH.f),
        NOT(NodePrinted(node_id=MATCH.nid)),
        salience=40,
    )
    def print_tree_node(self, nid, pid, act, g, h, f):
        self.declare(NodePrinted(node_id=nid))
        print(f"{pid} -> {nid}  action={act}  g={g}  h={h}  f={f}")
import sys
from experta import KnowledgeEngine, Rule, NOT, MATCH, TEST
from facts.search_facts import SearchNode, GoalNode, SearchStopped, OutputHeader, OutputNode, OutputBacktrack


class OutputRules(KnowledgeEngine):

    @Rule(SearchStopped(max_steps=MATCH.max_steps), NOT(GoalNode()), NOT(OutputHeader(name="no_solution")), salience=1000)
    def no_solution(self, max_steps):
        sys.stdout.write(f"\nNo solution found within {max_steps} rule firings.\n")
        sys.stdout.flush()
        self.declare(OutputHeader(name="no_solution"))

    @Rule(GoalNode(node_id=MATCH.nid), NOT(OutputHeader(name="solution")), salience=1000)
    def solution_header(self, nid):
        sys.stdout.write("\nSOLUTION BACKTRACE\n")
        sys.stdout.flush()
        self.declare(OutputHeader(name="solution"))

    @Rule(
        GoalNode(node_id=MATCH.nid),
        SearchNode(node_id=MATCH.nid, parent_id=MATCH.parent, action=MATCH.action,
                   g_cost=MATCH.g, h_cost=MATCH.h, f_cost=MATCH.f),
        OutputHeader(name="solution"),
        NOT(OutputNode(name="solution", node_id=MATCH.nid)),
        salience=999,
    )
    def solution_goal_node(self, nid, parent, action, g, h, f):
        sys.stdout.write(f"{nid}  action={action}  g={g}  h={h}  f={f}\n")
        self.declare(OutputNode(name="solution", node_id=nid))
        self.declare(OutputBacktrack(node_id=nid, parent_id=parent))

    @Rule(
        OutputBacktrack(node_id=MATCH.child, parent_id=MATCH.parent),
        SearchNode(node_id=MATCH.parent, parent_id=MATCH.next_parent, action=MATCH.action,
                   g_cost=MATCH.g, h_cost=MATCH.h, f_cost=MATCH.f),
        NOT(OutputNode(name="solution", node_id=MATCH.parent)),
        TEST(lambda child, parent: child != parent),
        salience=999,
    )
    def solution_parent_node(self, child, parent, next_parent, action, g, h, f):
        sys.stdout.write(f"{parent}  action={action}  g={g}  h={h}  f={f}\n")
        self.declare(OutputNode(name="solution", node_id=parent))
        self.declare(OutputBacktrack(node_id=parent, parent_id=next_parent))

    @Rule(GoalNode(), NOT(OutputHeader(name="tree")), salience=998)
    def tree_header(self):
        sys.stdout.write("\nSEARCH TREE\n")
        sys.stdout.flush()
        self.declare(OutputHeader(name="tree"))

    @Rule(SearchStopped(), NOT(OutputHeader(name="tree")), salience=998)
    def stopped_tree_header(self):
        sys.stdout.write("\nSEARCH TREE\n")
        sys.stdout.flush()
        self.declare(OutputHeader(name="tree"))

    @Rule(
        OutputHeader(name="tree"),
        SearchNode(node_id=MATCH.nid, parent_id=MATCH.parent, action=MATCH.action,
                   g_cost=MATCH.g, h_cost=MATCH.h, f_cost=MATCH.f),
        NOT(OutputNode(name="tree", node_id=MATCH.nid)),
        salience=997,
    )
    def tree_node(self, nid, parent, action, g, h, f):
        sys.stdout.write(f"{parent} -> {nid}  action={action}  g={g}  h={h}  f={f}\n")
        self.declare(OutputNode(name="tree", node_id=nid))
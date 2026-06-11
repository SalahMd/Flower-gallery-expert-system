from engine.setup_engine import build_initial_facts
from astar.astar_engine import AStarEngine


def main():
    initial_facts = build_initial_facts()
    engine = AStarEngine()
    goal_id, steps = engine.run_astar(initial_facts, max_depth=30)
    if not goal_id:
        print("No solution found")


main()

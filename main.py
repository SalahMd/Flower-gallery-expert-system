from engine.setup_engine import build_initial_facts
from astar.astar_engine import AStarEngine


def main():
    initial_facts = build_initial_facts()
    engine = AStarEngine()
    engine.run_astar(initial_facts, max_steps=50000)


main()

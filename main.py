from engine.setup_engine import build_initial_facts
from astar.astar_engine import AStarEngine


def main():
    print("Select search strategy:")
    print("  1. A*")
    print("  2. DFS")

    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        strategy = "astar"
    elif choice == "2":
        strategy = "dfs"
    else:
        print("Invalid choice, defaulting to A*")
        strategy = "astar"

    max_depth = input("Enter max depth (default 30): ").strip()
    max_depth = int(max_depth) if max_depth.isdigit() else 30

    print(f"\nRunning {strategy.upper()} with max_depth={max_depth}\n")

    initial_facts = build_initial_facts()
    engine = AStarEngine()
    goal_id, steps = engine.run_astar(initial_facts, max_depth=max_depth, strategy=strategy)

    if not goal_id:
        print("No solution found")


main()
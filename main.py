from engine.setup_engine import build_initial_facts
from astar.astar_engine import AStarEngine
from utils.printer import print_solution_path, print_search_tree, print_grid
from config.config import GRID_ROWS, GRID_COLS, WAREHOUSE_POS, ROBOT_START, PAVILIONS, PAVILION_NEEDS


def main():
    print_grid(GRID_ROWS, GRID_COLS, ROBOT_START, WAREHOUSE_POS, PAVILIONS)
    for pav_id, needs in PAVILION_NEEDS.items():
        for ft, col, qty in needs:
            print(f"{pav_id}  -> {ft} ({col}) x{qty}")
    print()

    initial_facts = build_initial_facts()
    engine = AStarEngine()

    goal_id, path = engine.run_astar(initial_facts)

    if goal_id is None:
        print("No solution found. Check config or constraints.\n")
        return

    print_solution_path(path)
    all_nodes = engine.get_all_nodes()
    print_search_tree(all_nodes)


if __name__ == "__main__":
    main()

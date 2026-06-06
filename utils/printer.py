def print_solution_path(path):
    print("  SOLUTION PATH")
    if not path:
        print("  No solution found.")
        return
    for i, node in enumerate(path):
        marker = "START" if i == 0 else f"Step {i:>3}"
        print(f"  [{marker}]  node={node['node_id']:<20}  action={node['action']:<35}  g={node['g_cost']}  h={node['h_cost']}  f={node['f_cost']}")
    print(f"  Total cost: {path[-1]['g_cost']}")


def print_search_tree(all_nodes):
    print("  SEARCH TREE  (all generated nodes)")
    if not all_nodes:
        print("  No nodes generated.")
        return

    by_parent = {}
    for node in all_nodes:
        pid = node["parent_id"]
        if pid not in by_parent:
            by_parent[pid] = []
        by_parent[pid].append(node)

    def _print_subtree(nid, depth):
        for node in all_nodes:
            if node["node_id"] == nid:
                indent = "  " + "  " * depth
                print(f"{indent}|-- {node['node_id']}  [{node['action']}]  g={node['g_cost']} h={node['h_cost']} f={node['f_cost']}")
                break
        children = by_parent.get(nid, [])
        for child in children:
            if child["node_id"] != nid:
                _print_subtree(child["node_id"], depth + 1)

    roots = [n for n in all_nodes if n["parent_id"] == n["node_id"]]
    for root in roots:
        _print_subtree(root["node_id"], 0)


    print(f"  Total nodes generated: {len(all_nodes)}")


def print_grid(grid_rows, grid_cols, robot_pos, warehouse_pos, pavilions):
    wh_r, wh_c = warehouse_pos
    rob_r, rob_c = robot_pos
    pav_positions = {pos: pid for pid, pos in pavilions.items()}

    header = "    " + "  ".join(str(c) for c in range(grid_cols))
    print(header)
    print("    " + "--" * grid_cols)
    for r in range(grid_rows):
        row_str = f"{r} | "
        for c in range(grid_cols):
            cell = "."
            if (r, c) == (wh_r, wh_c):
                cell = "W"
            if (r, c) in pav_positions:
                cell = pav_positions[(r, c)][0].upper()
            if (r, c) == (rob_r, rob_c):
                cell = "R"
            row_str += cell + "  "
        print(row_str)
    print()

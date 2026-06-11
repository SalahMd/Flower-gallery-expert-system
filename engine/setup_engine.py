from config.config import *
from facts.world_facts import *
from facts.robot_facts import RobotPosition, RobotState, RobotEmpty, AtWarehouse, RobotCapacity
from facts.cargo_facts import MaxCapacity, TotalCargoCount
from facts.search_facts import SearchNode, OpenNode, NodeCounter


def _neighbors(rows, cols):
    links = []
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                links.append((r, c, "right", r, c + 1))
                links.append((r, c + 1, "left", r, c))
            if r + 1 < rows:
                links.append((r, c, "down", r + 1, c))
                links.append((r + 1, c, "up", r, c))
    return links


def _max_capacity():
    best = 0
    for needs in PAVILION_NEEDS.values():
        total = sum(item[2] for item in needs)
        if total > best:
            best = total
    return best


def _unique_flowers():
    seen_k, seen_c, seen_b = set(), set(), set()
    kinds, colors, bouquets = [], [], []
    for ft, col in WAREHOUSE_STOCK:
        if ft not in seen_k:
            seen_k.add(ft)
            kinds.append(ft)
        if col not in seen_c:
            seen_c.add(col)
            colors.append(col)
        if (ft, col) not in seen_b:
            seen_b.add((ft, col))
            bouquets.append((ft, col))
    for needs in PAVILION_NEEDS.values():
        for ft, col, _ in needs:
            if ft not in seen_k:
                seen_k.add(ft)
                kinds.append(ft)
            if col not in seen_c:
                seen_c.add(col)
                colors.append(col)
            if (ft, col) not in seen_b:
                seen_b.add((ft, col))
                bouquets.append((ft, col))
    return kinds, colors, bouquets


def _pavilion_totals():
    bouquet_totals, color_totals, flower_totals = {}, {}, {}
    for pid, needs in PAVILION_NEEDS.items():
        btotal = 0
        for ft, col, qty in needs:
            btotal += qty
            color_totals[(pid, col)]  = color_totals.get((pid, col), 0) + qty
            flower_totals[(pid, ft)]  = flower_totals.get((pid, ft), 0) + qty
        bouquet_totals[pid] = btotal
    return bouquet_totals, color_totals, flower_totals


def build_initial_facts():
    facts = []
    facts.append(Grid(rows=GRID_ROWS, cols=GRID_COLS))

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            facts.append(Cell(row=r, col=c))

    for r, c, d, tr, tc in _neighbors(GRID_ROWS, GRID_COLS):
        facts.append(NeighborCell(from_row=r, from_col=c, direction=d, to_row=tr, to_col=tc))

    wh_r, wh_c = WAREHOUSE_POS
    facts.append(Warehouse(row=wh_r, col=wh_c))

    for pid, (pr, pc) in PAVILIONS.items():
        facts.append(Pavilion(id=pid, row=pr, col=pc))

    kinds, colors, bouquets = _unique_flowers()
    for name in kinds:
        facts.append(FlowerKind(name=name))
    for name in colors:
        facts.append(FlowerColor(name=name))
    for ft, col in bouquets:
        facts.append(Bouquet(flower_type=ft, color=col))

    for ft, col in WAREHOUSE_STOCK:
        facts.append(WarehouseStock(flower_type=ft, color=col))

    for pid, needs in PAVILION_NEEDS.items():
        for ft, col, qty in needs:
            facts.append(PavilionNeed(pavilion_id=pid, flower_type=ft, color=col, quantity=qty))

    bouquet_totals, color_totals, flower_totals = _pavilion_totals()
    for pid, total in bouquet_totals.items():
        facts.append(PavilionBouquetTotal(pavilion_id=pid, total=total))
    for (pid, col), total in color_totals.items():
        facts.append(PavilionColorNeedTotal(pavilion_id=pid, color=col, total=total))
    for (pid, ft), total in flower_totals.items():
        facts.append(PavilionFlowerNeedTotal(pavilion_id=pid, flower_type=ft, total=total))

    start_r, start_c = ROBOT_START
    cap = _max_capacity()
    facts.append(RobotPosition(node_id="n0", row=start_r, col=start_c))
    facts.append(RobotState(node_id="n0", row=start_r, col=start_c))
    facts.append(RobotEmpty(node_id="n0"))
    facts.append(MaxCapacity(value=cap))
    facts.append(RobotCapacity(value=cap))
    facts.append(TotalCargoCount(node_id="n0", count=0))

    if (start_r, start_c) == (wh_r, wh_c):
        facts.append(AtWarehouse(node_id="n0"))

    facts.append(SearchNode(
        node_id="n0", parent_id="n0", action="start",
        g_cost=0, h_cost=0, f_cost=0,
    ))
    facts.append(NodeCounter(value=1))
    facts.append(OpenNode(node_id="n0", f_cost=0, g_cost=0))

    return facts

def build_demo_facts():
    facts = [
        Grid(rows=3, cols=3),

        Cell(row=0, col=0), Cell(row=0, col=1), Cell(row=0, col=2),
        Cell(row=1, col=0), Cell(row=1, col=1), Cell(row=1, col=2),
        Cell(row=2, col=0), Cell(row=2, col=1), Cell(row=2, col=2),
    ]

    for r, c, d, tr, tc in _neighbors(3, 3):
        facts.append(NeighborCell(from_row=r, from_col=c, direction=d, to_row=tr, to_col=tc))

    facts += [
        Warehouse(row=1, col=2),
        Pavilion(id="p1", row=0, col=0),

        FlowerKind(name="rose"),
        FlowerColor(name="red"),
        Bouquet(flower_type="rose", color="red"),
        WarehouseStock(flower_type="rose", color="red"),

        PavilionNeed(pavilion_id="p1", flower_type="rose", color="red", quantity=1),
        PavilionBouquetTotal(pavilion_id="p1", total=1),
        PavilionColorNeedTotal(pavilion_id="p1", color="red", total=1),
        PavilionFlowerNeedTotal(pavilion_id="p1", flower_type="rose", total=1),

        RobotPosition(node_id="n0", row=0, col=2),
        RobotState(node_id="n0", row=0, col=2),
        RobotEmpty(node_id="n0"),

        MaxCapacity(value=1),
        RobotCapacity(value=1),
        TotalCargoCount(node_id="n0", count=0),

        SearchNode(node_id="n0", parent_id="n0", action="start", g_cost=0, h_cost=0, f_cost=0),
        NodeCounter(value=1),
        OpenNode(node_id="n0", f_cost=0, g_cost=0),
    ]
    return facts
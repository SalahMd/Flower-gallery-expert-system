from config.config import (
    GRID_ROWS, GRID_COLS, WAREHOUSE_POS, ROBOT_START,
    PAVILIONS, PAVILION_NEEDS, WAREHOUSE_STOCK,
)
from facts.world_facts import (
    Grid, Cell, NeighborCell, Warehouse, WarehouseStock, Pavilion,
    FlowerKind, FlowerColor, Bouquet,
    PavilionNeed, PavilionBouquetTotal,
    PavilionColorNeedTotal, PavilionFlowerNeedTotal,
)
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
        total = 0
        for item in needs:
            total = total + item[2]
        if total > best:
            best = total
    return best


def _unique_flowers():
    kinds = []
    colors = []
    bouquets = []
    seen_k = set()
    seen_c = set()
    seen_b = set()
    for stock in WAREHOUSE_STOCK:
        ft, col = stock[0], stock[1]
        if ft not in seen_k:
            seen_k.add(ft)
            kinds.append(ft)
        if col not in seen_c:
            seen_c.add(col)
            colors.append(col)
        key = (ft, col)
        if key not in seen_b:
            seen_b.add(key)
            bouquets.append(key)
    for pid, needs in PAVILION_NEEDS.items():
        for item in needs:
            ft, col = item[0], item[1]
            if ft not in seen_k:
                seen_k.add(ft)
                kinds.append(ft)
            if col not in seen_c:
                seen_c.add(col)
                colors.append(col)
            key = (ft, col)
            if key not in seen_b:
                seen_b.add(key)
                bouquets.append(key)
    return kinds, colors, bouquets


def _pavilion_totals():
    bouquet_totals = {}
    color_totals = {}
    flower_totals = {}
    for pid, needs in PAVILION_NEEDS.items():
        btotal = 0
        for item in needs:
            ft, col, qty = item[0], item[1], item[2]
            btotal = btotal + qty
            ck = (pid, col)
            color_totals[ck] = color_totals.get(ck, 0) + qty
            fk = (pid, ft)
            flower_totals[fk] = flower_totals.get(fk, 0) + qty
        bouquet_totals[pid] = btotal
    return bouquet_totals, color_totals, flower_totals


def build_initial_facts():
    facts = []
    facts.append(Grid(rows=GRID_ROWS, cols=GRID_COLS))

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            facts.append(Cell(row=r, col=c))

    for link in _neighbors(GRID_ROWS, GRID_COLS):
        facts.append(NeighborCell(
            from_row=link[0], from_col=link[1], direction=link[2],
            to_row=link[3], to_col=link[4],
        ))

    wh_r, wh_c = WAREHOUSE_POS
    facts.append(Warehouse(row=wh_r, col=wh_c))

    for pid, pos in PAVILIONS.items():
        facts.append(Pavilion(id=pid, row=pos[0], col=pos[1]))

    kinds, colors, bouquets = _unique_flowers()
    for name in kinds:
        facts.append(FlowerKind(name=name))
    for name in colors:
        facts.append(FlowerColor(name=name))
    for ft, col in bouquets:
        facts.append(Bouquet(flower_type=ft, color=col))

    for stock in WAREHOUSE_STOCK:
        facts.append(WarehouseStock(flower_type=stock[0], color=stock[1]))

    for pid, needs in PAVILION_NEEDS.items():
        for item in needs:
            facts.append(PavilionNeed(
                pavilion_id=pid, flower_type=item[0], color=item[1], quantity=item[2],
            ))

    bouquet_totals, color_totals, flower_totals = _pavilion_totals()
    for pid, total in bouquet_totals.items():
        facts.append(PavilionBouquetTotal(pavilion_id=pid, total=total))
    for key, total in color_totals.items():
        facts.append(PavilionColorNeedTotal(pavilion_id=key[0], color=key[1], total=total))
    for key, total in flower_totals.items():
        facts.append(PavilionFlowerNeedTotal(pavilion_id=key[0], flower_type=key[1], total=total))

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
        NeighborCell(from_row=0, from_col=0, direction="right", to_row=0, to_col=1),
        NeighborCell(from_row=0, from_col=1, direction="left", to_row=0, to_col=0),
        NeighborCell(from_row=0, from_col=1, direction="right", to_row=0, to_col=2),
        NeighborCell(from_row=0, from_col=2, direction="left", to_row=0, to_col=1),
        NeighborCell(from_row=1, from_col=0, direction="right", to_row=1, to_col=1),
        NeighborCell(from_row=1, from_col=1, direction="left", to_row=1, to_col=0),
        NeighborCell(from_row=1, from_col=1, direction="right", to_row=1, to_col=2),
        NeighborCell(from_row=1, from_col=2, direction="left", to_row=1, to_col=1),
        NeighborCell(from_row=2, from_col=0, direction="right", to_row=2, to_col=1),
        NeighborCell(from_row=2, from_col=1, direction="left", to_row=2, to_col=0),
        NeighborCell(from_row=2, from_col=1, direction="right", to_row=2, to_col=2),
        NeighborCell(from_row=2, from_col=2, direction="left", to_row=2, to_col=1),
        NeighborCell(from_row=0, from_col=0, direction="down", to_row=1, to_col=0),
        NeighborCell(from_row=1, from_col=0, direction="up", to_row=0, to_col=0),
        NeighborCell(from_row=1, from_col=0, direction="down", to_row=2, to_col=0),
        NeighborCell(from_row=2, from_col=0, direction="up", to_row=1, to_col=0),
        NeighborCell(from_row=0, from_col=1, direction="down", to_row=1, to_col=1),
        NeighborCell(from_row=1, from_col=1, direction="up", to_row=0, to_col=1),
        NeighborCell(from_row=1, from_col=1, direction="down", to_row=2, to_col=1),
        NeighborCell(from_row=2, from_col=1, direction="up", to_row=1, to_col=1),
        NeighborCell(from_row=0, from_col=2, direction="down", to_row=1, to_col=2),
        NeighborCell(from_row=1, from_col=2, direction="up", to_row=0, to_col=2),
        NeighborCell(from_row=1, from_col=2, direction="down", to_row=2, to_col=2),
        NeighborCell(from_row=2, from_col=2, direction="up", to_row=1, to_col=2),
        Warehouse(row=1, col=1),
        Pavilion(id="p1", row=0, col=2),
        Pavilion(id="p2", row=2, col=0),
        Pavilion(id="p3", row=2, col=2),
        FlowerKind(name="rose"),
        FlowerKind(name="tulip"),
        FlowerColor(name="red"),
        FlowerColor(name="yellow"),
        FlowerColor(name="pink"),
        FlowerColor(name="white"),
        Bouquet(flower_type="rose", color="red"),
        Bouquet(flower_type="rose", color="pink"),
        Bouquet(flower_type="rose", color="white"),
        Bouquet(flower_type="tulip", color="yellow"),
        WarehouseStock(flower_type="rose", color="red"),
        WarehouseStock(flower_type="rose", color="pink"),
        WarehouseStock(flower_type="rose", color="white"),
        WarehouseStock(flower_type="tulip", color="yellow"),
        PavilionNeed(pavilion_id="p1", flower_type="rose", color="red", quantity=1),
        PavilionNeed(pavilion_id="p1", flower_type="rose", color="pink", quantity=1),
        PavilionNeed(pavilion_id="p1", flower_type="rose", color="white", quantity=1),
        PavilionNeed(pavilion_id="p2", flower_type="tulip", color="yellow", quantity=1),
        PavilionNeed(pavilion_id="p3", flower_type="rose", color="red", quantity=1),
        PavilionBouquetTotal(pavilion_id="p1", total=3),
        PavilionBouquetTotal(pavilion_id="p2", total=1),
        PavilionBouquetTotal(pavilion_id="p3", total=1),
        PavilionColorNeedTotal(pavilion_id="p1", color="red", total=1),
        PavilionColorNeedTotal(pavilion_id="p1", color="pink", total=1),
        PavilionColorNeedTotal(pavilion_id="p1", color="white", total=1),
        PavilionColorNeedTotal(pavilion_id="p2", color="yellow", total=1),
        PavilionColorNeedTotal(pavilion_id="p3", color="red", total=1),
        PavilionFlowerNeedTotal(pavilion_id="p1", flower_type="rose", total=3),
        PavilionFlowerNeedTotal(pavilion_id="p2", flower_type="tulip", total=1),
        PavilionFlowerNeedTotal(pavilion_id="p3", flower_type="rose", total=1),
        RobotPosition(node_id="n0", row=1, col=1),
        RobotState(node_id="n0", row=1, col=1),
        RobotEmpty(node_id="n0"),
        AtWarehouse(node_id="n0"),
        MaxCapacity(value=3),
        RobotCapacity(value=3),
        TotalCargoCount(node_id="n0", count=0),
        SearchNode(node_id="n0", parent_id="n0", action="start", g_cost=0, h_cost=0, f_cost=0),
        NodeCounter(value=1),
        OpenNode(node_id="n0", f_cost=0, g_cost=0),
    ]
    return facts

from facts.world_facts import (
    Grid, Warehouse, WarehouseStock, Pavilion, PavilionNeed, PavilionBouquetTotal,
)
from facts.robot_facts import RobotState, AtWarehouse, AtPavilion
from facts.cargo_facts import MaxCapacity, TotalCargoCount
from facts.search_facts import SearchNode, OpenNode, NodeCounter

from config.config import (
    GRID_ROWS, GRID_COLS,
    WAREHOUSE_POS, ROBOT_START,
    PAVILIONS, PAVILION_NEEDS, WAREHOUSE_STOCK,
)


def build_initial_facts():
    facts = []

    facts.append(Grid(rows=GRID_ROWS, cols=GRID_COLS))

    wh_row, wh_col = WAREHOUSE_POS
    facts.append(Warehouse(row=wh_row, col=wh_col))

    for ft, col in WAREHOUSE_STOCK:
        facts.append(WarehouseStock(flower_type=ft, color=col))

    max_need = 0
    for pav_id, pos in PAVILIONS.items():
        prow, pcol = pos
        facts.append(Pavilion(id=pav_id, row=prow, col=pcol))
        needs = PAVILION_NEEDS.get(pav_id, [])
        total_for_pav = 0
        for ft, col, qty in needs:
            facts.append(PavilionNeed(
                pavilion_id=pav_id, flower_type=ft, color=col, quantity=qty,
            ))
            total_for_pav += qty
        facts.append(PavilionBouquetTotal(pavilion_id=pav_id, total=total_for_pav))
        if total_for_pav > max_need:
            max_need = total_for_pav

    facts.append(MaxCapacity(value=max_need))

    root_id = "n0"
    rr, rc = ROBOT_START
    facts.append(SearchNode(
        node_id=root_id, parent_id=root_id,
        action="start", g_cost=0, h_cost=0, f_cost=0,
    ))
    facts.append(RobotState(node_id=root_id, row=rr, col=rc))
    facts.append(TotalCargoCount(node_id=root_id, count=0))
    facts.append(NodeCounter(value=1))
    facts.append(OpenNode(node_id=root_id, f_cost=0, g_cost=0))

    if rr == wh_row and rc == wh_col:
        facts.append(AtWarehouse(node_id=root_id))
    else:
        for pav_id, pos in PAVILIONS.items():
            if pos == (rr, rc):
                facts.append(AtPavilion(node_id=root_id, pavilion_id=pav_id))

    return facts

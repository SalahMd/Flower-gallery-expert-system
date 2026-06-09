from facts.world_facts import (
    Grid, Cell, NeighborCell, Warehouse, WarehouseStock, Pavilion,
    FlowerKind, FlowerColor, Bouquet,
    PavilionNeed, PavilionBouquetTotal,
    PavilionColorNeedTotal, PavilionFlowerNeedTotal,
)
from facts.robot_facts import RobotPosition, RobotState, RobotCapacity, RobotEmpty
from facts.cargo_facts import MaxCapacity, TotalCargoCount
from facts.search_facts import SearchNode, OpenNode, NodeCounter


def build_initial_facts():
    return [

        # =========================
        # GRID 3x3
        # =========================
        Grid(rows=3, cols=3),

        Cell(0,0), Cell(0,1), Cell(0,2),
        Cell(1,0), Cell(1,1), Cell(1,2),
        Cell(2,0), Cell(2,1), Cell(2,2),

        # =========================
        # NEIGHBORS (simplified)
        # =========================
        NeighborCell(0,0,"right",0,1),
        NeighborCell(0,1,"left",0,0),
        NeighborCell(0,1,"right",0,2),
        NeighborCell(0,2,"left",0,1),

        NeighborCell(1,0,"right",1,1),
        NeighborCell(1,1,"left",1,0),
        NeighborCell(1,1,"right",1,2),
        NeighborCell(1,2,"left",1,1),

        NeighborCell(2,0,"right",2,1),
        NeighborCell(2,1,"left",2,0),
        NeighborCell(2,1,"right",2,2),
        NeighborCell(2,2,"left",2,1),

        NeighborCell(0,0,"down",1,0),
        NeighborCell(1,0,"up",0,0),
        NeighborCell(1,0,"down",2,0),
        NeighborCell(2,0,"up",1,0),

        NeighborCell(0,1,"down",1,1),
        NeighborCell(1,1,"up",0,1),
        NeighborCell(1,1,"down",2,1),
        NeighborCell(2,1,"up",1,1),

        NeighborCell(0,2,"down",1,2),
        NeighborCell(1,2,"up",0,2),
        NeighborCell(1,2,"down",2,2),
        NeighborCell(2,2,"up",1,2),

        # =========================
        # WORLD SETUP
        # =========================
        Warehouse(row=1, col=1),

        Pavilion(id="p1", row=0, col=2),
        Pavilion(id="p2", row=2, col=0),
        Pavilion(id="p3", row=2, col=2),

        # =========================
        # MINIMAL FLOWER TYPES
        # =========================
        FlowerKind("rose"),
        FlowerKind("tulip"),

        FlowerColor("red"),
        FlowerColor("yellow"),

        Bouquet("rose", "red"),
        Bouquet("tulip", "yellow"),

        WarehouseStock("rose", "red"),
        WarehouseStock("tulip", "yellow"),

        # =========================
        # SIMPLE PAVILION NEEDS
        # =========================
        PavilionNeed("p1", "rose", "red", 1),
        PavilionNeed("p2", "tulip", "yellow", 1),
        PavilionNeed("p3", "rose", "red", 1),

        # =========================
        # TOTALS (simplified)
        # =========================
        PavilionBouquetTotal("p1", 1),
        PavilionBouquetTotal("p2", 1),
        PavilionBouquetTotal("p3", 1),

        PavilionColorNeedTotal("p1", "red", 1),
        PavilionColorNeedTotal("p2", "yellow", 1),
        PavilionColorNeedTotal("p3", "red", 1),

        PavilionFlowerNeedTotal("p1", "rose", 1),
        PavilionFlowerNeedTotal("p2", "tulip", 1),
        PavilionFlowerNeedTotal("p3", "rose", 1),

        # =========================
        # ROBOT START
        # =========================
        RobotPosition("n0", 1, 1),
        RobotState("n0", 1, 1),
        RobotEmpty("n0"),

        MaxCapacity(2),
        RobotCapacity(2),
        TotalCargoCount("n0", 0),

        # =========================
        # SEARCH INIT
        # =========================
        SearchNode(
            node_id="n0",
            parent_id="n0",
            action="start",
            g_cost=0,
            h_cost=0,
            f_cost=0
        ),

        NodeCounter(value=1),

        OpenNode(node_id="n0", f_cost=0, g_cost=0),
    ]
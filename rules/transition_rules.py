from experta import KnowledgeEngine, Rule, AS, NOT, MATCH, TEST
from facts.search_facts import (
    StateCopy, LoadApply, UnloadColorApply, UnloadPavilionApply, Delivered,
    PendingCargoTotal, CargoLineCounted, PavilionHasExtraCargo,
)
from facts.robot_facts import RobotState, AtWarehouse, AtPavilion
from facts.cargo_facts import CargoItem, TotalCargoCount
from facts.world_facts import Warehouse, Pavilion, PavilionNeed, PavilionBouquetTotal


class TransitionRules(KnowledgeEngine):

    @Rule(
        StateCopy(parent_id=MATCH.pid, child_id=MATCH.cid),
        Delivered(node_id=MATCH.pid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty),
        NOT(Delivered(node_id=MATCH.cid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
    )
    def copy_delivered(self, pid, cid, pav, ft, col, qty):
        self.declare(Delivered(node_id=cid, pavilion_id=pav, flower_type=ft, color=col, quantity=qty))

    @Rule(
        StateCopy(parent_id=MATCH.pid, child_id=MATCH.cid),
        CargoItem(node_id=MATCH.pid, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty),
        NOT(CargoItem(node_id=MATCH.cid, flower_type=MATCH.ft, color=MATCH.col)),
    )
    def copy_cargo_line(self, pid, cid, ft, col, qty):
        self.declare(CargoItem(node_id=cid, flower_type=ft, color=col, quantity=qty))

    @Rule(
        StateCopy(parent_id=MATCH.pid, child_id=MATCH.cid),
        TotalCargoCount(node_id=MATCH.pid, count=MATCH.cnt),
        NOT(TotalCargoCount(node_id=MATCH.cid)),
    )
    def copy_cargo_total(self, pid, cid, cnt):
        self.declare(TotalCargoCount(node_id=cid, count=cnt))

    @Rule(
        StateCopy(parent_id=MATCH.pid, child_id=MATCH.cid),
        RobotState(node_id=MATCH.cid, row=MATCH.row, col=MATCH.col),
        Warehouse(row=MATCH.row, col=MATCH.col),
        NOT(AtWarehouse(node_id=MATCH.cid)),
    )
    def copy_at_warehouse(self, pid, cid, row, col):
        self.declare(AtWarehouse(node_id=cid))

    @Rule(
        StateCopy(parent_id=MATCH.pid, child_id=MATCH.cid),
        RobotState(node_id=MATCH.cid, row=MATCH.row, col=MATCH.col),
        Pavilion(id=MATCH.pav_id, row=MATCH.row, col=MATCH.col),
        NOT(AtPavilion(node_id=MATCH.cid, pavilion_id=MATCH.pav_id)),
    )
    def copy_at_pavilion(self, pid, cid, pav_id, row, col):
        self.declare(AtPavilion(node_id=cid, pavilion_id=pav_id))

    @Rule(
        AS.sc << StateCopy(parent_id=MATCH.pid, child_id=MATCH.cid),
        TotalCargoCount(node_id=MATCH.cid),
        salience=1,
    )
    def cleanup_state_copy(self, sc, pid, cid):
        self.retract(sc)

    @Rule(
        LoadApply(parent_id=MATCH.pid, child_id=MATCH.cid, flower_type=MATCH.lft, color=MATCH.lcol),
        Delivered(node_id=MATCH.pid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty),
        NOT(Delivered(node_id=MATCH.cid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
    )
    def load_copy_delivered(self, pid, cid, pav, ft, col, qty, lft, lcol):
        self.declare(Delivered(node_id=cid, pavilion_id=pav, flower_type=ft, color=col, quantity=qty))

    @Rule(
        LoadApply(parent_id=MATCH.pid, child_id=MATCH.cid, flower_type=MATCH.lft, color=MATCH.lcol),
        CargoItem(node_id=MATCH.pid, flower_type=MATCH.lft, color=MATCH.lcol, quantity=MATCH.qty),
        NOT(CargoItem(node_id=MATCH.cid, flower_type=MATCH.lft, color=MATCH.lcol)),
    )
    def load_bump_same_line(self, pid, cid, lft, lcol, qty):
        self.declare(CargoItem(node_id=cid, flower_type=lft, color=lcol, quantity=qty + 1))

    @Rule(
        LoadApply(parent_id=MATCH.pid, child_id=MATCH.cid, flower_type=MATCH.lft, color=MATCH.lcol),
        CargoItem(node_id=MATCH.pid, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty),
        NOT(CargoItem(node_id=MATCH.cid, flower_type=MATCH.ft, color=MATCH.col)),
        TEST(lambda ft, lft, col, lcol: ft != lft or col != lcol),
    )
    def load_copy_other_line(self, pid, cid, lft, lcol, ft, col, qty):
        self.declare(CargoItem(node_id=cid, flower_type=ft, color=col, quantity=qty))

    @Rule(
        LoadApply(parent_id=MATCH.pid, child_id=MATCH.cid, flower_type=MATCH.lft, color=MATCH.lcol),
        NOT(CargoItem(node_id=MATCH.pid, flower_type=MATCH.lft, color=MATCH.lcol)),
        NOT(CargoItem(node_id=MATCH.cid, flower_type=MATCH.lft, color=MATCH.lcol)),
    )
    def load_new_line(self, pid, cid, lft, lcol):
        self.declare(CargoItem(node_id=cid, flower_type=lft, color=lcol, quantity=1))

    @Rule(
        LoadApply(parent_id=MATCH.pid, child_id=MATCH.cid),
        TotalCargoCount(node_id=MATCH.pid, count=MATCH.cnt),
        NOT(TotalCargoCount(node_id=MATCH.cid)),
    )
    def load_bump_total(self, pid, cid, cnt):
        self.declare(TotalCargoCount(node_id=cid, count=cnt + 1))

    @Rule(
        LoadApply(parent_id=MATCH.pid, child_id=MATCH.cid),
        RobotState(node_id=MATCH.cid, row=MATCH.row, col=MATCH.col),
        NOT(AtWarehouse(node_id=MATCH.cid)),
    )
    def load_stay_at_warehouse(self, pid, cid, row, col):
        self.declare(AtWarehouse(node_id=cid))

    @Rule(
        AS.la << LoadApply(parent_id=MATCH.pid, child_id=MATCH.cid),
        TotalCargoCount(node_id=MATCH.cid),
        salience=1,
    )
    def cleanup_load_apply(self, la, pid, cid):
        self.retract(la)

    @Rule(
        UnloadColorApply(parent_id=MATCH.pid, child_id=MATCH.cid, pavilion_id=MATCH.action_pav, flower_type=MATCH.uft, color=MATCH.ucol),
        Delivered(node_id=MATCH.pid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty),
        NOT(Delivered(node_id=MATCH.cid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
    )
    def unload_color_copy_delivered(self, pid, cid, action_pav, pav, ft, col, qty, uft, ucol):
        self.declare(Delivered(node_id=cid, pavilion_id=pav, flower_type=ft, color=col, quantity=qty))

    @Rule(
        UnloadColorApply(parent_id=MATCH.pid, child_id=MATCH.cid, pavilion_id=MATCH.pav, flower_type=MATCH.uft, color=MATCH.ucol),
        PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.uft, color=MATCH.ucol, quantity=MATCH.needed),
        NOT(Delivered(node_id=MATCH.cid, pavilion_id=MATCH.pav, flower_type=MATCH.uft, color=MATCH.ucol)),
    )
    def unload_color_mark_delivered(self, pid, cid, pav, uft, ucol, needed):
        self.declare(Delivered(node_id=cid, pavilion_id=pav, flower_type=uft, color=ucol, quantity=needed))

    @Rule(
        UnloadColorApply(parent_id=MATCH.pid, child_id=MATCH.cid, flower_type=MATCH.uft, color=MATCH.ucol),
        CargoItem(node_id=MATCH.pid, flower_type=MATCH.uft, color=MATCH.ucol, quantity=MATCH.qty),
        PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.uft, color=MATCH.ucol, quantity=MATCH.needed),
        NOT(CargoItem(node_id=MATCH.cid, flower_type=MATCH.uft, color=MATCH.ucol)),
        TEST(lambda qty, needed: qty > needed),
    )
    def unload_color_reduce_line(self, pid, cid, uft, ucol, qty, needed, pav):
        self.declare(CargoItem(node_id=cid, flower_type=uft, color=ucol, quantity=qty - needed))

    @Rule(
        UnloadColorApply(parent_id=MATCH.pid, child_id=MATCH.cid, flower_type=MATCH.uft, color=MATCH.ucol),
        CargoItem(node_id=MATCH.pid, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty),
        NOT(CargoItem(node_id=MATCH.cid, flower_type=MATCH.ft, color=MATCH.col)),
        TEST(lambda ft, uft, col, ucol: ft != uft or col != ucol),
    )
    def unload_color_copy_other_line(self, pid, cid, uft, ucol, ft, col, qty):
        self.declare(CargoItem(node_id=cid, flower_type=ft, color=col, quantity=qty))

    @Rule(
        AS.uca << UnloadColorApply(parent_id=MATCH.pid, child_id=MATCH.cid, pavilion_id=MATCH.pav, flower_type=MATCH.uft, color=MATCH.ucol),
        TotalCargoCount(node_id=MATCH.pid, count=MATCH.cnt),
        PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.uft, color=MATCH.ucol, quantity=MATCH.needed),
        NOT(TotalCargoCount(node_id=MATCH.cid)),
    )
    def unload_color_total(self, uca, pid, cid, cnt, needed, pav, uft, ucol):
        self.declare(TotalCargoCount(node_id=cid, count=cnt - needed))

    @Rule(
        UnloadColorApply(parent_id=MATCH.pid, child_id=MATCH.cid),
        RobotState(node_id=MATCH.cid, row=MATCH.row, col=MATCH.col),
        Pavilion(id=MATCH.pav_id, row=MATCH.row, col=MATCH.col),
        NOT(AtPavilion(node_id=MATCH.cid, pavilion_id=MATCH.pav_id)),
    )
    def unload_color_stay_at_pavilion(self, pid, cid, pav_id, row, col):
        self.declare(AtPavilion(node_id=cid, pavilion_id=pav_id))

    @Rule(
        AS.uca << UnloadColorApply(parent_id=MATCH.pid, child_id=MATCH.cid, pavilion_id=MATCH.pav, flower_type=MATCH.uft, color=MATCH.ucol),
        TotalCargoCount(node_id=MATCH.cid),
        salience=1,
    )
    def cleanup_unload_color_apply(self, uca, pid, cid, pav, uft, ucol):
        self.retract(uca)

    @Rule(
        UnloadPavilionApply(parent_id=MATCH.pid, child_id=MATCH.cid, pavilion_id=MATCH.action_pav),
        Delivered(node_id=MATCH.pid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty),
        NOT(Delivered(node_id=MATCH.cid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
    )
    def unload_pav_copy_old_delivered(self, pid, cid, action_pav, pav, ft, col, qty):
        self.declare(Delivered(node_id=cid, pavilion_id=pav, flower_type=ft, color=col, quantity=qty))

    @Rule(
        UnloadPavilionApply(parent_id=MATCH.pid, child_id=MATCH.cid, pavilion_id=MATCH.pav),
        PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.needed),
        NOT(Delivered(node_id=MATCH.cid, pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
    )
    def unload_pav_mark_each_need(self, pid, cid, pav, ft, col, needed):
        self.declare(Delivered(node_id=cid, pavilion_id=pav, flower_type=ft, color=col, quantity=needed))

    @Rule(
        UnloadPavilionApply(parent_id=MATCH.pid, child_id=MATCH.cid, pavilion_id=MATCH.pav),
        CargoItem(node_id=MATCH.pid, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty),
        PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.needed),
        NOT(CargoItem(node_id=MATCH.cid, flower_type=MATCH.ft, color=MATCH.col)),
        TEST(lambda qty, needed: qty == needed),
    )
    def unload_pav_clear_used_line(self, pid, cid, pav, ft, col, qty, needed):
        pass

    @Rule(
        UnloadPavilionApply(parent_id=MATCH.pid, child_id=MATCH.cid, pavilion_id=MATCH.pav),
        CargoItem(node_id=MATCH.pid, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty),
        PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.needed),
        NOT(CargoItem(node_id=MATCH.cid, flower_type=MATCH.ft, color=MATCH.col)),
        TEST(lambda qty, needed: qty > needed),
    )
    def unload_pav_drop_partial(self, pid, cid, pav, ft, col, qty, needed):
        self.declare(CargoItem(node_id=cid, flower_type=ft, color=col, quantity=qty - needed))

    @Rule(
        UnloadPavilionApply(parent_id=MATCH.pid, child_id=MATCH.cid, pavilion_id=MATCH.pav),
        CargoItem(node_id=MATCH.pid, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty),
        NOT(PavilionNeed(pavilion_id=MATCH.pav, flower_type=MATCH.ft, color=MATCH.col)),
        NOT(CargoItem(node_id=MATCH.cid, flower_type=MATCH.ft, color=MATCH.col)),
    )
    def unload_pav_keep_other_cargo(self, pid, cid, pav, ft, col, qty):
        self.declare(CargoItem(node_id=cid, flower_type=ft, color=col, quantity=qty))

    @Rule(
        UnloadPavilionApply(parent_id=MATCH.pid, child_id=MATCH.cid),
        NOT(PendingCargoTotal(child_id=MATCH.cid)),
    )
    def unload_pav_start_total(self, pid, cid):
        self.declare(PendingCargoTotal(child_id=cid, total=0))

    @Rule(
        UnloadPavilionApply(parent_id=MATCH.pid, child_id=MATCH.cid),
        AS.pt << PendingCargoTotal(child_id=MATCH.cid, total=MATCH.t),
        CargoItem(node_id=MATCH.cid, flower_type=MATCH.ft, color=MATCH.col, quantity=MATCH.qty),
        NOT(CargoLineCounted(child_id=MATCH.cid, flower_type=MATCH.ft, color=MATCH.col)),
    )
    def unload_pav_add_total(self, pt, pid, cid, t, ft, col, qty):
        self.retract(pt)
        self.declare(PendingCargoTotal(child_id=cid, total=t + qty))
        self.declare(CargoLineCounted(child_id=cid, flower_type=ft, color=col))

    @Rule(
        UnloadPavilionApply(parent_id=MATCH.pid, child_id=MATCH.cid, pavilion_id=MATCH.pav),
        TotalCargoCount(node_id=MATCH.pid, count=MATCH.cnt),
        PavilionBouquetTotal(pavilion_id=MATCH.pav, total=MATCH.drop),
        NOT(PavilionHasExtraCargo(node_id=MATCH.pid, pavilion_id=MATCH.pav)),
        NOT(TotalCargoCount(node_id=MATCH.cid)),
    )
    def unload_pav_total_clean(self, pid, cid, pav, cnt, drop):
        self.declare(TotalCargoCount(node_id=cid, count=cnt - drop))

    @Rule(
        UnloadPavilionApply(parent_id=MATCH.pid, child_id=MATCH.cid),
        PendingCargoTotal(child_id=MATCH.cid, total=MATCH.t),
        NOT(TotalCargoCount(node_id=MATCH.cid)),
        NOT(CargoItem(node_id=MATCH.cid)),
    )
    def unload_pav_finish_counted(self, pid, cid, t):
        self.declare(TotalCargoCount(node_id=cid, count=t))

    @Rule(
        UnloadPavilionApply(parent_id=MATCH.pid, child_id=MATCH.cid),
        RobotState(node_id=MATCH.cid, row=MATCH.row, col=MATCH.col),
        Pavilion(id=MATCH.pav_id, row=MATCH.row, col=MATCH.col),
        NOT(AtPavilion(node_id=MATCH.cid, pavilion_id=MATCH.pav_id)),
    )
    def unload_pav_stay(self, pid, cid, pav_id, row, col):
        self.declare(AtPavilion(node_id=cid, pavilion_id=pav_id))

    @Rule(
        AS.upa << UnloadPavilionApply(parent_id=MATCH.pid, child_id=MATCH.cid, pavilion_id=MATCH.pav),
        TotalCargoCount(node_id=MATCH.cid),
        salience=1,
    )
    def cleanup_unload_pav_apply(self, upa, pid, cid, pav):
        self.retract(upa)

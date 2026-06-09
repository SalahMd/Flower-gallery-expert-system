from experta import Fact, Field


class SearchNode(Fact):
    node_id = Field(str)
    parent_id = Field(str)
    action = Field(str)
    g_cost = Field(int)
    h_cost = Field(int)
    f_cost = Field(int)


class OpenNode(Fact):
    node_id = Field(str)
    f_cost = Field(int)
    g_cost = Field(int)


class ClosedNode(Fact):
    node_id = Field(str)


class CurrentNode(Fact):
    node_id = Field(str)


class GoalNode(Fact):
    node_id = Field(str)


class SearchStopped(Fact):
    max_steps = Field(int)


class OutputHeader(Fact):
    name = Field(str)


class OutputNode(Fact):
    name = Field(str)
    node_id = Field(str)


class OutputBacktrack(Fact):
    node_id = Field(str)
    parent_id = Field(str)


class StateCost(Fact):
    node_id = Field(str)
    g_cost = Field(int)
    h_cost = Field(int)
    f_cost = Field(int)


class Delivered(Fact):
    node_id = Field(str)
    pavilion_id = Field(str)
    flower_type = Field(str)
    color = Field(str)
    quantity = Field(int)


class NodeCounter(Fact):
    value = Field(int)


class NextNodeId(Fact):
    parent_id = Field(str)
    child_id = Field(str)


class Phase(Fact):
    name = Field(str)


class PendingSuccessor(Fact):
    slot = Field(str)
    parent_id = Field(str)


class MoveGenerated(Fact):
    parent_id = Field(str)
    direction = Field(str)
    row = Field(int, mandatory=False)
    col = Field(int, mandatory=False)


class LoadGenerated(Fact):
    parent_id = Field(str)
    flower_type = Field(str)
    color = Field(str)


class UnloadColorGenerated(Fact):
    parent_id = Field(str)
    pavilion_id = Field(str)
    flower_type = Field(str)
    color = Field(str)


class UnloadPavilionGenerated(Fact):
    parent_id = Field(str)
    pavilion_id = Field(str)


class PendingH(Fact):
    node_id = Field(str)
    value = Field(int)


class HProcessed(Fact):
    node_id = Field(str)
    pavilion_id = Field(str)
    flower_type = Field(str)
    color = Field(str)


class UnsatisfiedNeed(Fact):
    node_id = Field(str)
    pavilion_id = Field(str)
    flower_type = Field(str)
    color = Field(str)


class NotBest(Fact):
    node_id = Field(str)
    eliminated_by = Field(str)


class StateCopy(Fact):
    parent_id = Field(str)
    child_id = Field(str)


class LoadApply(Fact):
    parent_id = Field(str)
    child_id = Field(str)
    flower_type = Field(str)
    color = Field(str)


class UnloadColorApply(Fact):
    parent_id = Field(str)
    child_id = Field(str)
    pavilion_id = Field(str)
    flower_type = Field(str)
    color = Field(str)


class UnloadPavilionApply(Fact):
    parent_id = Field(str)
    child_id = Field(str)
    pavilion_id = Field(str)


class GoalBlocked(Fact):
    node_id = Field(str)


class ExpandCleanup(Fact):
    parent_id = Field(str)


class ExpandVisited(Fact):
    node_id = Field(str)


class ExpandStarted(Fact):
    node_id = Field(str)


class NeedScore(Fact):
    node_id = Field(str)


class PavilionNeedUnmet(Fact):
    node_id = Field(str)
    pavilion_id = Field(str)


class PavilionHasExtraCargo(Fact):
    node_id = Field(str)
    pavilion_id = Field(str)


class PendingCargoTotal(Fact):
    child_id = Field(str)
    total = Field(int)


class CargoLineCounted(Fact):
    child_id = Field(str)
    flower_type = Field(str)
    color = Field(str)


class ClosedPosSig(Fact):
    row = Field(int)
    col = Field(int)
    cargo_total = Field(int)
    node_id = Field(str)
    g_cost = Field(int)


class CargoSnap(Fact):
    node_id = Field(str)
    flower_type = Field(str)
    color = Field(str)
    quantity = Field(int)


class DelSnap(Fact):
    node_id = Field(str)
    pavilion_id = Field(str)
    flower_type = Field(str)
    color = Field(str)


class StateReady(Fact):
    node_id = Field(str)

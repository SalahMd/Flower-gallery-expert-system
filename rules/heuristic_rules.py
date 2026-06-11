
import math
from experta import KnowledgeEngine

class HeuristicRules(KnowledgeEngine):

    def compute_h(self, node_id):
        wh_row, wh_col = None, None
        for f in self.facts.values():
            if type(f).__name__ == "Warehouse":
                wh_row, wh_col = f["row"], f["col"]
                break

        robot_row, robot_col = None, None
        for f in self.facts.values():
            if type(f).__name__ == "RobotState" and f["node_id"] == node_id:
                robot_row, robot_col = f["row"], f["col"]
                break

        capacity = 1
        for f in self.facts.values():
            if type(f).__name__ == "MaxCapacity":
                capacity = f["value"]
                break

        cargo_count = 0
        for f in self.facts.values():
            if type(f).__name__ == "TotalCargoCount" and f["node_id"] == node_id:
                cargo_count = f["count"]
                break

        delivered = set()
        for f in self.facts.values():
            if type(f).__name__ == "Delivered" and f["node_id"] == node_id:
                delivered.add((f["pavilion_id"], f["flower_type"], f["color"]))

        pavilion_pos = {}
        for f in self.facts.values():
            if type(f).__name__ == "Pavilion":
                pavilion_pos[f["id"]] = (f["row"], f["col"])

        undelivered_pavs = set()
        for f in self.facts.values():
            if type(f).__name__ == "PavilionNeed":
                key = (f["pavilion_id"], f["flower_type"], f["color"])
                if key not in delivered:
                    undelivered_pavs.add(f["pavilion_id"])

        if not undelivered_pavs:
            return 0

        distances = []
        for pav_id in undelivered_pavs:
            pr, pc = pavilion_pos[pav_id]
            distances.append(abs(pr - wh_row) + abs(pc - wh_col))

        d_avg = sum(distances) / len(distances)
        trips = math.ceil(len(undelivered_pavs) / max(capacity, 1))
        d_robot_wh = abs(robot_row - wh_row) + abs(robot_col - wh_col)
        if cargo_count > 0:
            d_robot_wh = 0

        h = d_robot_wh + (trips - 1) * (2 * d_avg + 2) + d_avg + 2

        return int(math.floor(h))
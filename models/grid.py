from dataclasses import dataclass, field




CELL_EMPTY = "."
CELL_WAREHOUSE = "W"
CELL_ROBOT = "R"


@dataclass
class Grid:
    rows: int
    cols: int
    warehouse_pos: tuple
    warehouse_stock: set = field(default_factory=set)
    pavilions: set = field(default_factory=set)

    def pavilion_at(self, pos):
        for p in self.pavilions:
            if p.position == pos:
                return p
        return None

    def is_valid_position(self, pos):
        r, c = pos
        return (
            0 <= r < self.rows
            and 0 <= c < self.cols)

    def neighbors(self, pos):
        r, c = pos

        positions = [
            (r - 1, c),
            (r + 1, c),
            (r, c - 1),
            (r, c + 1),
        ]

        valid = []

        for p in positions:
            if self.is_valid_position(p):
                valid.append(p)

        return valid

    def render(self, robot_pos=None):
        lines = []

        pav_positions = {}

        for p in self.pavilions:
            pav_positions[p.position] = p.pavilion_id

        for r in range(self.rows):
            row = []

            for c in range(self.cols):
                pos = (r, c)


                if robot_pos and pos == robot_pos:
                    row.append(CELL_ROBOT)

                elif pos == self.warehouse_pos:
                    row.append(CELL_WAREHOUSE)

                elif pos in pav_positions:
                    row.append(pav_positions[pos][0])

                else:
                    row.append(CELL_EMPTY)

            lines.append(" ".join(row))

        return "\n".join(lines)
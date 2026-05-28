from dataclasses import dataclass, field

@dataclass
class Robot:
    position: tuple
    cargo: list = field(default_factory=list)
    capacity: int 

    def cargo_count(self):
        return len(self.cargo)

    def is_full(self):
        return len(self.cargo) >= self.capacity

    def is_empty(self):
        return len(self.cargo) == 0

    def can_load(self, bouquet):

        if self.is_full():
            return False

        if len(self.cargo) == 0:
            return True

        types = set()
        colors = set()

        for b in self.cargo:
            types.add(b.flower_type)
            colors.add(b.color)

        types.add(bouquet.flower_type)
        colors.add(bouquet.color)

        if len(types) > 1 and len(colors) > 1:
            return False

        return True

    def load(self, bouquet):
        self.cargo.append(bouquet)

    def unload(self, bouquet):
        if bouquet in self.cargo:
            self.cargo.remove(bouquet)

    def move(self, position):
        self.position = position

    def __repr__(self):
        return (
            f"Robot(pos={self.position}, "
            f"cargo={len(self.cargo)}, "
            f"capacity={self.capacity})"
        )
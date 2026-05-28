from dataclasses import dataclass, field

@dataclass
class Pavilion:
    pavilion_id: str
    position: tuple
    requests: list = field(default_factory=list)
    delivered: list = field(default_factory=list)

    def is_served(self):
        return len(self.requests) == 0

    def needs(self, bouquet):
        for b in self.requests:
            if (
                b.flower_type == bouquet.flower_type
                and b.color == bouquet.color
            ):
                return True

        return False

    def deliver(self, bouquet):
        for req in self.requests:

            if (
                req.flower_type == bouquet.flower_type
                and req.color == bouquet.color
            ):
                self.requests.remove(req)
                self.delivered.append(bouquet)
                return True

        return False

    def __repr__(self):
        reqs = []
        for b in self.requests:
            reqs.append(f"{b.flower_type}/{b.color}")

        return (
            f"Pavilion(id={self.pavilion_id}, "
            f"pos={self.position}, "
            f"pending={reqs})"
        )
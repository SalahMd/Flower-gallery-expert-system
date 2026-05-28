import uuid


class Bouquet:
    def __init__(self, flower_type, color):
        self.flower_type = flower_type
        self.color = color
        self.bouquet_id = str(uuid.uuid4())[:8]

    def matches(self, flower_type=None, color=None):
        if flower_type and self.flower_type != flower_type:
            return False

        if color and self.color != color:
            return False

        return True

    def __repr__(self):
        return f"Bouquet(id={self.bouquet_id}, type={self.flower_type}, color={self.color})"
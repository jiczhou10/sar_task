from matrx.objects import EnvObject

class Obstacle(EnvObject):
    def __init__(self, location, name, img_name, time_to_remove=None, blocks_path=False, style=75):
        super().__init__(location=location,
                         name=name,
                         is_traversable=False,
                         is_movable=True,
                         img_name=img_name,
                         class_callable=Obstacle
                         )
        if time_to_remove is None:
            time_to_remove = 0
        self.time_to_remove = time_to_remove
        self.blocks_path = blocks_path
        self.style = style
        self.custom_properties = {"img_name": img_name,
                                  "time_to_remove": self.time_to_remove,
                                  "blocks_path": self.blocks_path,
                                  "style": style}


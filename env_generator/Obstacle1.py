from matrx.objects import EnvObject


class Obstacle1(EnvObject):
    def __init__(self, location, name, img_name, type):
        super().__init__(location=location,
                         name=name,
                         is_traversable=False,
                         is_movable=True,
                         img_name=img_name,
                         class_callable=Obstacle1
                         )
        self.custom_properties = {
            "type": type,
            "img_name": img_name
        }

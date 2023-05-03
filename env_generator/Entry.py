from matrx.objects import EnvObject


class Entry(EnvObject):
    def __init__(self, location, name, visualize_colour, visualize_opacity):
        super().__init__(location=location,
                         name=name,
                         is_traversable=True,
                         class_callable=Entry,
                         visualize_colour='8a8a8a',
                         visualize_opacity=0.0
                         )


from matrx.objects import EnvObject


# class CollectableBlock(EnvObject):
#     def __init__(self, location, name, visualize_shape, img_name):
#         super().__init__(location, name, is_traversable=True, is_movable=True,
#                          visualize_shape=visualize_shape,img_name=img_name,
#                          class_callable=CollectableBlock, is_collectable=True)

class Victim1(EnvObject):
    def __init__(self, location, name, img_name, type, critically_injured=False,
                 time_to_rescue=0):
        super().__init__(location=location,
                         name=name,
                         is_traversable=True,
                         is_movable=True,
                         img_name=img_name,
                         class_callable=Victim1,
                         is_collectable=True
                         )
        self.custom_properties = {
            "type": type,
            "img_name": img_name,
            "critically_injured": critically_injured,
            "time_to_rescue": time_to_rescue
        }

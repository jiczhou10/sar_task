from matrx import WorldBuilder
from matrx.actions.move_actions import *
from matrx.agents import HumanAgentBrain


# def create_builder():
#     tick = 0.1
#     # Create our builder
#     builder = WorldBuilder(shape=[25, 25], run_matrx_api=True, run_matrx_visualizer=True,
#                            visualization_bg_clr="#FFFFE0", tick_duration=tick)
#
#     # Add the walls surrounding the maze
#     builder.add_room(top_left_location=[0, 0], width=14, height=13, name="Borders")
#
#     # Add the walls to our maze
#     builder.add_line(start=[2, 2], end=[6, 2], name="Maze wall", visualize_colour="#966F33", is_movable=False)
#     builder.add_line(start=[8, 2], end=[11, 2], name="Maze wall", visualize_colour="#966F33", is_movable=False)
#     builder.add_line(start=[2, 3], end=[2, 5], name="Maze wall", visualize_colour="#966F33", is_movable=False)
#     builder.add_line(start=[11, 3], end=[11, 5], name="Maze wall", visualize_colour="#966F33", is_movable=False)
#     builder.add_line(start=[6, 4], end=[8, 4], name="Maze wall", visualize_colour="#966F33", is_movable=False)
#     builder.add_line(start=[9, 4], end=[9, 7], name="Maze wall", visualize_colour="#966F33", is_movable=False)
#     builder.add_line(start=[6, 5], end=[6, 6], name="Maze wall", visualize_colour="#966F33", is_movable=False)
#     builder.add_line(start=[4, 4], end=[4, 8], name="Maze wall", visualize_colour="#966F33", is_movable=False)
#     builder.add_line(start=[5, 8], end=[9, 8], name="Maze wall", visualize_colour="#966F33", is_movable=False)
#     builder.add_line(start=[2, 7], end=[2, 9], name="Maze wall", visualize_colour="#966F33", is_movable=False)
#     builder.add_line(start=[11, 7], end=[11, 9], name="Maze wall", visualize_colour="#966F33", is_movable=False)
#     builder.add_line(start=[2, 10], end=[5, 10], name="Maze wall", visualize_colour="#966F33", is_movable=False)
#     builder.add_line(start=[7, 10], end=[11, 10], name="Maze wall", visualize_colour="#966F33", is_movable=False)
#
#     # add a treasure as human's goal
#     builder.add_object(location=[7, 5], name="Treasure", visualize_colour="FFD700",
#                        is_traversable=True)
#
#     key_action = {
#         'w': MoveNorth.__name__,
#         'd': MoveEast.__name__,
#         's': MoveSouth.__name__,
#         'a': MoveWest.__name__,
#     }
#     brain = HumanAgentBrain()
#     builder.add_human_agent(location=[3, 1], agent_brain=brain, name="Human", key_action_map=key_action,
#                             img_name="/static/images/rescue.png")
#
#     # Return the builder
#     return builder

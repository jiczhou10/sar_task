import random
import os
import numpy as np
from datetime import datetime
from matrx import WorldBuilder
from matrx.actions.move_actions import *
from matrx.agents import SenseCapability
from SAR_agent.human_agent import CustomHumanAgent
from action.custom_actions import DropObjectTogether, CarryObjectTogether, RemoveObjectTogether, RemoveObject, CarryObject, DropObjectAlone
from SAR_agent.sar_agent_1 import SarAgent1
from SAR_agent.sar_agent_2 import SarAgent2
from env_generator.Victim import Victim
from env_generator.Obstacle import Obstacle
from env_generator.Entry import Entry
from env_generator.Obstacle1 import Obstacle1
from env_generator.Victim1 import Victim1
from matrx.objects import EnvObject
from matrx.goals import LimitedTimeGoal
from action.agent_actions import RemoveAlone
from SAR_agent.tutorial_agent import TutorialAgent
from logs.message_logger import MessageLogger
from logs.action_logger import ActionLogger

media_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "images")
agent_sense_range = 3
# agent_sense_range = np.inf
block_sense_range = 1
# block_sense_range = np.inf
other_sense_range = np.inf
max_nr_ticks = 9600

key_action = {
    'w': MoveNorth.__name__,
    'd': MoveEast.__name__,
    's': MoveSouth.__name__,
    'a': MoveWest.__name__,
    'ArrowUp': MoveNorth.__name__,
    'ArrowRight': MoveEast.__name__,
    'ArrowDown': MoveSouth.__name__,
    'ArrowLeft': MoveWest.__name__,
    'g': CarryObject.__name__,
    'r': RemoveObject.__name__,
    'q': DropObjectAlone.__name__,
    'c': CarryObjectTogether.__name__,
    'x': DropObjectTogether.__name__,
    'p': RemoveObjectTogether.__name__
}

sense_capability = SenseCapability({AgentBody: agent_sense_range,
                                    Victim: block_sense_range,
                                    # Victim1: block_sense_range,
                                    Obstacle: block_sense_range,
                                    # Obstacle1: block_sense_range,
                                    None: other_sense_range})
robot_sense_capability = SenseCapability({AgentBody: np.inf,
                                          Victim: block_sense_range,
                                        # Victim1: block_sense_range,
                                          # Obstacle: block_sense_range,
                                          None: other_sense_range})

firstAgent = None
visualization_color = "#cfc8bc"


def add_agents_first(builder, rnd):

    humanBrain = CustomHumanAgent()

    if rnd == 0:
        agentBrain = SarAgent1()
        agent_location = [28, 28]
        human_location = [1, 1]
    elif rnd == 1:
        agentBrain = SarAgent2()
        agent_location = [28, 28]
        human_location = [1, 1]

    builder.add_agent(location=agent_location, agent_brain=agentBrain, name="agent",
                          is_traversable=True, visualize_size=1, img_name="robot.png",
                          sense_capability=robot_sense_capability, customizable_properties=['score', 'nr_victims', 'is_busy'],
                          visualize_when_busy=True, score=0, nr_victims=0, is_busy=False)

    builder.add_human_agent(location=human_location, agent_brain=humanBrain, name="human",
                                key_action_map=key_action, is_traversable=True, img_name="human.png",
                                customizable_properties=['score', 'nr_victims'], sense_capability=sense_capability,
                                visualize_when_busy=True, score=0, nr_victims=0)
#     sense_capability=sense_capability,


def add_agents_second(builder, rnd):
    humanBrain = CustomHumanAgent()

    if rnd == 0:
        agentBrain = SarAgent1()
        # then firstAgent == sar_agent_1
        agent_location = [28, 28]
        human_location = [1, 1]
    elif rnd == 1:
        agentBrain = SarAgent2()
        # then firstAgent == sar_agent_2
        agent_location = [28, 28]
        human_location = [1, 1]

    builder.add_agent(location=agent_location, agent_brain=agentBrain, name="agent",
                          is_traversable=True, visualize_size=1, img_name="robot.png",
                          sense_capability=robot_sense_capability, customizable_properties=['score', 'nr_victims', 'is_busy'],
                          visualize_when_busy=True, score=0, nr_victims=0, is_busy=False)

    builder.add_human_agent(location=human_location, agent_brain=humanBrain, name="human",
                                key_action_map=key_action, is_traversable=True, img_name="human.png",
                                customizable_properties=['score', 'nr_victims'], sense_capability=sense_capability,
                                visualize_when_busy=True, score=0, nr_victims=0)
    # sense_capability=sense_capability,
    # return rnd_seed


def create_builder_tutorial():
    tick = 0.05
    goal = LimitedTimeGoal(999999999999999)
    builder = WorldBuilder(shape=[30, 30], tick_duration=tick, run_matrx_api=True, run_matrx_visualizer=True,
                           verbose=False, visualization_bg_clr=visualization_color, visualization_bg_img="", simulation_goal=goal)

    current_exp_folder = datetime.now().strftime("task1_at_time_%Hh-%Mm-%Ss_date_%dd-%mm-%Yy")
    logger_save_folder = os.path.join("tutorial_log_results", current_exp_folder)
    builder.add_logger(ActionLogger, log_strategy=1, save_path=logger_save_folder, file_name_prefix="actions_")
    builder.add_logger(MessageLogger, save_path=logger_save_folder, file_name_prefix="messages_")

    builder.add_room(top_left_location=[0, 0], width=30, height=30, name="Borders")
    wall_color = '#8a8a8a'
    room_color = '#98a7ab'

    entry_loc = [[18, 5],
                 [5, 13], [12, 9], [19, 13], [23, 13],
                 [4, 14], [9, 14], [14, 17], [22, 18],
                 [7, 21], [11, 20], [18, 22],
                 [6, 26]]

    for i in entry_loc:
        builder.add_object(location=i, name='Entry', callable_class=Entry,
                           visualize_opacity=0)

    # build room A1
    builder.add_room(top_left_location=(3, 1), width=4, height=5, name='area A1', door_locations=[(3, 3)],
                     doors_open=True, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     door_visualization_opacity=0.5, wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "A1.svg"})
    builder.add_object(location=[3, 3], name="SmallRock1", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # door_custom_properties={"img_name": "Untitled.png"}

    # victim in area A1
    builder.add_object(location=[4, 4], name="HealthyManA1", callable_class=Victim, img_name="healthy_victim.png",
                       type='healthy', gender='him')

    # build room A2
    builder.add_room(top_left_location=(9, 1), width=4, height=4, name='area A2', door_locations=[(10, 4)],
                     doors_open=True,
                     door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "A2.svg"})
    builder.add_object(location=[10, 4], name="Tree", callable_class=Obstacle, img_name="tree.png",
                       type="tree")

    # victim in area A2
    builder.add_object(location=[11, 3], name="CriticalManA2", callable_class=Victim, img_name="critical_victim.png",
                       type='critical', gender='her')

    # build room A3
    builder.add_room(top_left_location=(15, 1), width=6, height=4, name='area A3', door_locations=[(18, 4)],
                     doors_open=True,
                     door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "A3.svg"})
    builder.add_object(location=[18, 4], name="large_rock", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim A3
    builder.add_object(location=[19, 2], name="InjuredManA3", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='him')

    builder.add_object(location=[1, 7], name="pine", img_name="pine.png", is_movable=False, is_traversable=False)
    builder.add_object(location=[2, 7], name="pine", img_name="pine.png", is_movable=False, is_traversable=False)

    # add line to separate intro area and simulation area
    builder.add_line(start=[1, 8], end=[13, 8], name="Redzone wall", is_traversable=False, is_movable=False)
    builder.add_line(start=[15, 8], end=[28, 8], name="Redzone wall", is_traversable=False, is_movable=False)
    builder.add_object(location=[14, 8], name='rock1',
                       callable_class=Obstacle, img_name='rock1.png', type='small')

    # add bush around safe zone
    builder.add_object(location=[23, 1], name="bush", img_name="bush.png", is_movable=False, is_traversable=False)

    # build room safe zone
    builder.add_room(top_left_location=(24, 1), width=5, height=7, name='safe_zone', door_locations=[(24, 4)],
                     doors_open=True,
                     door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.0,
                     wall_custom_properties={"img_name": "Untitled_2.png"})

    # build room B1
    builder.add_room(top_left_location=(1, 9), width=7, height=4, name='area B1', door_locations=[(5, 12)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "B1.svg"})
    builder.add_object(location=[5, 12], name="Tree", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim in area B1
    builder.add_object(location=[2, 10], name="CriticalManB1", callable_class=Victim, img_name="critical_victim.png",
                       type='critical', gender='him')

    # build room B2
    builder.add_room(top_left_location=(10, 10), width=4, height=4, name='area B2', door_locations=[(12, 10)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "B2.svg"})
    builder.add_object(location=[12, 10], name="SmallRock1", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim B2
    builder.add_object(location=[11, 12], name="HealthyManB2", callable_class=Victim, img_name="healthy_victim.png",
                       type='healthy', gender='her')

    # build room B3
    builder.add_room(top_left_location=(16, 9), width=6, height=4, name='area B3', door_locations=[(19, 12)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "B3.svg"})
    builder.add_object(location=[19, 12], name="Tree", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim B3
    builder.add_object(location=[20, 10], name="InjuredMan9", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='him')

    # build room B4
    builder.add_room(top_left_location=(24, 9), width=4, height=7, name='area B4', door_locations=[(24, 13)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "B4.svg"})
    builder.add_object(location=[24, 13], name="LargeRock", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim B4
    builder.add_object(location=[26, 10], name="InjuredMan9", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='her')

    # fence around B4
    builder.add_object(location=[28, 9], name="fence", img_name="fence.png", is_movable=False, is_traversable=False)
    builder.add_object(location=[28, 10], name="bush", img_name="bush.png", is_movable=False, is_traversable=False)

    # build room C1
    builder.add_room(top_left_location=(2, 15), width=4, height=4, name='area C1', door_locations=[(4, 15)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "C1.svg"})
    builder.add_object(location=[4, 15], name="SmallRock", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim C1
    builder.add_object(location=[3, 17], name="HealthyManC1", callable_class=Victim, img_name="healthy_victim.png",
                       type='healthy', gender='him')

    # build room C2
    builder.add_room(top_left_location=(7, 15), width=6, height=4, name='area C2', door_locations=[(9, 15)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "C2.svg"})
    builder.add_object(location=[9, 15], name="large_rock", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim C2
    builder.add_object(location=[11, 17], name="CriticalManC2", callable_class=Victim, img_name="critical_victim.png",
                       type='critical', gender='her')

    # build room C3
    builder.add_room(top_left_location=(15, 14), width=6, height=5, name='area C3', door_locations=[(15, 17)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "C3.svg"})
    builder.add_object(location=[15, 17], name="SmallRock", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim C3
    builder.add_object(location=[18, 15], name="InjuredMan9", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='him')

    # build room C4
    builder.add_room(top_left_location=(23, 17), width=6, height=4, name='area C4', door_locations=[(23, 18)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "C4.svg"})
    builder.add_object(location=[23, 18], name="Tree", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim C4
    builder.add_object(location=[27, 19], name="InjuredMan9", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='her')

    # build room D1
    builder.add_room(top_left_location=(1, 20), width=6, height=4, name='area D1', door_locations=[(6, 21)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "D1.svg"})
    builder.add_object(location=[6, 21], name="Tree", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim D1
    builder.add_object(location=[2, 22], name="InjuredMan9", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='him')

    # build room D2
    builder.add_room(top_left_location=(9, 21), width=4, height=6, name='area D2', door_locations=[(11, 21)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "D2.svg"})
    builder.add_object(location=[11, 21], name="SmallRock", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim D2
    builder.add_object(location=[10, 24], name="CriticalManD2", callable_class=Victim, img_name="critical_victim.png",
                       type='critical', gender='her')

    # pine around D2
    builder.add_object(location=[8, 24], name="pine", img_name="pine.png", is_movable=False, is_traversable=False)
    builder.add_object(location=[8, 25], name="pine", img_name="pine.png", is_movable=False, is_traversable=False)

    # build room D3
    builder.add_room(top_left_location=(14, 20), width=4, height=4, name='area D3', door_locations=[(17, 22)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "D3.svg"})
    builder.add_object(location=[17, 22], name="large_rock", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim D3
    builder.add_object(location=[15, 21], name="InjuredMan9", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='her')

    # build room E1
    builder.add_room(top_left_location=(2, 25), width=4, height=4, name='area E1', door_locations=[(5, 26)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "E1.svg"})
    builder.add_object(location=[5, 26], name="SmallRock", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim E1
    builder.add_object(location=[3, 27], name="InjuredMan9", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='her')

    # fence around E1
    builder.add_object(location=[1, 28], name="fence", img_name="fence.png", is_movable=False, is_traversable=False)

    # pine around safe zone
    builder.add_object(location=[17, 28], name="pine", img_name="pine.png", is_movable=False, is_traversable=False)
    builder.add_object(location=[18, 28], name="pine", img_name="pine.png", is_movable=False, is_traversable=False)

    # bush around safe zone
    builder.add_object(location=[22, 23], name="bush", img_name="bush.png", is_movable=False, is_traversable=False)
    builder.add_object(location=[23, 23], name="bush", img_name="bush.png", is_movable=False, is_traversable=False)
    builder.add_object(location=[24, 23], name="bush", img_name="bush.png", is_movable=False, is_traversable=False)

    # build safe zone
    builder.add_room(top_left_location=(19, 24), width=9, height=5, name='safe_zone', door_locations=[(20, 24)],
                     doors_open=True, wall_visualize_colour="#00a000",
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled_2.png"})

    humanBrain = CustomHumanAgent()
    agentBrain = TutorialAgent()

    builder.add_agent(location=[2, 1], agent_brain=agentBrain, name="agent",
                      is_traversable=True, visualize_size=1, img_name="robot.png",
                      customizable_properties=['score', 'nr_victims'],
                      sense_capability=robot_sense_capability, score=0, nr_victims=0, visualize_when_busy=True)

    builder.add_human_agent(location=[1, 1], agent_brain=humanBrain, name="human", key_action_map=key_action,
                            is_traversable=True, img_name="human.png", visualize_when_busy=True,
                            customizable_properties=['score', 'nr_victims'],
                            score=0, nr_victims=0, sense_capability=sense_capability)
    # , sense_capability=sense_capability

    return builder


def create_builder_task1(rnd):
    tick = 0.05
    # Create our builder
    goal = LimitedTimeGoal(max_nr_ticks)
    builder = WorldBuilder(shape=[30, 30], tick_duration=tick, run_matrx_api=True, run_matrx_visualizer=True,
                           verbose=False, visualization_bg_clr=visualization_color, visualization_bg_img="", simulation_goal=goal)

    current_exp_folder = datetime.now().strftime("task1_at_time_%Hh-%Mm-%Ss_date_%dd-%mm-%Yy")
    if rnd == 0:
        logger_save_folder = os.path.join("task1_log_results_rnd0", current_exp_folder)
        builder.add_logger(ActionLogger, save_path=logger_save_folder, file_name_prefix="actions_")
        builder.add_logger(MessageLogger, save_path=logger_save_folder, file_name_prefix="messages_")
    else:
        logger_save_folder = os.path.join("task1_log_results_rnd1", current_exp_folder)
        builder.add_logger(ActionLogger, save_path=logger_save_folder, file_name_prefix="actions_")
        builder.add_logger(MessageLogger, save_path=logger_save_folder, file_name_prefix="messages_")

    # Add the walls surrounding the maze
    builder.add_room(top_left_location=[0, 0], width=30, height=30, name="Borders")
    wall_color = '#8a8a8a'
    room_color = '#98a7ab'

    entry_loc = [[9, 3], [11, 6], [17, 5], [25, 1],
                 [7, 10], [13, 7], [19, 6], [22, 11],
                 [4, 13], [8, 14], [17, 12], [21, 15],
                 [5, 20], [8, 19], [14, 19], [27, 21],
                 [6, 24], [9, 27]]

    for i in entry_loc:
        builder.add_object(location=i, name='Entry', callable_class=Entry,
                           visualize_opacity=0)
    # visualize_colour='#8a8a8a',

    # door location list, also used as a subset of obstacle location
    builder.add_object(location=[1, 1], name='road', img_name='road.png', is_traversable=True, is_movable=False)

    # build room A1
    builder.add_room(top_left_location=(3, 1), width=6, height=4, name='area A1', door_locations=[(8, 3)],
                     doors_open=True, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     door_visualization_opacity=0.5, wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "A1.svg"})
    builder.add_object(location=[8, 3], name="Tree1", callable_class=Obstacle, img_name="tree.png",
                       type="tree")

    # victim in area A1
    builder.add_object(location=[5, 2], name="InjuredManA1_1", callable_class=Victim, img_name="injured_victim.png",
                       time_to_rescue=5, type='injured', gender='him')
    builder.add_object(location=[7, 3], name="InjuredManA1_2", callable_class=Victim, img_name="injured_victim.png",
                       time_to_rescue=5, type='injured', gender='her')

    # build room A2
    builder.add_room(top_left_location=(10, 2), width=4, height=4, name='area A2', door_locations=[(11, 5)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "A2.svg"})
    builder.add_object(location=[11, 5], name="SmallRock1", callable_class=Obstacle, img_name="rock1.png",
                       type="small")

    # victim in area A2
    builder.add_object(location=[12, 4], name="HealthyMan1", callable_class=Victim, img_name="healthy_victim.png",
                       time_to_rescue=5, type='healthy', gender='him')


    # build room A3
    builder.add_room(top_left_location=(16, 1), width=4, height=4, name='area A3', door_locations=[(17, 4)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "A3.svg"})
    builder.add_object(location=[17, 4], name="LargeRock1", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim in area A3
    builder.add_object(location=[18, 3], name="InjuredMan2", callable_class=Victim, img_name="injured_victim.png",
                       time_to_rescue=5, type='injured', gender='her')


    # build room A4
    builder.add_room(top_left_location=(21, 2), width=6, height=4, name='area A4', door_locations=[(25, 2)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "A4.svg"})
    builder.add_object(location=[25, 2], name="SmallRock2", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim in area A4
    builder.add_object(location=[22, 4], name="CriticalMan1", callable_class=Victim, img_name="critical_victim.png",
                       time_to_rescue=5, type='critical', gender='him')
    # fence around A4
    builder.add_object(location=[28, 1], name="fence", img_name="fence.png", is_movable=False, is_traversable=False)
    builder.add_object(location=[28, 2], name="pine", img_name="pine.png", is_movable=False, is_traversable=False)


    # build room B1
    builder.add_room(top_left_location=(1, 7), width=6, height=6, name='area B1', door_locations=[(6, 10)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "B1.svg"})
    builder.add_object(location=[6, 10], name="LargeRock2", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim in area B1
    builder.add_object(location=[3, 8], name="CriticalMan2", callable_class=Victim, img_name="critical_victim.png",
                       time_to_rescue=5, type='critical', gender='him')
    builder.add_object(location=[2, 11], name="InjuredMan3", callable_class=Victim, img_name="injured_victim.png",
                       time_to_rescue=5, type='injured', gender='her')
    builder.add_object(location=[5, 9], name="HealthyManB1_1", callable_class=Victim, img_name="healthy_victim.png",
                       time_to_rescue=5, type='healthy', gender='her')

    # pine around B1
    builder.add_object(location=[1, 5], name="pine", img_name="pine.png", is_movable=False, is_traversable=False)
    builder.add_object(location=[1, 6], name="pine", img_name="pine.png", is_movable=False, is_traversable=False)


    # build room B2
    builder.add_room(top_left_location=(9, 8), width=6, height=4, name='area B2', door_locations=[(13, 8)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "B2.svg"})
    builder.add_object(location=[13, 8], name="Tree2", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim in area B2
    builder.add_object(location=[11, 10], name="InjuredMan4", callable_class=Victim, img_name="injured_victim.png",
                       time_to_rescue=5, type='injured', gender='him')
    builder.add_object(location=[10, 9], name="HealthyManB2_1", callable_class=Victim, img_name="healthy_victim.png",
                       time_to_rescue=5, type='healthy', gender='her')

    # bush around B2
    builder.add_object(location=[9, 7], name="bush", img_name="bush.png", is_movable=False, is_traversable=False)


    # build room B3
    builder.add_room(top_left_location=(16, 7), width=6, height=4, name='area B3', door_locations=[(19, 7)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "B3.svg"})
    builder.add_object(location=[19, 7], name="Tree3", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim in area B3
    builder.add_object(location=[18, 9], name="HealthyManB3_1", callable_class=Victim, img_name="healthy_victim.png",
                       time_to_rescue=5, type='healthy', gender='him')
    builder.add_object(location=[20, 8], name="InjuredManB3_1", callable_class=Victim, img_name="injured_victim.png",
                       time_to_rescue=5, type='injured', gender='her')


    # fence and pine around B3
    # builder.add_object(location=[18, 11], name="bush", img_name="bush.png", is_movable=False, is_traversable=False)
    builder.add_object(location=[19, 11], name="pine", img_name="pine.png", is_movable=False, is_traversable=False)
    builder.add_object(location=[20, 11], name="fence", img_name="fence.png", is_movable=False, is_traversable=False)



    # build room B4
    builder.add_room(top_left_location=(23, 7), width=6, height=6, name='area B4', door_locations=[(23, 11)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "B4.svg"})
    builder.add_object(location=[23, 11], name="SmallRock4", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim in area B4
    builder.add_object(location=[25, 8], name="InjuredMan5", callable_class=Victim, img_name="injured_victim.png",
                       time_to_rescue=5, type='injured', gender='him')
    builder.add_object(location=[26, 11], name="HealthyMan3", callable_class=Victim, img_name="healthy_victim.png",
                       time_to_rescue=5, type='healthy', gender='her')


    # build room C1
    builder.add_room(top_left_location=(2, 14), width=6, height=4, name='area C1', door_locations=[(4, 14)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "C1.svg"})
    builder.add_object(location=[4, 14], name="SmallRock5", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim in area C1
    builder.add_object(location=[3, 16], name="HealthyMan4", callable_class=Victim, img_name="healthy_victim.png",
                       time_to_rescue=5, type='healthy', gender='him')


    # build room C2
    builder.add_room(top_left_location=(9, 13), width=4, height=6, name='area C2', door_locations=[(9, 14)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "C2.svg"})
    builder.add_object(location=[9, 14], name="LargeRock2", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim in area C2
    builder.add_object(location=[11, 17], name="CriticalMan3", callable_class=Victim, img_name="critical_victim.png",
                       time_to_rescue=5, type='critical', gender='her')



    # build room C3
    builder.add_room(top_left_location=(14, 13), width=6, height=4, name='area C3', door_locations=[(17, 13)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "C3.svg"})
    builder.add_object(location=[17, 13], name="Tree4", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim in area C3
    builder.add_object(location=[16, 15], name="InjuredMan6", callable_class=Victim, img_name="injured_victim.png",
                       time_to_rescue=5, type='injured', gender='him')


    # build room C4
    builder.add_room(top_left_location=(22, 14), width=6, height=4, name='area C4', door_locations=[(22, 15)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "C4.svg"})
    builder.add_object(location=[22, 15], name="LargeRock3", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim in area C4
    builder.add_object(location=[25, 15], name="InjuredManC4_1", callable_class=Victim, img_name="injured_victim.png",
                       time_to_rescue=5, type='injured', gender='him')
    builder.add_object(location=[23, 16], name="InjuredManC4_2", callable_class=Victim, img_name="injured_victim.png",
                       time_to_rescue=5, type='injured', gender='her')


    # build room D1
    builder.add_room(top_left_location=(1, 19), width=4, height=4, name='area D1', door_locations=[(4, 20)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "D1.svg"})
    builder.add_object(location=[4, 20], name="SmallRock5", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim in area D1
    builder.add_object(location=[2, 20], name="HealthyMan4", callable_class=Victim, img_name="healthy_victim.png",
                       time_to_rescue=5, type='healthy', gender='him')



    # build room D2
    builder.add_room(top_left_location=(7, 20), width=6, height=4, name='area D2', door_locations=[(8, 20)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "D2.svg"})
    builder.add_object(location=[8, 20], name="LargeRock5", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim in area D2
    builder.add_object(location=[10, 22], name="InjuredManD2_1", callable_class=Victim, img_name="injured_victim.png",
                       time_to_rescue=5, type='injured', gender='her')
    builder.add_object(location=[9, 21], name="InjuredManD2_2", callable_class=Victim, img_name="injured_victim.png",
                       time_to_rescue=5, type='injured', gender='him')



    # build room D3
    builder.add_room(top_left_location=(15, 18), width=6, height=4, name='area D3', door_locations=[(15, 19)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "D3.svg"})
    builder.add_object(location=[15, 19], name="Tree5", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim in area D3
    builder.add_object(location=[19, 20], name="CriticalMan4", callable_class=Victim, img_name="critical_victim.png",
                       time_to_rescue=5, type='critical', gender='him')


    # build room D4
    builder.add_room(top_left_location=(23, 19), width=4, height=4, name='area D4', door_locations=[(26, 21)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "D4.svg"})
    builder.add_object(location=[26, 21], name="LargeRock6", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim in area D4
    builder.add_object(location=[24, 21], name="InjuredMan9", callable_class=Victim, img_name="injured_victim.png",
                       time_to_rescue=5, type='injured', gender='her')



    # build room E1
    builder.add_room(top_left_location=(2, 25), width=6, height=4, name='area E1', door_locations=[(6, 25)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "E1.svg"})
    builder.add_object(location=[6, 25], name="Tree6", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim in area E1
    builder.add_object(location=[3, 27], name="CriticalMan5", callable_class=Victim, img_name="critical_victim.png",
                       time_to_rescue=5, type='critical', gender='him')


    # build room E2
    builder.add_room(top_left_location=(10, 25), width=4, height=4, name='area E2', door_locations=[(10, 27)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "E2.svg"})
    builder.add_object(location=[10, 27], name="SmallRock6", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim in area E2
    builder.add_object(location=[12, 26], name="HealthyMan5", callable_class=Victim, img_name="healthy_victim.png",
                       time_to_rescue=5, type='healthy', gender='him')



    # build safe zone
    builder.add_room(top_left_location=(16, 24), width=11, height=5, name='safe_zone', door_locations=[(18, 24)],
                     doors_open=True, wall_visualize_colour="#00a000",
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled_2.png"})

    # fence and bush around safe zone
    builder.add_object(location=[15, 27], name="fence", img_name="fence.png", is_movable=False, is_traversable=False)
    builder.add_object(location=[15, 28], name="bush", img_name="bush.png", is_movable=False, is_traversable=False)

    add_agents_first(builder, rnd)

    return builder


def create_builder_task2(rnd):
    tick = 0.05
    # Create our builder
    goal = LimitedTimeGoal(max_nr_ticks)
    builder = WorldBuilder(shape=[30, 30], tick_duration=tick, run_matrx_api=True, run_matrx_visualizer=True,
                           verbose=False, visualization_bg_clr=visualization_color, visualization_bg_img="", simulation_goal=goal)

    current_exp_folder = datetime.now().strftime("task2_at_time_%Hh-%Mm-%Ss_date_%dd-%mm-%Yy")
    if rnd == 0:
        logger_save_folder = os.path.join("task2_log_results_rnd0", current_exp_folder)
        builder.add_logger(ActionLogger, save_path=logger_save_folder, file_name_prefix="actions_")
        builder.add_logger(MessageLogger, save_path=logger_save_folder, file_name_prefix="messages_")
    elif rnd == 1:
        logger_save_folder = os.path.join("task2_log_results_rnd1", current_exp_folder)
        builder.add_logger(ActionLogger, save_path=logger_save_folder, file_name_prefix="actions_")
        builder.add_logger(MessageLogger, save_path=logger_save_folder, file_name_prefix="messages_")

    # Add the walls surrounding the maze
    builder.add_room(top_left_location=[0, 0], width=30, height=30, name="Borders")
    wall_color = '#8a8a8a'
    room_color = '#98a7ab'

    entry_loc = [[1, 4], [7, 3], [21, 3], [22, 2],
                 [7, 8], [8, 7], [16, 7], [25, 6],
                 [4, 12], [13, 15], [18, 12], [27, 13],
                 [5, 22], [9, 19], [13, 19], [24, 17],
                 [8, 26], [11, 24]]
    for i in entry_loc:
        builder.add_object(location=i, name='Entry', callable_class=Entry, visualize_colour=None, visualize_opacity=0.0)

    # area A1
    builder.add_room(top_left_location=(2, 2), width=4, height=4, name='area A1', door_locations=[(2, 4)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "A1.svg"})
    builder.add_object(location=[2, 4], name="TreeA1", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim in area A1
    builder.add_object(location=[4, 3], name="InjuredMan1", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='her')

    # area A2
    builder.add_room(top_left_location=(8, 1), width=6, height=4, name='area A2', door_locations=[(8, 3)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "A2.svg"})
    builder.add_object(location=[8, 3], name="SmallRock1", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim in area A2
    builder.add_object(location=[12, 2], name="CriticalMan1", callable_class=Victim, img_name="critical_victim.png",
                       type='critical', gender='him')

    # add fence around A2
    builder.add_object(location=[7, 1], name="fence", img_name="fence.png", is_movable=False, is_traversable=False)


    # area A3
    builder.add_room(top_left_location=(15, 1), width=6, height=6, name='area A3', door_locations=[(20, 3)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "A3.svg"})
    builder.add_object(location=[20, 3], name="LargeRock3", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim A3
    builder.add_object(location=[16, 2], name="InjuredMan2", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='her')
    builder.add_object(location=[19, 5], name="InjuredMan3", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='him')
    builder.add_object(location=[16, 5], name="InjuredManA3", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='him')


    # area A4
    builder.add_room(top_left_location=(23, 1), width=6, height=4, name='area A4', door_locations=[(23, 2)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "A4.svg"})
    builder.add_object(location=[23, 2], name="Tree2", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim A4
    builder.add_object(location=[25, 2], name="HealthyMan1", callable_class=Victim, img_name="healthy_victim.png",
                       type='healthy', gender='her')
    builder.add_object(location=[27, 3], name="InjuredManA4", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='him')

    # add pine around A4
    builder.add_object(location=[28, 5], name="bush", img_name="bush.png", is_movable=False, is_traversable=False)

    # area B1
    builder.add_room(top_left_location=(1, 7), width=6, height=4, name='area B1', door_locations=[(6, 8)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "B1.svg"})
    builder.add_object(location=[6, 8], name="SmallRockA3", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim B1
    builder.add_object(location=[4, 9], name="HealthyManB1", callable_class=Victim, img_name="healthy_victim.png",
                       type='healthy', gender='her')
    builder.add_object(location=[2, 8], name="InjuredMan4", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='him')


    # add pine & fence around B1
    builder.add_object(location=[1, 11], name="pine", img_name="pine.png", is_movable=False, is_traversable=False)
    builder.add_object(location=[1, 12], name="fence", img_name="fence.png", is_movable=False, is_traversable=False)

    # area B2
    builder.add_room(top_left_location=(9, 6), width=4, height=4, name='area B2', door_locations=[(9, 7)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "B2.svg"})
    builder.add_object(location=[9, 7], name="Tree3", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim B2
    builder.add_object(location=[11, 7], name="HealthyMan2", callable_class=Victim, img_name="healthy_victim.png",
                       type='healthy', gender='her')

    # area B3
    builder.add_room(top_left_location=(14, 8), width=6, height=4, name='area B3', door_locations=[(16, 8)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "B3.svg"})
    builder.add_object(location=[16, 8], name="SmallRock3", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim B3
    builder.add_object(location=[15, 10], name="HealthyMan3", callable_class=Victim, img_name="healthy_victim.png",
                       type='healthy', gender='him')

    # area B4
    builder.add_room(top_left_location=(22, 7), width=6, height=4, name='area B4', door_locations=[(25, 7)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "B4.svg"})
    builder.add_object(location=[25, 7], name="LargeRock2", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim B4
    builder.add_object(location=[23, 9], name="CriticalMan2", callable_class=Victim, img_name="critical_victim.png",
                       type='critical', gender='her')

    # area C1
    builder.add_room(top_left_location=(1, 13), width=6, height=6, name='area C1', door_locations=[(4, 13)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "C1.svg"})
    builder.add_object(location=[4, 13], name="LargeRock3", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim C1
    builder.add_object(location=[2, 14], name="CriticalMan3", callable_class=Victim, img_name="critical_victim.png",
                       type='critical', gender='her')
    builder.add_object(location=[5, 17], name="InjuredMan5", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='him')

    # area C2
    builder.add_room(top_left_location=(9, 12), width=4, height=6, name='area C2', door_locations=[(12, 15)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "C2.svg"})
    builder.add_object(location=[12, 15], name="SmallRock4", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim C2
    builder.add_object(location=[10, 13], name="HealthyMan4", callable_class=Victim, img_name="healthy_victim.png",
                       type='healthy', gender='her')

    # area C3
    builder.add_room(top_left_location=(15, 13), width=6, height=4, name='area C3', door_locations=[(18, 13)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "C3.svg"})
    builder.add_object(location=[18, 13], name="Tree4", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim C3
    builder.add_object(location=[16, 14], name="InjuredMan6", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='him')
    builder.add_object(location=[19, 15], name="InjuredManC3", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='her')

    # area C4
    builder.add_room(top_left_location=(23, 12), width=4, height=4, name='area C4', door_locations=[(26, 13)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "C4.svg"})
    builder.add_object(location=[26, 13], name="LargeRock4", callable_class=Obstacle, img_name="tall.png",
                       type="large")

    # victim C4
    builder.add_object(location=[24, 13], name="InjuredMan7", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='her')

    # area D1
    builder.add_room(top_left_location=(1, 20), width=4, height=4, name='area D1', door_locations=[(4, 22)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "D1.svg"})
    builder.add_object(location=[4, 22], name="Tree5", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim D1
    builder.add_object(location=[2, 21], name="InjuredMan8", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='him')

    # area D2
    builder.add_room(top_left_location=(7, 20), width=6, height=4, name='area D2', door_locations=[(9, 20)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "D2.svg"})
    builder.add_object(location=[9, 20], name="LargeRock5", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim D2
    builder.add_object(location=[11, 22], name="InjuredMan9", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='her')
    builder.add_object(location=[8, 21], name="InjuredManD2", callable_class=Victim, img_name="injured_victim.png",
                       type='injured', gender='him')


    # area D3
    builder.add_room(top_left_location=(14, 18), width=6, height=4, name='area D3', door_locations=[(14, 19)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "D3.svg"})
    builder.add_object(location=[14, 19], name="Tree6", callable_class=Obstacle, img_name="tree.png",
                       type="tree")
    # victim D3
    builder.add_object(location=[18, 20], name="CriticalMan4", callable_class=Victim, img_name="critical_victim.png",
                       type='critical', gender='him')
    builder.add_object(location=[16, 19], name="HealthyMan6", callable_class=Victim, img_name="healthy_victim.png",
                       type='healthy', gender='her')


    # area D4
    builder.add_room(top_left_location=(22, 18), width=6, height=4, name='area D4', door_locations=[(24, 18)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "D4.svg"})
    builder.add_object(location=[24, 18], name="SmallRockA3", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim D4
    builder.add_object(location=[25, 20], name="HealthyMan5", callable_class=Victim, img_name="healthy_victim.png",
                       type='healthy', gender='her')

    # area E1
    builder.add_room(top_left_location=(2, 25), width=6, height=4, name='area E1', door_locations=[(7, 26)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "E1.svg"})
    builder.add_object(location=[7, 26], name="LargeRock6", callable_class=Obstacle, img_name="tall.png",
                       type="large")
    # victim E1
    builder.add_object(location=[3, 26], name="CriticalMan5", callable_class=Victim, img_name="critical_victim.png",
                       type='critical', gender='him')

    # area E2
    builder.add_room(top_left_location=(10, 25), width=4, height=4, name='area E2', door_locations=[(11, 25)],
                     doors_open=True, door_visualization_opacity=0.5, wall_visualize_colour=wall_color,
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled.png"},
                     door_custom_properties={"img_name": "E2.svg"})
    builder.add_object(location=[11, 25], name="SmallRockA3", callable_class=Obstacle, img_name="rock1.png",
                       type="small")
    # victim E2
    builder.add_object(location=[12, 26], name="HealthyMan6", callable_class=Victim, img_name="healthy_victim.png",
                       type='healthy', gender='her')


    # build safe zone
    builder.add_room(top_left_location=(16, 24), width=11, height=5, name='safe_zone', door_locations=[(18, 24)],
                     doors_open=True, wall_visualize_colour="#00a000",
                     with_area_tiles=True, area_visualize_colour=room_color, area_visualize_opacity=0.5,
                     wall_custom_properties={"img_name": "Untitled_2.png"})

    # add pine around safe zone
    builder.add_object(location=[14, 28], name="pine", img_name="pine.png", is_movable=False, is_traversable=False)
    builder.add_object(location=[15, 28], name="pine", img_name="pine.png", is_movable=False, is_traversable=False)

    add_agents_second(builder, rnd)
    return builder

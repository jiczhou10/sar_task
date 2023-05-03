from matrx.actions.object_actions import GrabObject, RemoveObject, DropObject
from matrx.utils import get_distance

from matrx.objects import EnvObject
from matrx.actions.action import Action, ActionResult
from matrx.agents.agent_utils.state import State
from matrx.objects.standard_objects import AreaTile
import collections


# agent score
score = 0
safe_tiles = [(17, 25), (18, 25), (19, 25), (20, 25), (21, 25), (22, 25), (23, 25), (24, 25), (25, 25),
              (17, 26), (18, 26), (19, 26), (20, 26), (21, 26), (22, 26), (23, 26), (24, 26), (25, 26),
              (17, 27), (18, 27), (19, 27), (20, 27), (21, 27), (22, 27), (23, 27), (24, 27), (25, 27)]


class RemoveTogether(RemoveObject):
    # every obstacle is possible to remove together if two agents are close enough
    # large obstacle has to be removed together

    def __init__(self):
        super().__init__()

    def mutate(self, grid_world, agent_id, world_state, **kwargs):
        # get object id to remove together
        obj = world_state[kwargs['object_id']]

        # if agent_id == 'agent':
        other_agent_id = 'human'
        # change human's image to carry together image
        other_agent = grid_world.registered_agents['human']
        agent = grid_world.registered_agents['agent']
        # other_agent.change_property("location", agent.properties['location'])

        # agent.change_property("img_name", "remove_tog.png")
        other_agent.change_property("visualize_opacity", 0)

        return super().mutate(grid_world, agent_id, world_state, **kwargs)

    def is_possible(self, grid_world, agent_id, world_state, **kwargs):
        # checks if an object can be removed
        return super().is_possible(grid_world, agent_id, **kwargs)


class RemoveAgents(Action):
    def __init__(self, duration_in_ticks=0):
        super().__init__(duration_in_ticks)

    def mutate(self, grid_world, agent_id, world_state, **kwargs):
        # reg_ag = world_state[{"name": "agent"}]
        reg_ag = grid_world.registered_agents['agent']
        # human_ag = world_state[{"name": "human"}]
        human_ag = grid_world.registered_agents['human']
        reg_ag.change_property("visualize_opacity", 0)
        human_ag.change_property("visualize_opacity", 0)

        return self.is_possible(grid_world, agent_id, world_state, **kwargs)

    def is_possible(self, grid_world, agent_id, world_state, **kwargs):
        return RemoveAgentsResult(RemoveAgentsResult.RESULT_SUCCESS, True)


class RemoveAgentsResult(ActionResult):
    SUCCESS = "REMOVE AGENTS SUCCEED."

    def __init__(self, result, succeeded):
        super().__init__(result, succeeded)

class RemoveAlone(RemoveObject):
    def __init__(self):
        super().__init__()

    def is_possible(self, grid_world, agent_id, **kwargs):
        return super().is_possible(grid_world, agent_id, **kwargs)

    def mutate(self, grid_world, agent_id, world_state, **kwargs):
        '''
        if the obstacle is at door location, then change the opacity of the door
        '''
        return super().mutate(grid_world, agent_id, world_state, **kwargs)


class CarryAlone(GrabObject):
    def __init__(self):
        super().__init__()

    def is_possible(self, grid_world, agent_id, world_state, **kwargs):
        return super().is_possible(grid_world, agent_id, **kwargs)


class CarryTogether(GrabObject):
    def __init__(self):
        super().__init__()

    def is_possible(self, grid_world, agent_id, world_state, **kwargs):
        return super().is_possible(grid_world, agent_id, world_state, **kwargs)

    def mutate(self, grid_world, agent_id, world_state, **kwargs):
        if agent_id == 'agent':
            other_agent_id = 'human'

        # if we want to change objects, we need to change the grid_world object
        # other_agent = grid_world.registered_agents[other_agent_id]
        # agent = grid_world.registered_agents[agent_id]

        # make the other agent invisible
        # if agent_id == 'agent':
            # change human's image to carry together image
            # agent.change_property("img_name", "carry_together.png")
            # agent.change_property("visualize_opacity", 0)

        # pickup the object
        return super().mutate(grid_world, agent_id, world_state, **kwargs)


# agent idle action
class Idle(Action):
    def __init__(self, duration_in_ticks=1):
        super().__init__(duration_in_ticks)

    def is_possible(self, grid_world, agent_id, **kwargs):
        # Maybe do a check to see if the empty location is really and still empty?
        return IdleResult(IdleResult.RESULT_SUCCESS, True)


class IdleResult(ActionResult):
    """ Result when falling succeeded. """
    RESULT_SUCCESS = 'Idling action successful'

    """ Result when the emptied space was not actually empty. """
    RESULT_FAILED = 'Failed to idle'

    def __init__(self, result, succeeded):
        super().__init__(result, succeeded)


class DropAlone(DropObject):
    """ Drops a carried object.
    """

    def __init__(self, duration_in_ticks=0):
        super().__init__(duration_in_ticks)

    def mutate(self, grid_world, agent_id, world_state, **kwargs):
        global score
        obj_id = kwargs['object_id']
        ag = grid_world.registered_agents['agent']
        other_ag = grid_world.registered_agents['human']
        env_obj = [obj for obj in ag.is_carrying if obj.obj_id == obj_id][0]
        obj_type = env_obj.properties['type']
        print('obj_type ', obj_type)
        score = other_ag.custom_properties['score']
        nr_victims = other_ag.custom_properties['nr_victims']

        if ag.properties['location'] in safe_tiles:
            print('in safe tiles')
            nr_victims += 1
            other_ag.change_property('nr_victims', nr_victims)
            if obj_type == 'healthy':
                score += 1
                other_ag.change_property('score', score)
            elif obj_type == 'injured':
                score += 3
                other_ag.change_property('score', score)

        print('score: ', other_ag.properties['score'])

        # drop the actual object like we would do with a normal drop action
        return super().mutate(grid_world, agent_id, world_state, **kwargs)





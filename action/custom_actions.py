import numpy as np
import collections

from matrx.actions.action import Action, ActionResult
from matrx.actions.object_actions import GrabObject, DropObject
from action.rmv_object import RemoveObject
from matrx.utils import get_distance
from matrx.agents.agent_utils.state import State
from matrx.objects.agent_body import AgentBody

from matrx.objects.standard_objects import AreaTile

human_score = 0
nr_victims = 0

safe_tiles = [(17, 25), (18, 25), (19, 25), (20, 25), (21, 25), (22, 25), (23, 25), (24, 25), (25, 25),
              (17, 26), (18, 26), (19, 26), (20, 26), (21, 26), (22, 26), (23, 26), (24, 26), (25, 26),
              (17, 27), (18, 27), (19, 27), (20, 27), (21, 27), (22, 27), (23, 27), (24, 27), (25, 27)]


class CarryObject(GrabObject):
    def __init__(self, duration_in_ticks=1):
        super().__init__(duration_in_ticks)

    def is_possible(self, grid_world, agent_id, world_state, **kwargs):
        grab_range = np.inf if 'grab_range' not in kwargs else kwargs['grab_range']
        if agent_id == 'human':
            reg_ag = world_state[{"name": "human"}]
        # obj_to_grab = world_state[kwargs['object_id']]

        if reg_ag['is_carrying']:
            print('human is carrying something else. ')
            return CarryResult(CarryResult.CARRYING_ANOTHER, False)

        # do the checks for grabbing a regular object as well
        return super().is_possible(grid_world, agent_id, world_state, **kwargs)

    def mutate(self, grid_world, agent_id, world_state, **kwargs):
        if agent_id == 'agent':
            other_agent_id = 'human'

        # other_agent_id = world_state[{"name": "agent"}]['obj_id']
        agent = grid_world.registered_agents[agent_id]
        # other_agent = grid_world.registered_agents[other_agent_id]
        victim = world_state[kwargs['object_id']]
        victim_type = victim['type']
        print('agent', agent)

        # change human's image to carry together image
        if victim_type == 'healthy':
            agent.change_property("img_name", 'carry_healthy.png')
        elif victim_type == 'injured':
            agent.change_property("img_name", "carry_injured.png")
            # other_agent.change_property("visualize_opacity", 0)
        elif victim_type == 'critical':
            agent.change_property("img_name", "carry_critical.png")
            # other_agent.change_property("visualize_opacity", 0)

        # pickup the object
        return super().mutate(grid_world, agent_id, world_state, **kwargs)


class CarryObjectTogether(GrabObject):
    def __init__(self, duration_in_ticks=1):
        super().__init__(duration_in_ticks)

    def is_possible(self, grid_world, agent_id, world_state, **kwargs):
        grab_range = np.inf if 'grab_range' not in kwargs else kwargs['grab_range']
        if agent_id == 'human':
            reg_ag = world_state[{"name": 'human'}]
            other_agent = world_state[{"name": "agent"}]
        obj_to_grab = world_state[kwargs['object_id']]
        print('carry together ', obj_to_grab)
        if reg_ag['is_carrying']:
            print('human is carrying something else. ')
            return CarryTogetherResult(CarryTogetherResult.CARRYING_ANOTHER, False)

        # check if the collaborating agent is close enough to the object as well 
        if get_distance(other_agent['location'], obj_to_grab['location']) > grab_range:
            return CarryTogetherResult(CarryTogetherResult.OTHER_TOO_FAR, False)

        # do the checks for grabbing a regular object as well
        return super().is_possible(grid_world, agent_id, world_state, **kwargs)

    def mutate(self, grid_world, agent_id, world_state, **kwargs):
        if agent_id == 'agent':
            other_agent_id = 'human'
        elif agent_id == 'human':
            other_agent_id = 'agent'
        # other_agent_id = world_state[{"name": "agent"}]['obj_id']
        agent = grid_world.registered_agents[agent_id]
        other_agent = grid_world.registered_agents[other_agent_id]
        victim = world_state[kwargs['object_id']]
        victim_type = victim['type']

        # change human's image to carry together image
        if victim_type == 'injured':
            agent.change_property("img_name", "carry_together_yellow.png")
            other_agent.change_property("visualize_opacity", 0)
        elif victim_type == 'critical':
            agent.change_property("img_name", "carry_together_red.png")
            other_agent.change_property("visualize_opacity", 0)

        # pickup the object 
        return super().mutate(grid_world, agent_id, world_state, **kwargs)


class DropObjectAlone(DropObject):
    """ Drops a carried object.
    """

    def __init__(self, duration_in_ticks=0):
        super().__init__(duration_in_ticks)

    def mutate(self, grid_world, agent_id, world_state, **kwargs):
        global human_score
        global nr_victims
        obj_id = kwargs['object_id']
        reg_ag = grid_world.registered_agents['human']
        env_obj = [obj for obj in reg_ag.is_carrying if obj.obj_id == obj_id][0]
        obj_type = env_obj.properties['type']

        human_score = reg_ag.custom_properties['score']
        nr_victims = reg_ag.custom_properties['nr_victims']

        if reg_ag.properties['location'] in safe_tiles:
            nr_victims += 1
            reg_ag.change_property('nr_victims', nr_victims)
            if obj_type == 'healthy':
                human_score += 1
                reg_ag.change_property('score', human_score)
            elif obj_type == 'injured':
                human_score += 3
                reg_ag.change_property('score', human_score)
            elif obj_type == 'critical':
                human_score += 6
                reg_ag.change_property('score', human_score)
        print('score: ', reg_ag.properties['score'])
        print('nr_victims', reg_ag.properties['nr_victims'])

        # change the agent image back to default
        reg_ag.change_property("img_name", "human.png")

        # drop the actual object like we would do with a normal drop action
        return super().mutate(grid_world, agent_id, world_state, **kwargs)


class DropObjectTogether(DropObject):
    def __init__(self, duration_in_ticks=0):
        super().__init__(duration_in_ticks)

    def mutate(self, grid_world, agent_id, world_state, **kwargs):
        global human_score
        global nr_victims
        other_agent_id = world_state[{"name": "agent"}]['obj_id']
        obj_id = kwargs['object_id']
        reg_ag = grid_world.registered_agents[agent_id]
        env_obj = [obj for obj in reg_ag.is_carrying if obj.obj_id == obj_id][0]
        print('env_obj', env_obj)
        obj_type = env_obj.properties['type']
        print('obj_type ', obj_type)

        human_score = reg_ag.custom_properties['score']
        nr_victims = reg_ag.custom_properties['nr_victims']

        # if we want to change objects, we need to change the grid_world object 
        other_agent = grid_world.registered_agents[other_agent_id]

        if reg_ag.properties['location'] in safe_tiles:
            nr_victims += 1
            reg_ag.change_property('nr_victims', nr_victims)
            if obj_type == 'healthy':
                human_score += 1
                reg_ag.change_property('score', human_score)
            elif obj_type == 'injured':
                human_score += 3
                reg_ag.change_property('score', human_score)
            elif obj_type == 'critical':
                human_score += 6
                reg_ag.change_property('score', human_score)
        print('score: ', reg_ag.properties['score'])
        print('nr_victims', reg_ag.properties['nr_victims'])

        # teleport the other agent to our current position 
        other_agent.change_property("location", reg_ag.properties['location'])

        # make the other agent visible again 
        other_agent.change_property("visualize_opacity", 1)

        # change the agent image back to default 
        reg_ag.change_property("img_name", "human.png")

        # drop the actual object like we would do with a normal drop action
        return super().mutate(grid_world, agent_id, world_state, **kwargs)


class RemoveObjectTogether(RemoveObject):
    def __init__(self):
        super().__init__()

    def is_possible(self, grid_world, agent_id, world_state, **kwargs):
        grab_range = 1
        if agent_id == 'human':
            other_agent = world_state[{"name": "agent"}]
        obj_to_grab = world_state[kwargs['object_id']]
        print('remove together ', obj_to_grab)
        print('other agent loc', other_agent['location'])

        # check if the collaborating agent is close enough to the object as well
        if get_distance(other_agent['location'], obj_to_grab['location']) > grab_range:
            print('too far too far')
            return CarryTogetherResult(CarryTogetherResult.OTHER_TOO_FAR, False)

        # do the checks for grabbing a regular object as well
        return super().is_possible(grid_world, agent_id, world_state, **kwargs)


    def mutate(self, grid_world, agent_id, world_state, **kwargs):
        if agent_id == 'agent':
            other_agent_id = world_state[{"name": "human"}]['obj_id']
            # print('other agent id ', other_agent_id)
            # other agent id  {'isAgent': True, 'img_name': 'human.png', 'key_action_map':
            # {'w': 'MoveNorth', 'd': 'MoveEast', 's': 'MoveSouth', 'a': 'MoveWest', 'ArrowUp': 'MoveNorth',
            # 'ArrowRight': 'MoveEast', 'ArrowDown': 'MoveSouth', 'ArrowLeft': 'MoveWest', 'g': 'GrabObject',
            # 'r': 'RemoveAlone', 'q': 'DropObject', 'c': 'CarryObjectTogether', 'x': 'DropObjectTogether',
            # 't': 'RemoveObjectTogether'}, 'team': 'human_team', 'name': 'human', 'obj_id': 'human',
            # 'location': (7, 3), 'is_movable': None,
            # 'action_set': ['OpenDoorAction', 'MoveSouthWest', 'MoveSouthEast', 'MoveNorthEast', 'Idle', 'CarryAlone', 'Move', 'RemoveTogether', 'DropObjectTogether', 'MoveWest', 'GrabObject', 'CloseDoorAction', 'MoveSouth', 'RemoveObject', 'DropObject', 'MoveEast', 'MoveNorth', 'RemoveAlone', 'RemoveObjectTogether', 'CarryObjectTogether', 'MoveNorthWest'],
            # 'carried_by': [], 'is_human_agent': True, 'is_traversable': True,
            # 'class_inheritance': ['HumanCustomBrain', 'HumanAgentBrain', 'AgentBrain', 'object'],
            # 'is_blocked_by_action': False, 'is_carrying': [],
            # 'sense_capability': "{<class 'matrx.objects.agent_body.AgentBody'>: inf, <class 'env_generator.Victim.Victim'>: 1,
            # <class 'env_generator.Obstacle.Obstacle'>: 1, '*': inf}", 'visualization': {'size': 1.0, 'shape': 1,
            # 'colour': '#92f441', 'depth': 100, 'opacity': 1.0, 'show_busy': False, 'visualize_from_center': True},
            # 'current_action': 'MoveNorth', 'current_action_args': {}, 'current_action_duration': 0,
            # 'current_action_started_at_tick': 256}

        elif agent_id == 'human':
            other_agent_id = world_state[{"name": "agent"}]['obj_id']

        # if we want to change objects, we need to change the grid_world object
        other_agent = grid_world.registered_agents[other_agent_id]
        agent = grid_world.registered_agents[agent_id]

        # pickup the object
        return super().mutate(grid_world, agent_id, world_state, **kwargs)


class RemoveObject(Action):
    """ Removes an object from the world."""

    def __init__(self, duration_in_ticks=0):
        super().__init__(duration_in_ticks)

    def mutate(self, grid_world, agent_id, world_state, **kwargs):
        assert 'object_id' in kwargs.keys()  # assert if object_id is given.
        object_id = kwargs['object_id']  # assign
        remove_range = 1  # default remove range
        if 'remove_range' in kwargs.keys():  # if remove range is present
            assert isinstance(kwargs['remove_range'], int)  # should be of integer
            assert kwargs['remove_range'] >= 0  # should be equal or larger than 0
            remove_range = kwargs['remove_range']  # assign

        # get the current agent (exists, otherwise the is_possible failed)
        agent_avatar = grid_world.registered_agents[agent_id]
        agent_loc = agent_avatar.location  # current location

        # Get all objects in the remove_range
        objects_in_range = grid_world.get_objects_in_range(agent_loc, object_type="*", sense_range=remove_range)

        # You can't remove yourself
        objects_in_range.pop(agent_id)

        for obj in objects_in_range:  # loop through all objects in range
            if obj == object_id:  # if object is in that list
                success = grid_world.remove_from_grid(object_id)  # remove it, success is whether GridWorld succeeded
                if success:  # if we succeeded in removal return the appropriate ActionResult
                    return RemoveObjectResult(RemoveObjectResult.OBJECT_REMOVED.replace('object_id'.upper(),
                                                                                        str(object_id)), True)
                else:  # else we return a failure due to the GridWorld removal failed
                    return RemoveObjectResult(RemoveObjectResult.REMOVAL_FAILED.replace('object_id'.upper(),
                                                                                        str(object_id)), False)

        # If the object was not in range, or no objects were in range we return that the object id was not in range
        return RemoveObjectResult(RemoveObjectResult.OBJECT_ID_NOT_WITHIN_RANGE
                                  .replace('remove_range'.upper(), str(remove_range))
                                  .replace('object_id'.upper(), str(object_id)), False)

    def is_possible(self, grid_world, agent_id, **kwargs):
        """ Checks if an object can be removed.

        Parameters
        ----------
        Returns
        -------
        RemoveObjectResult
            The :class:`matrx.actions.action.ActionResult` depicting the
            action's expected success or failure and reason for that result.

            See :class:`matrx.actions.object_actions.RemoveObjectResult` for
            the results it can contain.

        """
        agent_avatar = grid_world.get_env_object(agent_id, obj_type=AgentBody)  # get ourselves
        assert agent_avatar is not None  # check if we actually exist
        agent_loc = agent_avatar.location  # get our location

        # need an object id to remove an object
        if 'object_id' not in kwargs:
            return RemoveObjectResult(RemoveObjectResult.REMOVAL_FAILED.replace('object_id'.upper(),
                                                                                str(None)), False)
        remove_range = 1  # default remove range
        if 'remove_range' in kwargs.keys():  # if remove range is present
            assert isinstance(kwargs['remove_range'], int)  # should be of integer
            assert kwargs['remove_range'] >= 0  # should be equal or larger than 0
            remove_range = kwargs['remove_range']  # assign

        # get all objects within remove range
        objects_in_range = grid_world.get_objects_in_range(agent_loc, object_type="*", sense_range=remove_range)

        # You can't remove yourself
        objects_in_range.pop(agent_avatar.obj_id)

        if len(objects_in_range) == 0:  # if there are no objects in remove range besides ourselves, we return fail
            return RemoveObjectResult(RemoveObjectResult.NO_OBJECTS_IN_RANGE.replace('remove_range'.upper(),
                                                                                     str(remove_range)), False)
        # check if the object is actually within removal range
        object_id = kwargs['object_id']
        if object_id not in objects_in_range:
            return RemoveObjectResult(RemoveObjectResult.REMOVAL_FAILED.replace('object_id'.upper(),
                                                                                str(object_id)), False)

        # otherwise some instance of RemoveObject is possible, although we do not know yet IF the intended removal is
        # possible.
        return RemoveObjectResult(RemoveObjectResult.ACTION_SUCCEEDED, True)


class RemoveObjectResult(ActionResult):
    """ActionResult for a RemoveObjectAction

    The results uniquely for RemoveObjectAction are (as class constants):

    * OBJECT_REMOVED: If the object was successfully removed.
    * REMOVAL_FAILED: If the object could not be removed by the
      :class:`matrx.grid_world.GridWorld`.
    * OBJECT_ID_NOT_WITHIN_RANGE: If the object is not within specified range.
    * NO_OBJECTS_IN_RANGE: If no objects are within range.

    Parameters
    ----------
    result: str
        A string representing the reason for the (expected) success or fail of
        a :class:`matrx.actions.object_actions.RemoveObjectAction`.
    succeeded: bool
        A boolean representing the (expected) success or fail of a
        :class:`matrx.actions.object_actions.RemoveObjectAction`.

    See Also
    --------
    :class:`matrx.actions.object_actions.RemoveObjectAction`

    """

    """ Result when the specified object is successfully removed. """
    OBJECT_REMOVED = "The object with id `OBJECT_ID` is removed."

    """ Result when no objects were within the specified range. """
    NO_OBJECTS_IN_RANGE = "No objects were in `REMOVE_RANGE`."

    """ Result when the specified object is not within the specified range. """
    OBJECT_ID_NOT_WITHIN_RANGE = "The object with id `OBJECT_ID` is not within the range of `REMOVE_RANGE`."

    """ Result when the world could not remove the object for some reason. """
    REMOVAL_FAILED = "The object with id `OBJECT_ID` failed to be removed by the environment for some reason."

    def __init__(self, result, succeeded):
        super().__init__(result, succeeded)


class CarryTogetherResult(ActionResult):
    PICKUP_SUCCESS = 'Successfully grabbed object together'
    OTHER_TOO_FAR = 'Failed to grab object. The other agent is too far from the object'
    CARRYING_ANOTHER = 'Failed to grab object together. The agent is carrying another object'

class CarryResult(ActionResult):
    PICKUP_SUCCESS = 'Successfully grabbed object'
    OTHER_TOO_FAR = 'Failed to grab object. The other agent is too far from the object'
    CARRYING_ANOTHER = 'Failed to grab object. The agent is carrying another object'

class RemoveTogetherResult(ActionResult):
    PICKUP_SUCCESS = 'Successfully removed object together'
    OTHER_TOO_FAR = 'Failed to grab object. The other agent is too far from the object'


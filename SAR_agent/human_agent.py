from matrx.agents import HumanAgentBrain
from action.custom_actions import CarryObjectTogether, DropObjectTogether, RemoveObjectTogether, RemoveObject, CarryObject, DropObjectAlone
# from matrx.actions import GrabObject, DropObject
from matrx.messages import Message
from matrx.utils import get_distance
# from matrx.agents.agent_utils.state import State


class CustomHumanAgent(HumanAgentBrain):
    """ Creates a Human Agent which is an agent that can be controlled by a human.
    For more extensive documentation on the functions below, see:
    http://docs.matrx-software.com/en/master/sections/_generated_autodoc/matrx.agents.agent_types.human_agent.HumanAgentBrain.html
    """

    def __init__(self, memorize_for_ticks=None, max_carry_objects=1,
                 grab_range=1, drop_range=1):
        super().__init__(memorize_for_ticks=memorize_for_ticks)
        self._max_carry_objects = max_carry_objects
        self.__grab_range = grab_range
        self.__remove_range = 1
        self.flag_carry_together = False
        self.carry_obj_id = None

    def filter_observations(self, state):
        """ Filters the world state before deciding on an action. """

        return state

    def decide_on_action(self, state, user_input):
        """ Contains the decision logic of the agent. """
        action = None
        action_kwargs = {"action_duration": 1}

        # if no keys were pressed, do nothing
        if user_input is None or user_input == []:
            return None, {}

        # take the latest pressed key and fetch the action
        pressed_keys = user_input[-1]
        action = self.key_action_map[pressed_keys]

        # if self.send_message()

        if action == RemoveObject.__name__:
            obj = state.get_closest_with_property(props={'class_inheritance': 'Obstacle'})
            obj1 = state.get_closest_with_property(props={'class_inheritance': 'Obstacle1'})
            loc = state.get_agents_with_property({'name': 'human'})[0].get('location')
            print('human wants to remove an object')
            if obj and get_distance(obj[0]['location'], loc) <= 1:
                # human can remove a small rock with 100 * tick_duration seconds
                if obj[0]['type'] == 'small':
                    action_kwargs['action_duration'] = 50
                    action_kwargs['object_id'] = obj[0]['obj_id']
                # human can remove a tree with 500 * tick_duration seconds
                elif obj[0]['type'] == 'tree':
                    action_kwargs['action_duration'] = 300
                    action_kwargs['object_id'] = obj[0]['obj_id']
                # human cannot remove a large rock alone
                elif obj[0]['type'] == 'large':
                    action = None
                    action_kwargs = {}
            elif obj1 and get_distance(obj1[0]['location'], loc) <= 1:
                # human can remove a small rock with 100 * tick_duration seconds
                if obj1[0]['type'] == 'small':
                    action_kwargs['action_duration'] = 50
                    action_kwargs['object_id'] = obj[0]['obj_id']
                # human can remove a tree with 500 * tick_duration seconds
                elif obj1[0]['type'] == 'tree':
                    action_kwargs['action_duration'] = 300
                    action_kwargs['object_id'] = obj[0]['obj_id']
                # human cannot remove a large rock alone
                elif obj1[0]['type'] == 'large':
                    action = None
                    action_kwargs = {}
            else:
                action = None
                action_kwargs = {}

        elif action == RemoveObjectTogether.__name__:
            action_kwargs['remove_range'] = self.__remove_range
            obj = state.get_closest_with_property(props={"class_inheritance": "Obstacle"})
            obj1 = state.get_closest_with_property(props={"class_inheritance": "Obstacle1"})
            loc = state.get_agents_with_property({"name": "human"})[0].get('location')
            agent = state.get_agents_with_property({"name": "agent"})
            if agent:
                agent_loc = agent[0].get('location')

            if agent and get_distance(loc, agent_loc) <= 1:
                if obj and get_distance(obj[0]['location'], loc) <= 1:
                    if obj[0]['type'] == 'small':
                        action_kwargs['action_duration'] = 0
                        action_kwargs['object_id'] = obj[0]['obj_id']
                        action_kwargs['remove_range'] = self.__remove_range
                    elif obj[0]['type'] == 'tree':
                        action_kwargs['action_duration'] = 50
                        action_kwargs['object_id'] = obj[0]['obj_id']
                        action_kwargs['remove_range'] = self.__remove_range
                    elif obj[0]['type'] == 'large':
                        action_kwargs['action_duration'] = 100
                        action_kwargs['object_id'] = obj[0]['obj_id']
                        action_kwargs['remove_range'] = self.__remove_range
                    else:
                        action = None
                        action_kwargs = {}
                elif obj1 and get_distance(obj1[0]['location'], loc) <= 1:
                    if obj1[0]['type'] == 'small':
                        action_kwargs['action_duration'] = 0
                        action_kwargs['object_id'] = obj[0]['obj_id']
                        action_kwargs['remove_range'] = self.__remove_range
                    elif obj1[0]['type'] == 'tree':
                        action_kwargs['action_duration'] = 50
                        action_kwargs['object_id'] = obj[0]['obj_id']
                        action_kwargs['remove_range'] = self.__remove_range
                    elif obj1[0]['type'] == 'large':
                        action_kwargs['action_duration'] = 100
                        action_kwargs['object_id'] = obj[0]['obj_id']
                        action_kwargs['remove_range'] = self.__remove_range
                    else:
                        action = None
                        action_kwargs = {}
                else:
                    action = None
                    action_kwargs = {}
            else:
                action = None
                action_kwargs = {}

        elif action == CarryObject.__name__:
            victim = state.get_closest_with_property(props={'class_inheritance': 'Victim'})
            victim1 = state.get_closest_with_property(props={'class_inheritance': 'Victim1'})
            human = state.get_agents_with_property({"name": "human"})[0]
            if victim and not human['is_carrying']:
                victim_loc = victim[0]['location']
                victim_type = victim[0]['type']
                self.carry_obj_id = victim[0]['obj_id']
            elif victim1 and not human['is_carrying']:
                victim_loc = victim1[0]['location']
                victim_type = victim1[0]['type']
                self.carry_obj_id = victim1[0]['obj_id']
            else:
                return None, {}
            agent_loc = state.get_agents_with_property({'name': 'human'})[0].get('location')
            if get_distance(victim_loc, agent_loc) <= self.__grab_range:
                # for healthy/injured victims, human can grab with different ticks
                # for critically injured victims, human need to collaborate with agent
                if victim_type == 'healthy':
                    # takes 5 seconds to grab a healthy victim
                    action_kwargs['action_duration'] = 25
                    action_kwargs['object_id'] = victim[0]['obj_id']
                    action_kwargs['grab_range'] = self.__grab_range
                    action_kwargs['max_objects'] = self._max_carry_objects
                elif victim_type == 'injured':
                    # takes 10 seconds to grab an injured victim
                    action_kwargs['action_duration'] = 70
                    action_kwargs['object_id'] = victim[0]['obj_id']
                    action_kwargs['grab_range'] = self.__grab_range
                    action_kwargs['max_objects'] = self._max_carry_objects
                elif victim_type == 'critical':
                    action = None
                    action_kwargs = {}
            else:
                return None, {}

        # if the user chose a grab action, choose an object within grab_range
        elif action == CarryObjectTogether.__name__:
            # Set grab range
            action_kwargs['grab_range'] = self.__grab_range
            # Set max amount of objects
            action_kwargs['max_objects'] = self._max_carry_objects

            # grab the closest victim
            obj = state.get_closest_with_property(props={"class_inheritance": "Victim"})
            obj1 = state.get_closest_with_property(props={"class_inheritance": "Victim1"})
            human = state.get_agents_with_property({"name": "human"})[0]
            if state.get_agents_with_property({"name": "agent"}):
                agent = state.get_agents_with_property({"name": "agent"})[0]
                if obj and not human['is_carrying'] and not agent['is_carrying']:
                    obj_id = obj[0]['obj_id']
                    action_kwargs['object_id'] = obj_id
                    self.carry_obj_id = obj_id
                    self.flag_carry_together = True
                elif obj1 and not human['is_carrying'] and not agent['is_carrying']:
                    obj_id = obj1[0]['obj_id']
                    action_kwargs['object_id'] = obj_id
                    self.carry_obj_id = obj_id
                    self.flag_carry_together = True
                else:
                    action = None
                    action_kwargs = {}
            else:
                return None, {}

        elif action == DropObjectAlone.__name__:
            safe_tiles = self.get_safe_zone_tiles(state)
            human_location = state.get_agents_with_property({"name": "human"})[0].get('location')
            if human_location in safe_tiles:
                action = DropObjectAlone.__name__
                action_kwargs['object_id'] = self.carry_obj_id
                if self.flag_carry_together:
                    action = DropObjectTogether.__name__
                    action_kwargs['object_id'] = self.carry_obj_id
                    self.flag_carry_together = False
            else:
                action = None
                action_kwargs = {}
        return action, action_kwargs

    def _set_messages(self, messages=None):
        # make sure we save the entire message and not only the content
        for mssg in messages:
            received_message = mssg
            self.received_messages.append(received_message)

    def get_safe_zone_tiles(self, state):
        tiles = []
        room_values = state.get_room('safe_zone')
        if room_values:
            for r in room_values:
                if 'AreaTile' in r['class_inheritance']:
                    tiles.append(r['location'])
        return tiles

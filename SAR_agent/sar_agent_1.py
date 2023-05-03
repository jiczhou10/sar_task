import enum

from random import randint
from matrx.agents.agent_brain import AgentBrain
from matrx.actions import RemoveObject, GrabObject
from matrx.messages.message import Message
from matrx.utils import get_distance
from matrx.agents.agent_utils.state import State
from matrx.agents.agent_utils.state_tracker import StateTracker
from matrx.agents.agent_utils.navigator import Navigator
from action.agent_actions import DropAlone, RemoveAgents

'''
Agent1 only explain the basic information of current situation
For how explanation, including current location, how to execute next move,
For why explanation, including current location, current state, 
the reason of why agent want to collaborate
'''

'''
After starting the task, agent is at the top left corner, and human is at bottom right,
agent starts to search from the nearest room，
once agent finds an obstacle, it first evaluates the type of the obstacle,
if it requires collaboration, then ask for human's help,
if human accepts the request, then wait for human,
if human rejects to help, agent record this obstacle's location, and starts to search for the next room, 

after finding a victim, agent recognize severity of injury is soft interdependence,
human has ability to carry healthy and medium injured victim, but not severely injured victim,
agent has ability to carry all types of victim, but severely injured victim need to rescue first,
'''


class Phase(enum.Enum):
    INTRO = 0,
    GET_CLOSEST_STUCK_ROOM = 1,
    GO_TO_LOC = 2,
    FIND_OBSTACLE = 3,
    SEARCH_FOR_VICTIM = 4,
    WAIT_FOR_HUMAN_REMOVE_TOG = 5,
    REMOVE_OBSTACLE = 6,
    REMOVE_TOGETHER = 7,
    WAIT_FOR_HUMAN = 8,
    GRAB_VICTIM = 9
    CARRY_VICTIM = 10,
    CARRY_TOGETHER = 11,
    PLAN_PATH_IN_ROOM = 12,
    PLAN_PATH_TO_SAFE = 13,
    DROP_VICTIM = 14,
    GO_TO_HUMAN = 15,
    HELP_HUMAN = 16,
    WAIT_FOR_SEARCH_ROOM = 17,
    WAIT_FOR_ANSWER = 18,
    PLAN_RESCUE = 19,
    WAIT_FOR_SAFE_ZONE = 20,
    BACK_TO_ROOM = 21,
    WAIT_RESCUE = 22,
    WAIT_REMOVE = 23


class SarAgent1(AgentBrain):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.phase = Phase.INTRO
        self.maxTicks = 9600
        self.wayPoint = [] if 'waypoints' not in kwargs else kwargs['waypoints']
        self.sendMessages = []
        # obstacle location stored as dictionary, key: obstacle location; val: obstacle type
        self.foundObstacle = {}
        # victim location stored as dictionary, key: victim id; val: victim location
        self.foundVictims = {}
        self.foundEntry = {}
        # victims location that have been rescued by agent
        self.rescuedVictims = {}
        # obstacles location that have been removed by the agent
        self.removedObstacle = {}
        self.detectRange = 2
        self.grabRange = 1
        self.dropRange = 1
        self.searchedRooms = set()
        self.lastObstacleLoc = ()
        self.lastVictimLoc = ()
        self.humanLoc = ()
        self.goalLoc = ()
        self.agentPrevLoc = ()
        self.prevPhase = None
        self.next_goal = None
        self.roomName = None
        self.searchRoute = None
        self.searedRooms = set()
        self.received_messages_ticks = []
        self.lastWaitTick = None
        self.newly_found_victim = {}
        self.carry_obj_id = None
        self.msg_id = 'SarBot'
        self.lastEntry = None
        self.preWaitPhase = None
        self.next_closest_flag = False

    def initialize(self):
        self._state_tracker = StateTracker(agent_id=self.agent_id)
        self._navigator = Navigator(agent_id=self.agent_id,
                                    action_set=self.action_set, algorithm=Navigator.A_STAR_ALGORITHM)
        self._navigator.add_waypoints(self.wayPoint, is_circular=False)

    def _send_message(self, message):
        if message.content not in self.sendMessages:
            if not self.sendMessages:
                self.send_message(message)
                self.sendMessages.append(message.content)
            if self.sendMessages[-1] != message.content:
                self.send_message(message)
                self.sendMessages.append(message.content)
        # if message.content not in self.sendMessages:
        #     self.send_message(message)
        #     self.sendMessages.append(message.content)

    def __send_message(self, message):
        if not self.sendMessages:
            self.send_message(message)
            self.sendMessages.append(message.content)
        if self.sendMessages[-1] != message.content:
            self.send_message(message)
            self.sendMessages.append(message.content)

    def _set_messages(self, messages=None):
        # make sure we save the entire message and not only the content
        for mssg in messages:
            received_message = mssg
            # state = State
            tick = self._state['World']['nr_ticks']
            self.received_messages.append(received_message)
            self.received_messages_ticks.append(tick)

    def decide_on_action(self, state: State):
        # hhh()

        while True:
            # check whether human asks for help
            if self.maxTicks - self._state['World']['nr_ticks'] <= 3600:
                self._send_message(Message('3_left.svg', self.msg_id))
            if self.maxTicks - self._state['World']['nr_ticks'] <= 2400:
                self._send_message(Message('2_left.svg', self.msg_id))
            if self.maxTicks - self._state['World']['nr_ticks'] <= 1200:
                self._send_message(Message('1_left.svg', self.msg_id))
            if self.maxTicks - self._state['World']['nr_ticks'] <= 20:
                nr_victims = state.get_agents_with_property({"name": "human"})[0].get('nr_victims')
                self._send_message(
                    (Message(f'Congratulations! We successfully rescued {nr_victims} victims! Now the task '
                             'has ended, please ask the instructor for the next step. ', self.msg_id)))

            if self.received_messages and self.received_messages[-1].content == 'Help':
                agent = state.get_agents_with_property(props={"name": "agent"})[0]
                is_busy = agent['is_busy']
                # self.__send_message(Message(f'{is_busy}', self.msg_id))

                if self.phase != Phase.GO_TO_HUMAN and self.phase != Phase.HELP_HUMAN \
                        and self.phase != Phase.GO_TO_LOC \
                        and self.phase != Phase.INTRO and not agent['is_carrying']:
                    # record agent's previous phase and location
                    # self.received_messages = []
                    # if not self.received_messages:
                    #     self.__send_message(Message('Last message does not respond. ', self.msg_id))
                    # else:
                    self.received_messages = []
                    self.prevPhase = self.phase
                    self._send_message(Message('I am coming to your location.', self.msg_id))
                    self.agentPrevLoc = state.get_agents_with_property({"name": "agent"})[0].get('location')
                    # go to human's location
                    self.phase = Phase.GO_TO_HUMAN
                elif self.phase == Phase.GO_TO_HUMAN:
                    self.__send_message(Message('I am coming to your location.', self.msg_id))
                elif self.phase == Phase.REMOVE_OBSTACLE:
                    self.__send_message(Message('I am removing an obstacle.', self.msg_id))
                elif self.phase == Phase.CARRY_VICTIM:
                    self.__send_message(Message('I am carrying victim.', self.msg_id))
                elif self.phase == Phase.PLAN_PATH_TO_SAFE:
                    self.__send_message(Message('I am carrying victim.', self.msg_id))
                elif agent['is_carrying']:
                    self.__send_message(Message('I am carrying victim.', self.msg_id))

            if Phase.INTRO == self.phase:
                mssg = Message(content=f'Hello, my name is SaR bot, together '
                                       f'we are going to do a search and rescue task in this 2D world. '
                                       f'The goal of this task is to get the highest score. '
                                       f'Now you are at the top left corner of this world, and I am '
                                       f'at the bottom right corner. We have 8 minutes to do this task. '
                                       f'Once the task is started, it cannot be paused. '
                                       f'If you understand everything I said, and are ready to start the task, '
                                       f'you can click the Ready button.'
                               , from_id=self.msg_id)
                self._send_message(mssg)
                if self.received_messages and self.received_messages[-1].content == 'Ready':
                    self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                    self.received_messages = []
                else:
                    return None, {}

            if self.phase == Phase.GET_CLOSEST_STUCK_ROOM:
                # if there is still obstacles stuck the room entry
                if self.next_closest_flag:
                    agent_location = self.state[self.agent_id]['location']
                    obstacles = state.get_with_property(props={'class_inheritance': 'Obstacle'})
                    next_closest = None
                    min_distance = 20
                    for o in obstacles:
                        distance = get_distance(o['location'], agent_location)
                        if distance > 1 and distance < min_distance:
                            print(f'{o}')
                            min_distance = distance
                            next_closest = o

                    if next_closest:
                        entries = state.get_of_type('Entry')
                        self.foundObstacle[next_closest['location']] = next_closest
                        self.lastObstacleLoc = next_closest['location']
                        for entry in entries:
                            entry_location = entry['location']
                            # print(f'entry location, {entry_location}, next closest {next_closest} ')
                            if get_distance(entry_location, next_closest['location']) <= 1:
                                self.wayPoint.append(entry_location)
                                self.lastObstacleLoc = next_closest['location']
                                self.lastEntry = entry_location
                                print(f'last found with next closest {self.lastObstacleLoc}, {self.lastEntry}, {self.foundObstacle}')
                                self.next_closest_flag = False
                                self.phase = Phase.GO_TO_LOC

                    else:
                        return None, {}


                elif state.get_closest_with_property(props={'class_inheritance': 'Obstacle'}):
                    # find closest obstacle
                    obstacles = state.get_closest_with_property(props={'class_inheritance': 'Obstacle'})
                    if obstacles:
                        print('obstacles', obstacles)
                        obstacle_location = obstacles[0]['location']

                        if obstacle_location:
                            # store this obstacle's location and type into dict
                            self.foundObstacle[obstacle_location] = obstacles[0]
                            entry = state.get_closest_with_property(props={'class_inheritance': 'Entry'})
                            entry_location = entry[0]['location']
                            # print('entry location ', entry_location)

                            if get_distance(entry_location, obstacle_location) <= 1:
                                self.wayPoint.append(entry_location)
                                self.lastObstacleLoc = obstacle_location
                                self.lastEntry = entry_location
                                self.phase = Phase.GO_TO_LOC
                            else:
                                entries = state.get_of_type('Entry')
                                for entry in entries:
                                    entry_location = entry['location']
                                    print('entry location, ', entry_location)
                                    if get_distance(entry_location, obstacle_location) <= 1:
                                        self.wayPoint.append(entry_location)
                                        self.lastObstacleLoc = obstacle_location
                                        self.lastEntry = entry_location
                                        self.phase = Phase.GO_TO_LOC
                        else:
                            return None, {}
                    else:
                        return None, {}
                # none of the rooms is blocked by obstacle, then search for closest room
                else:
                    self.phase = Phase.PLAN_PATH_IN_ROOM
                return None, {}

            # go to the last waypoint
            if self.phase == Phase.GO_TO_LOC:
                print('waypoints: ', self.wayPoint)
                if self.agentPrevLoc:
                    print('self.agentPrevLoc is not None')
                    self._navigator.reset_full()
                    self._navigator.add_waypoint(self.agentPrevLoc)
                    self._state_tracker.update(self.state)
                    action = self._navigator.get_move_action(self._state_tracker)
                    if action != None:
                        return action, {'action_duration': 5}
                    else:
                        self.phase = Phase.FIND_OBSTACLE
                        self.agentPrevLoc = None
                        return None, {}
                else:
                    self._navigator.reset_full()
                    self._navigator.add_waypoint(self.wayPoint[-1])
                    self._state_tracker.update(self.state)
                    action = self._navigator.get_move_action(self._state_tracker)
                    agent_location = self.state[self.agent_id]['location']
                    # if agent_location == self.wayPoint[-1]:
                    #     # after arrival, remove the last waypoint
                    #     self.wayPoint.remove(agent_location)
                    if action != None:
                        return action, {'action_duration': 5}
                    else:
                        self.wayPoint.remove(agent_location)
                        self.phase = Phase.FIND_OBSTACLE
                        return None, {}

            if self.phase == Phase.FIND_OBSTACLE:
                # print('into find obstacle phase')
                # print('last found entry: ', self.lastEntry)
                agent_location = state.get_agents_with_property({"name": "agent"})[0].get('location')
                if agent_location == self.lastEntry:
                    type = self.foundObstacle[self.lastObstacleLoc]['type']
                    obs = self.foundObstacle[self.lastObstacleLoc]
                    img = str(self.foundObstacle[self.lastObstacleLoc]['img_name'])
                    doors = state.get_with_property(props={'class_inheritance': 'Door'})
                    for door in doors:
                        if self.lastObstacleLoc == door['location']:
                            door_img = door['img_name']
                    closest_obstacle = state.get_closest_with_property(props={"class_inheritance": "Obstacle"})
                    if closest_obstacle and get_distance(closest_obstacle[0]['location'], agent_location) <= 1:
                        agent_opacity = state.get_agents_with_property(props={"name": "agent"})[0]

                        if type == 'small' and agent_opacity != 0:
                            mssg = Message(f'I found {img} at {door_img}. '
                                           f'I suggest to remove it myself. ',
                                           self.msg_id)
                            self._send_message(mssg)
                            # self.received_messages = []
                            human = state.get_agents_with_property(props={"name": "human"})[0]
                            agent = state.get_agents_with_property(props={"name": "agent"})[0]
                            if self.received_messages and self.received_messages[-1].content == 'Ok':
                                mssg = Message(f'I will remove it alone.', self.msg_id)
                                self.__send_message(mssg)
                                self.phase = Phase.REMOVE_OBSTACLE
                                self.received_messages = []
                                return None, {}
                            elif self.received_messages and self.received_messages[-1].content == 'No':
                                self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                                self.next_closest_flag = True
                                self.received_messages = []
                                return None, {}
                            elif human['current_action'] and human['current_action'] == 'RemoveObject':
                                if human['location'] == agent['location']:
                                    print('human is blocked by remove action')
                                    self.next_closest_flag = True
                                    self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                                    self.received_messages = []
                                    return None, {}
                            elif self.received_messages:
                                self.received_messages = []
                                return None, {}
                            return None, {}

                        elif type == 'large' and agent_opacity != 0:
                            distance = get_distance(
                                state.get_agents_with_property({"name": "human"})[0].get('location'),
                                state.get_agents_with_property({"name": "agent"})[0].get('location'))
                            # for soft interdependence, if the distance between two agents are too far, then
                            # collaboration is slower

                            if distance > 10:
                                mssg = Message(f'I found {img} at {door_img}. '
                                               f'I suggest to remove it myself. ', self.msg_id)
                                self._send_message(mssg)
                                human = state.get_agents_with_property(props={"name":"human"})[0]
                                agent = state.get_agents_with_property(props={"name":"agent"})[0]
                                if self.received_messages and self.received_messages[-1].content == 'Ok':
                                    mssg = Message(f'I will remove it alone.', self.msg_id)
                                    self.__send_message(mssg)
                                    self.phase = Phase.REMOVE_OBSTACLE
                                    self.received_messages = []
                                    return None, {}
                                elif self.received_messages and self.received_messages[-1].content == 'No':
                                    mssg = Message(f'Copy that.', self.msg_id)
                                    self.__send_message(mssg)
                                    self.next_closest_flag = True
                                    self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                                    self.received_messages = []
                                    return None, {}
                                elif self.received_messages:
                                    self.received_messages = []
                                    return None, {}
                                else:
                                    return None, {}

                            # for soft interdependence, agent sends message to request collaborate
                            else:
                                mssg = Message(f'I found {img} at {door_img}. '
                                               f'I suggest you come here and we remove it together instead of alone. '
                                               , self.msg_id)
                                self._send_message(mssg)
                                if self.received_messages and self.received_messages[-1].content == 'Ok':
                                    mssg = Message(f'I will wait for you.', self.msg_id)
                                    self.__send_message(mssg)
                                    self.next_goal = 'remove'
                                    self.phase = Phase.WAIT_FOR_HUMAN
                                    self.received_messages = []
                                    return None, {}
                                elif self.received_messages and self.received_messages[-1].content == 'No':
                                    mssg = Message(f'I will remove it alone.', self.msg_id)
                                    self.__send_message(mssg)
                                    self.phase = Phase.REMOVE_OBSTACLE
                                    self.received_messages = []
                                    return None, {}
                                elif self.received_messages:
                                    self.received_messages = []
                                    return None, {}
                                else:
                                    return None, {}

                        # agent cannot remove tree, which requires hard interdependence,
                        # for hard interdependence, it requires two agents to collaborate to remove large obstacle
                        elif type == 'tree' and agent_opacity != 0:
                            mssg = Message(f'I found {img} at {door_img}, '
                                           f'I suggest you come here and we remove it together. ',
                                           self.msg_id)
                            self._send_message(mssg)
                            # if human agrees to collaborate, wait for human
                            if self.received_messages and self.received_messages[-1].content == 'Ok':
                                mssg = Message(f'I will wait for you.', self.msg_id)
                                self.__send_message(mssg)
                                self.next_goal = 'remove'
                                self.phase = Phase.WAIT_FOR_HUMAN
                                self.received_messages = []
                                return None, {}
                            # if human disagrees to collaborate, then search for the next closest stuck room
                            elif self.received_messages and self.received_messages[-1].content == 'No':
                                mssg = Message(f'Copy that.', self.msg_id)
                                self.__send_message(mssg)
                                self.next_closest_flag = True
                                self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                                self.received_messages = []
                                return None, {}
                            elif self.received_messages:
                                self.received_messages = []
                                return None, {}
                            else:
                                # self.phase = Phase.WAIT_FOR_ANSWER
                                # self.preWaitPhase = Phase.FIND_OBSTACLE
                                # self.lastWaitTick = self._state['World']['nr_ticks']
                                # self.received_messages = []
                                return None, {}
                            # return None, {}
                        else:
                            return None, {}
                    else:
                        self.next_closest_flag = True
                        self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                        self.received_messages = []
                        return None, {}
                else:
                    print('waypoint before appending ', self.wayPoint)
                    self.wayPoint.append(self.lastEntry)
                    print('waypoint after appending ', self.wayPoint)
                    self._navigator.reset_full()
                    self._navigator.add_waypoint(self.lastEntry)
                    self._state_tracker.update(state)
                    action = self._navigator.get_move_action(self._state_tracker)
                    if action != None:
                        return action, {'action_duration': 7}
                    else:
                        self.wayPoint.remove(self.lastEntry)
                        return None, {}

            if self.phase == Phase.WAIT_FOR_HUMAN:
                '''
                wait for human come to agent's location,
                after human arrives, agent and human remove/carry victim together'''
                # self._send_message(Message('waiting for human', self.msg_id))
                human_location = state.get_agents_with_property({"name": "human"})[0].get('location')
                agent_location = state.get_agents_with_property({"name": "agent"})[0].get('location')
                distance = get_distance(human_location, agent_location)
                # after human is close enough
                if distance <= self.detectRange:
                    if self.next_goal == 'remove':
                        # self._send_message(Message('into grab range, remove ', self.msg_id))
                        self.next_goal = None
                        self.phase = Phase.REMOVE_TOGETHER
                        return None, {}
                    if self.next_goal == 'carry':
                        # self._send_message(Message('into grab range, carry ', self.msg_id))
                        self.next_goal = None
                        self.phase = Phase.CARRY_TOGETHER
                        return None, {}
                else:
                    return None, {}
                return None, {}

            if self.phase == Phase.REMOVE_OBSTACLE:
                '''
                agent removes the obstacle alone
                '''
                mssg = Message(f'into remove obstacle phase', self.msg_id)
                # self._send_message(mssg)
                type = self.foundObstacle[self.lastObstacleLoc]['type']
                door = state.get_closest_with_property(props={'class_inheritance': 'Door'})[0]
                if door['room_name'] not in self.searedRooms:
                    self.roomName = door['room_name']
                    if type == 'small':
                        duration = 50
                    elif type == 'large':
                        duration = 300
                    elif type == 'tree':
                        return None, {}
                    action = RemoveObject.__name__
                    closest_obstacle = self.foundObstacle[self.lastObstacleLoc]
                    agent_location = state.get_agents_with_property(props={"name": "agent"})[0].get('location')
                    if action != None:
                        self.phase = Phase.PLAN_PATH_IN_ROOM
                        agent = state.get_agents_with_property(props={"name": "agent"})[0]
                        agent['is_busy'] = True
                        return action, {'object_id': self.foundObstacle[self.lastObstacleLoc]['obj_id'],
                                        'action_duration': duration}
                    else:
                        # self._send_message(Message(content=f'action None', from_id=self.msg_id))
                        return None, {}

            if self.phase == Phase.PLAN_PATH_IN_ROOM:
                '''
                search the whole room for victim
                '''
                agent = state.get_agents_with_property(props={"name": "agent"})[0]
                agent['is_busy'] = False
                room_tiles = []
                current_room = self.roomName
                room_values = state.get_room(current_room)
                # get all tiles in this room
                if current_room:
                    for r in room_values:
                        if 'AreaTile' in r['class_inheritance']:
                            room_tiles.append(r['location'])

                closest_obstacle = state.get_closest_with_property(props={'class_inheritance': 'Obstacle'})
                agent_location = state.get_agents_with_property(props={"name": "agent"})[0].get('location')
                if not closest_obstacle or get_distance(closest_obstacle[0]['location'], agent_location) > 1:
                    # get room search route
                    self.searchRoute = room_tiles
                    self.phase = Phase.SEARCH_FOR_VICTIM
                return None, {}

            if self.phase == Phase.SEARCH_FOR_VICTIM:
                # self._send_message(Message(str('in search for victim phase'), self.msg_id))
                self.searedRooms.add(self.roomName)
                # if did not finish search route, keep navigating to next waypoint
                if self.searchRoute:
                    self._navigator.reset_full()
                    self._navigator.add_waypoint(self.searchRoute[0])
                    self._state_tracker.update(state)
                    action = self._navigator.get_move_action(self._state_tracker)
                    action_kwargs = {}
                    if action != None:
                        for info in state.values():
                            # if there is a victim within sense range, add to found victim dict
                            if 'class_inheritance' in info and 'Victim' in info['class_inheritance']:
                                victim_location = info['location']
                                if victim_location not in self.foundVictims.keys():
                                    self.foundVictims[victim_location] = info
                                    self.newly_found_victim[victim_location] = info
                                # else:
                                #     return None, {}
                            # else:
                            #     return None, {}
                        return action, action_kwargs
                    else:
                        self.searchRoute.remove(self.searchRoute[0])
                        return None, {}
                else:
                    # refresh search route
                    self.searchRoute = []
                    # if there is newly found victims, plan rescue
                    if self.newly_found_victim.keys():
                        self.phase = Phase.PLAN_RESCUE
                        return None, {}
                    # if there is not newly found victims, get the closest stuck room
                    else:
                        self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                        return None, {}

            if self.phase == Phase.PLAN_RESCUE:
                # self._send_message(Message('in plan rescue phase', self.msg_id))
                action_kwargs = {}
                if self.foundVictims.keys():
                    self.victim_location = list(self.foundVictims.keys())[0]
                    print('current victim ', self.victim_location)

                    rooms = state.get_with_property(props={'class_inheritance': 'AreaTile'})
                    room_name = None
                    # get the room name of current victim
                    for room in rooms:
                        if self.victim_location == room['location']:
                            room_name = room['room_name']

                    room_img = state.get_room_doors(room_name)[0]['img_name']
                    self.currentvictim = self.victim_location

                    victim_type = self.foundVictims[self.victim_location]['type']
                    victim_img = self.foundVictims[self.victim_location]['img_name']
                    print('victim img and type: ', victim_img, victim_type)
                    # need victim_id to check whether it is still there
                    self.goalLoc = self.victim_location
                    human_location = state.get_agents_with_property({"name": "human"})[0]['location']
                    agent_location = state.get_agents_with_property({"name": "agent"})[0]['location']
                    gender = self.foundVictims[self.victim_location]['gender']

                    if victim_type == 'healthy':
                        # go to victim's location
                        self._navigator.reset_full()
                        self._navigator.add_waypoint(self.victim_location)
                        self._state_tracker.update(state)
                        action = self._navigator.get_move_action(self._state_tracker)
                        if action != None:
                            return action, {'action_duration': 5}
                        else:
                            # check whether there is victim or not
                            if state.get_closest_with_property(props={"class_inheritance": "Victim"}):
                                check_location = \
                                state.get_closest_with_property(props={"class_inheritance": "Victim"})[0]['location']
                                agent_opacity = state.get_agents_with_property(props={"name": "agent"})[0]

                                if check_location and check_location == self.victim_location and agent_opacity != 0:
                                    mssg = Message(f'I found {victim_img} in {room_img}. '
                                                   f'I suggest to rescue {gender} by myself.',
                                                   self.msg_id)
                                    self.__send_message(mssg)
                                    if self.received_messages and self.received_messages[-1].content == 'Ok':
                                        mssg = Message(f'I will rescue by myself.', self.msg_id)
                                        self.__send_message(mssg)
                                        action = GrabObject.__name__
                                        self.carry_obj_id = self.foundVictims[self.victim_location]['obj_id']
                                        print(self.foundVictims[self.victim_location]['obj_id'])
                                        action_kwargs['object_id'] = self.foundVictims[self.victim_location]['obj_id']
                                        action_kwargs['grab_range'] = self.grabRange
                                        action_kwargs['max_objects'] = 1
                                        action_kwargs['action_duration'] = 100
                                        agent = state.get_agents_with_property(props={"name": "agent"})[0]
                                        agent['is_busy'] = True
                                        self.received_messages = []
                                        self.phase = Phase.PLAN_PATH_TO_SAFE
                                        return action, action_kwargs
                                    elif self.received_messages and self.received_messages[-1].content == 'No':
                                        mssg = Message(f'Copy that.', self.msg_id)
                                        self.__send_message(mssg)
                                        self.received_messages = []
                                        self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                                        return None, {}
                                    elif self.received_messages:
                                        print('self.received message not none.')
                                        self.received_messages = []
                                        return None, {}
                                    else:
                                        return None, {}
                                else:
                                    self.foundVictims.pop(self.victim_location)
                                    self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                                    return None, {}
                            else:
                                self.foundVictims.pop(self.victim_location)
                                self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                                return None, {}

                    if victim_type == 'injured':
                        # self._send_message(Message('Found injured victim', self.msg_id))
                        self._navigator.reset_full()
                        self._navigator.add_waypoint(self.victim_location)
                        self._state_tracker.update(state)
                        action = self._navigator.get_move_action(self._state_tracker)
                        if action != None:
                            return action, {'action_duration': 5}
                        else:
                            if get_distance(human_location, agent_location) <= 6:
                                # check whether there is victim or not
                                if state.get_closest_with_property(props={"class_inheritance": "Victim"}):
                                    check_location = \
                                        state.get_closest_with_property(props={"class_inheritance": "Victim"})[0][
                                            'location']
                                    agent_opacity = state.get_agents_with_property(props={"name": "agent"})[0]
                                    human = state.get_agents_with_property({"name": "human"})[0]

                                    if check_location and check_location == self.victim_location and agent_opacity != 0:
                                        if not human['is_carrying']:
                                            mssg = Message(f'I found {victim_img} in {room_img}. '
                                                       f'I suggest you come here and we rescue {gender} together.',
                                                       self.msg_id)
                                            self.__send_message(mssg)

                                            if self.received_messages and self.received_messages[-1].content == 'Ok':
                                                mssg = Message(f'Copy that.', self.msg_id)
                                                self.__send_message(mssg)
                                                self.received_messages = []
                                                self.phase = Phase.CARRY_TOGETHER
                                            elif self.received_messages and self.received_messages[-1].content == 'No':
                                                mssg = Message(f'Copy that.', self.msg_id)
                                                self.__send_message(mssg)
                                                self.received_messages = []
                                                action = GrabObject.__name__
                                                self.carry_obj_id = self.foundVictims[self.victim_location]['obj_id']
                                                print(self.foundVictims[self.victim_location]['obj_id'])
                                                agent = state.get_agents_with_property(props={"name": "agent"})[0]
                                                agent['is_busy'] = True
                                                action_kwargs['object_id'] = self.foundVictims[self.victim_location][
                                                    'obj_id']
                                                action_kwargs['grab_range'] = self.grabRange
                                                action_kwargs['max_objects'] = 1
                                                action_kwargs['action_duration'] = 300
                                                self.phase = Phase.PLAN_PATH_TO_SAFE
                                                self.received_messages = []
                                                return action, action_kwargs
                                            else:
                                                return None, {}
                                        else:
                                            mssg = Message(f'I found {victim_img} in {room_img}. '
                                                           f'I suggest to rescue {gender} by myself.',
                                                           self.msg_id)
                                            self.__send_message(mssg)
                                            if self.received_messages and self.received_messages[-1].content == 'Ok':
                                                mssg = Message(f'Copy that.', self.msg_id)
                                                self.__send_message(mssg)
                                                action = GrabObject.__name__
                                                self.carry_obj_id = self.foundVictims[self.victim_location]['obj_id']
                                                print(self.foundVictims[self.victim_location]['obj_id'])
                                                agent = state.get_agents_with_property(props={"name": "agent"})[0]
                                                agent['is_busy'] = True
                                                action_kwargs['object_id'] = self.foundVictims[self.victim_location][
                                                    'obj_id']
                                                action_kwargs['grab_range'] = self.grabRange
                                                action_kwargs['max_objects'] = 1
                                                action_kwargs['action_duration'] = 300
                                                self.phase = Phase.PLAN_PATH_TO_SAFE
                                                self.received_messages = []
                                                return action, action_kwargs
                                            else:
                                                return None, {}
                                    else:
                                        self.foundVictims.pop(self.victim_location)
                                        self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                                        return None, {}
                                else:
                                    self.foundVictims.pop(self.victim_location)
                                    self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                                    return None, {}
                            else:
                                if state.get_closest_with_property(props={"class_inheritance": "Victim"}):
                                    check_location = \
                                        state.get_closest_with_property(props={"class_inheritance": "Victim"})[0][
                                            'location']
                                    agent_opacity = state.get_agents_with_property(props={"name": "agent"})[0]

                                    if check_location and check_location == self.victim_location and agent_opacity != 0:
                                        mssg = Message(f'I found {victim_img} in {room_img}. '
                                                       f'I suggest to rescue {gender} by myself.',
                                                       self.msg_id)
                                        self.__send_message(mssg)
                                        if self.received_messages and self.received_messages[-1].content == 'Ok':
                                            mssg = Message(f'Copy that.', self.msg_id)
                                            self.__send_message(mssg)
                                            action = GrabObject.__name__
                                            self.carry_obj_id = self.foundVictims[self.victim_location]['obj_id']
                                            print(self.foundVictims[self.victim_location]['obj_id'])
                                            agent = state.get_agents_with_property(props={"name": "agent"})[0]
                                            agent['is_busy'] = True
                                            action_kwargs['object_id'] = self.foundVictims[self.victim_location][
                                                'obj_id']
                                            action_kwargs['grab_range'] = self.grabRange
                                            action_kwargs['max_objects'] = 1
                                            action_kwargs['action_duration'] = 300
                                            self.phase = Phase.PLAN_PATH_TO_SAFE
                                            self.received_messages = []
                                            return action, action_kwargs
                                        else:
                                            return None, {}
                                    else:
                                        self.foundVictims.pop(self.victim_location)
                                        self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                                        return None, {}
                                    # return None, {}
                                else:
                                    self.foundVictims.pop(self.victim_location)
                                    self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                                    return None, {}

                    if victim_type == 'critical':
                        self._navigator.reset_full()
                        self._navigator.add_waypoint(self.victim_location)
                        self._state_tracker.update(state)
                        action = self._navigator.get_move_action(self._state_tracker)
                        if action != None:
                            return action, {'action_duration': 5}
                        else:
                            if state.get_closest_with_property(props={"class_inheritance": "Victim"}):
                                check_location = \
                                    state.get_closest_with_property(props={"class_inheritance": "Victim"})[0][
                                        'location']
                                agent_opacity = state.get_agents_with_property(props={"name": "agent"})[0]

                                if check_location and check_location == self.victim_location and agent_opacity != 0:

                                    mssg = Message(f'I found {victim_img} in {room_img}. '
                                                   f'I suggest you come here and help me to rescue together',
                                                   self.msg_id)
                                    self.__send_message(mssg)
                                    if self.received_messages and self.received_messages[-1].content == 'Ok':
                                        mssg = Message(f'Copy that.', self.msg_id)
                                        self.__send_message(mssg)
                                        self.received_messages = []
                                        self.phase = Phase.CARRY_TOGETHER
                                    elif self.received_messages and self.received_messages[-1].content == 'No':
                                        mssg = Message(f'Copy that.', self.msg_id)
                                        self.__send_message(mssg)
                                        self.received_messages = []
                                        self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                                    else:
                                        # self.phase = Phase.CARRY_TOGETHER
                                        self.received_messages = []
                                        return None, {}
                                    return None, {}
                                else:
                                    self.foundVictims.pop(self.victim_location)
                                    self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                                    return None, {}
                            else:
                                self.foundVictims.pop(self.victim_location)
                                self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                                return None, {}

                else:
                    self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                    return None, {}

            if self.phase == Phase.PLAN_PATH_TO_SAFE:
                safe_tiles = self.get_safe_zone_tiles(state)

                self._navigator.reset_full()
                self._navigator.add_waypoint(safe_tiles[-1])
                self._state_tracker.update(state)
                action = self._navigator.get_move_action(self._state_tracker)
                if action != None:
                    return action, {'action_duration': 5}
                else:
                    self.phase = Phase.DROP_VICTIM
                    return None, {}
                return None, {}

            if self.phase == Phase.DROP_VICTIM:
                action = DropAlone.__name__
                agent = state.get_agents_with_property(props={"name": "agent"})[0]
                agent['is_busy'] = False
                # action_kwargs['object_id'] = self.carry_obj_id
                if action != None:
                    self.phase = Phase.PLAN_RESCUE
                    self.foundVictims.pop(self.victim_location)
                    self.newly_found_victim.pop(self.victim_location)
                    self.victim_location = None
                    return action, {'object_id': self.carry_obj_id}
                return None, {}

            if self.phase == Phase.GO_TO_HUMAN:
                '''
                agent go to human's current location'''
                # get human's location
                self.humanLoc = state.get_agents_with_property(props={"name": "human"})[0].get('location')
                # go to human's location
                self.wayPoint.append(self.humanLoc)
                self._navigator.reset_full()
                self._navigator.add_waypoint(self.humanLoc)
                self._state_tracker.update(self.state)
                action = self._navigator.get_move_action(self._state_tracker)
                if action != None:
                    return action, {'action_duration': 5}
                else:
                    self.wayPoint.remove(self.humanLoc)
                    print('deleted arrived human loc')
                    self.phase = Phase.HELP_HUMAN
                    return None, {}

            if self.phase == Phase.WAIT_FOR_ANSWER:
                if not self.received_messages:
                    if self._state['World']['nr_ticks'] - self.lastWaitTick >= 400:
                        # self._send_message(Message('stop waiting', self.msg_id))
                        self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                else:
                    self.phase = self.preWaitPhase
                    self.prevPhase = None
                return None, {}

            if self.phase == Phase.HELP_HUMAN:
                '''
                check whether human needs help, 
                if so, remove/carry victim together, after collaboration, agent returns to previous location;
                if not, agent returns to previous location'''
                closest_tree_obstacle = state.get_closest_with_property(props={'type': 'tree'})
                closest_large_obstacle = state.get_closest_with_property(props={'type': 'large'})
                closest_injured_victim = state.get_closest_with_property(props={'type': 'injured'})
                closest_critical_victim = state.get_closest_with_property(props={'type': 'critical'})
                agentLoc = state.get_agents_with_property(props={"name": "agent"})[0].get('location')
                print('into help human phase')

                if closest_tree_obstacle and \
                        get_distance(closest_tree_obstacle[0]['location'], agentLoc) <= self.grabRange:
                    goal_location = closest_tree_obstacle[0]['location']
                    self.foundObstacle[goal_location] = closest_tree_obstacle
                    self.phase = Phase.REMOVE_TOGETHER
                    return None, {}
                elif closest_large_obstacle and \
                        get_distance(closest_large_obstacle[0]['location'], agentLoc) <= self.grabRange:
                    goal_location = closest_large_obstacle[0]['location']
                    self.foundObstacle[goal_location] = closest_large_obstacle
                    self.phase = Phase.REMOVE_TOGETHER
                    return None, {}
                elif closest_injured_victim and \
                        get_distance(closest_injured_victim[0]['location'], agentLoc) <= self.grabRange:
                    goal_location = closest_injured_victim[0]['location']
                    self.foundObstacle[goal_location] = closest_injured_victim
                    self.victim_location = goal_location
                    self.phase = Phase.CARRY_TOGETHER
                    return None, {}
                elif closest_critical_victim and \
                        get_distance(closest_critical_victim[0]['location'], agentLoc) <= self.grabRange:
                    goal_location = closest_critical_victim[0]['location']
                    self.victim_location = goal_location
                    self.foundObstacle[goal_location] = closest_critical_victim
                    self.phase = Phase.CARRY_TOGETHER
                    return None, {}
                else:
                    self._send_message(
                        Message(f'I do not think we need to work together. '
                                f'', self.msg_id))
                    self.phase = self.prevPhase
                    # self._send_message(
                    #     Message(f'current phase {self.phase}', self.msg_id))
                    return None, {}

            if self.phase == Phase.CARRY_TOGETHER:
                '''
                agent and human carry the victim to safe zone together'''
                print('into carry together phase')

                agent_location = state.get_agents_with_property(props={"name": "agent"})[0].get('location')
                human_location = state.get_agents_with_property(props={"name": "human"})[0].get('location')

                if get_distance(agent_location, human_location) <= 1:
                    # check whether the victim is still there
                    closest_victim = state.get_closest_with_property(props={"class_inheritance": "Victim"})
                    if closest_victim and closest_victim[0]['location'] == self.victim_location:
                        self.phase = Phase.WAIT_FOR_SAFE_ZONE
                    else:
                        self.foundVictims.pop(self.victim_location)
                        self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                return None, {}

            if self.phase == Phase.WAIT_FOR_SAFE_ZONE:
                self.agentPrevLoc = None
                agent_location = state.get_agents_with_property(props={"name": "agent"})[0].get('location')
                safe_zone_tiles = self.get_safe_zone_tiles(state)
                if agent_location in safe_zone_tiles:
                    # once arrives safe zone, agent removes the current victim from found_victim dict, and checks whether
                    # there is other found victims need to be rescued
                    if self.victim_location in self.foundVictims.keys():
                        # self.send_message(Message(f'self victim location{self.victim_location}', self.msg_id))
                        self.foundVictims.pop(self.victim_location)
                        self.victim_location = None
                        self.currentvictim = None
                        print('found victims after pop ', self.foundVictims)
                    if self.foundVictims:
                        print('self.foundvictims not none, ', self.foundVictims)
                        self.phase = Phase.BACK_TO_ROOM
                        self.victim_location = list(self.foundVictims.keys())[0]
                        self.room_location = list(self.foundVictims.keys())[0]
                        print('next found victim loc ', self.room_location)
                        # self.agentPrevLoc = location
                    else:
                        self.phase = Phase.GET_CLOSEST_STUCK_ROOM
                        self.victim_location = None
                        return None, {}
                return None, {}

            if self.phase == Phase.BACK_TO_ROOM:
                self._navigator.reset_full()
                self._navigator.add_waypoint(self.room_location)
                self._state_tracker.update(self.state)
                action = self._navigator.get_move_action(self._state_tracker)
                if action != None:
                    return action, {'action_duration': 5}
                else:
                    self.phase = Phase.PLAN_RESCUE
                    self.room_location = None
                    return None, {}
                return None, {}

            if self.phase == Phase.CARRY_VICTIM:
                '''
                agent carries the victim to the safe zone alone'''
                # self.agentPrevLoc = state.get_agents_with_property({"name": "agent"})[0].get('location')
                safe_zone = state.get_closest_with_property(props={'name': 'safe_zone'})[0].get('location')
                # self.wayPoint.append(safe_zone)
                self._navigator.reset_full()
                self._navigator.add_waypoint(safe_zone)
                self._state_tracker.update(self.state)
                action = self._navigator.get_move_action(self._state_tracker)
                if action != None:
                    return action, {'action_duration': 5}
                else:
                    return None, {}

            if self.phase == Phase.REMOVE_TOGETHER:
                '''
                agent asks human's help to remove obstacle
                agent and human removes the obstacle together
                agent checks whether the obstacle has been removed
                if so, then break the image, and search for room
                '''

                # self._send_message(Message(f'into remove together phase', self.msg_id))
                closest_obstacle = state.get_closest_with_property(props={'class_inheritance': 'Obstacle'})
                if closest_obstacle:
                    obstacle_location = closest_obstacle[0]['location']
                else:
                    return None, {}
                agent_location = state.get_agents_with_property(props={"name": "agent"})[0].get('location')
                human_location = state.get_agents_with_property(props={"name": "human"})[0].get('location')
                door = state.get_closest_with_property(props={'class_inheritance': 'Door'})[0]
                if door['room_name'] not in self.searedRooms:
                    self.roomName = door['room_name']
                if get_distance(agent_location, human_location) == 0 and \
                        get_distance(agent_location, obstacle_location) <= 1:
                    self.phase = Phase.WAIT_REMOVE
                else:
                    return None, {}

                return None, {}

            if self.phase == Phase.WAIT_REMOVE:
                '''
                wait for the obstacle to be removed together'''
                closest_obstacle = state.get_closest_with_property(props={'class_inheritance': 'Obstacle'})
                agent_location = state.get_agents_with_property(props={"name": "agent"})[0].get('location')
                human_location = state.get_agents_with_property(props={"name": "human"})[0].get('location')
                if not closest_obstacle or get_distance(closest_obstacle[0]['location'], agent_location) > 1:
                    self.phase = Phase.PLAN_PATH_IN_ROOM
                    return None, {}
                else:
                    return None, {}

            if self.phase == Phase.WAIT_FOR_SEARCH_ROOM:
                '''
                checks whether the obstacle has been removed
                '''
                if not state.get_closest_with_property(props={'location': str(self.lastObstacleLoc),
                                                              'class_inheritance': 'Obstacle'}):
                    self.phase = Phase.PLAN_PATH_IN_ROOM

                return None, {}

        def go_to_loc(self, state: State, loc):
            self.wayPoint.append(loc)
            self._navigator.add_waypoint(loc)
            self._state_tracker.update(state)
            action = self._navigator.get_move_action(self._state_tracker)
            if action != None:
                return action, {'action_duration': 7}
            else:
                return None, {}

    def get_safe_zone_tiles(self, state: State):
        tiles = []
        room_values = state.get_room('safe_zone')
        if room_values:
            for r in room_values:
                if 'AreaTile' in r['class_inheritance']:
                    tiles.append(r['location'])
        return tiles

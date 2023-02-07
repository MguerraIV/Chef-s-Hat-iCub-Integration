# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
import numpy as np
import socket
import pickle
import random
from numbers import Number
from ChefsHatGym.Rewards import RewardOnlyWinning, RewardPerformanceScore

class IAgent():
    """This is the Agent class interface. Every new Agent must inherit from this class and implement the methods below."""
    __metaclass__ = ABCMeta
    name = "" #: Class attribute to store the name of the agent
    saveModelIn = "" #: Class attribute path to a folder acessible by this agent to save/load from
    
    @abstractmethod
    def __init__(self, name, saveModelIn, _):
        """Constructor method.

        :param name: The name of the Agent (must be a unique name).
        :type name: str

        :param saveModelIn: a folder acessible by this agent to save/load from
        :type saveModelIn: str

        :param _: Other parameters that your Agent must need
        :type _: obj, optional

        """
        pass

    @abstractmethod
    def getAction(self, observations):
        """This method returns one action given the observation parameter.

                :param observations: The observation is an int data-type ndarray.
                                    The observation array has information about the board game, the player's hand, and possible actions.
                                    This array must have the shape of (228, ) as follows:
                                    The first 11 elements represent the board game card placeholder (the pizza area).
                                    The game cards are represented by an integer, where 0 (zero) means no card.
                                    The following 17 elements (from index 11 to 27) represent the player hand cards in the sequence.
                                    By the end, the last 200 elements (from index 28 to 227) represent all possible actions in the game.
                                    The allowed actions are filled with one, while invalid actions are filled with 0.
                :type observations: ndarray
                :return: The action array with 200 elements, where the choosen action is the index of the highest value
                :rtype: ndarray
        """

        pass

    @abstractmethod
    def getReward(self, info, stateBefore, stateAfter):
        """The Agent reward method, called inside each evironment step.

                :param info: [description]
                :type info: dict

                :param stateBefore: The observation before the action happened is an int data-type ndarray.
                                    The observationBefore array has information (before the player's action) about the board game, the player's hand, and possible actions.
                                    This array must have the shape of (228, ) as follows:
                                    The first 11 elements represent the board game card placeholder (the pizza area).
                                    The game cards are represented by an integer, where 0 (zero) means no card.
                                    The following 17 elements (from index 11 to 27) represent the player hand cards in the sequence.
                                    By the end, the last 200 elements (from index 28 to 227) represent all possible actions in the game.
                                    The allowed actions are filled with one, while invalid actions are filled with 0.
                :type stateBefore: ndarray

                :param stateAfter: The observation after the action happened is an int data-type ndarray.
                                    The observationBefore array has information (after the player's action) about the board game, the player's hand, and possible actions.
                                    This array must have the shape of (228, ) as follows:
                                    The first 11 elements represent the board game card placeholder (the pizza area).
                                    The game cards are represented by an integer, where 0 (zero) means no card.
                                    The following 17 elements (from index 11 to 27) represent the player hand cards in the sequence.
                                    By the end, the last 200 elements (from index 28 to 227) represent all possible actions in the game.
                                    The allowed actions are filled with one, while invalid actions are filled with 0.
                :type stateAfter: ndarray

                """

        pass

    @abstractmethod
    def observeOthers(self, envInfo):
        """This method gives the agent information of other playes actions. It is called after each other player action.

        :param envInfo: [description]
        :type envInfo: [type]
        """

        pass

    @abstractmethod
    def actionUpdate(self,  observation, nextObservation, action, envInfo):
        """This method that is called after the Agent's action.

                :param observation: The observation is an int data-type ndarray.
                                    The observation array has information about the board game, the player's hand, and possible actions.
                                    This array must have the shape of (228, ) as follows:
                                    The first 11 elements represent the board game card placeholder (the pizza area).
                                    The game cards are represented by an integer, where 0 (zero) means no card.
                                    The following 17 elements (from index 11 to 27) represent the player hand cards in the sequence.
                                    By the end, the last 200 elements (from index 28 to 227) represent all possible actions in the game.
                                    The allowed actions are filled with one, while invalid actions are filled with 0.
                :type observation: ndarray
                :param nextObservation: The nextObservation is an int data-type ndarray.
                                    The nextObservation array has information about the board game, the player's hand, and possible actions.
                                    This array must have the shape of (228, ) as follows:
                                    The first 11 elements represent the board game card placeholder (the pizza area).
                                    The game cards are represented by an integer, where 0 (zero) means no card.
                                    The following 17 elements (from index 11 to 27) represent the player hand cards in the sequence.
                                    By the end, the last 200 elements (from index 28 to 227) represent all possible actions in the game.
                                    The allowed actions are filled with one, while invalid actions are filled with 0.
                :type nextObservation: ndarray
                :param action: The action array with 200 elements, where the choosen action is the index of the highest value
                :type action: ndarray
                :param envInfo: [description]
                :type envInfo: [type]
                """

        pass

    @abstractmethod
    def matchUpdate(self,  envInfo):
        """This method that is called by the end of each match. This is an oportunity to update the Agent with information gathered in the match.

                :param envInfo: [description]
                :type envInfo: [type]
                """
        pass

    def sendPickle(self, sock: socket.socket, data): # This method sends data about the game environment through the Pickle library.
        sock.sendall(pickle.dumps(data) + b'.EOF')

    def receivePickle(self, sock: socket.socket): # This method is used to receive the data saved by pickle.
        data = []
        while True:
            packet = sock.recv(1024)
            data.append(packet)
            if packet.endswith(b'.EOF'):
                break
        data = pickle.loads(b''.join(data)[:-4])
        return data

    def listen(self, port=8080): # This method is used to connect the game environment to the human player/AI Agent.
        s = socket.socket()
        s.bind(('', port))
        s.listen(1)

        while True:
            w, _ = s.accept()
            d = self.receivePickle(w)
            method = d[0]
            args = d[1:]
            
            r = None
            
            if method == 'getAction':
                r = self.getAction(*args)
            elif method == 'getReward':
                r = self.getReward(*args)
            elif method == 'observeOthers':
                r = self.observeOthers(*args)
            elif method == 'actionUpdate':
                r = self.actionUpdate(*args)
            elif method == 'matchUpdate':
                r = self.matchUpdate(*args)
            else:
                r = None

            self.sendPickle(w, r)
            w.close()
    
    def fetch(self, method, *parameters): # This method uses websockets to send data and receive it.
        s = socket.socket()
        s.connect((self.ip, self.port))

        try:
            self.sendPickle(s, [method] + [p for p in parameters])
            r = self.receivePickle(s)
        except:
            r = None

        s.close()

class RemoteAgent(IAgent): # This class creates a remote Agent that can run in the localhost or any other ip address.
    def __init__(self, name="NAIVE", ip='localhost', port=8080):
        self.name = "RANDOM_"+name
        self.ip = socket.gethostbyname(socket.gethostname()) if ip == 'localhost' else ip
        self.port = port

    def getAction(self, observations):
        r = self.fetch('getAction', observations)
        return r if isinstance(r, np.ndarray) else np.zeros(200)

    def actionUpdate(self, observations, nextobs, action, reward, info):
        r = self.fetch('actionUpdate', observations, nextobs, action, reward, info)
        if isinstance(r, type(None)):
            pass
        else:
            return r

    def observeOthers(self, envInfo):
        r = self.fetch('observeOthers', envInfo)
        if isinstance(r, type(None)):
            pass
        else:
            return r

    def matchUpdate(self, envInfo):
        r = self.fetch('matchUpdate', envInfo)
        if isinstance(r, type(None)):
            pass
        else:
            return r

    def getReward(self, info, stateBefore, stateAfter):
        r = self.fetch('getReward', info, stateBefore, stateAfter)
        return r if isinstance(r, Number) else 0

class AgentNaive_Random(IAgent): # This class has a IAgent implementation and uses it to create a Agent with random actions.
    def __init__(self, name="NAIVE"):
        self.name = "RANDOM_"+name
        self.reward = RewardOnlyWinning()
    
    def getAction(self, observations):
        itemindex = np.array(np.where(np.array(observations[28:]) == 1))[0].tolist()
        random.shuffle(itemindex)
        a = np.array([1 if i == itemindex[0] else 0 for i in range(200)])
        return a

    def actionUpdate(self, observations, nextobs, action, reward, info):
        pass

    def observeOthers(self, envInfo):
        pass

    def matchUpdate(self, envInfo):
        pass

    def getReward(self, info, stateBefore, stateAfter):
        return self.reward.getReward(info["thisPlayerPosition"], info["thisPlayerFinished"])

class HumanAgent(IAgent): # This class creates the possibility to insert human players in the game using the IAgent's class as a param.
    def __init__(self, name="HUMAN"):
        self.name = name
        self.reward = RewardOnlyWinning()

    def getAction(self, observations): #This method is kind a different compared to the others because it needs a entry from the board.
        possibilities = observations[28:]
        observations = np.array(np.array(observations[:28]) * 13, dtype=int).tolist()
        idx = -1

        print(f'This is the board {observations[0:11]}')
        print(f'These are your cards {observations[11:28]}')

        while True:
            cards = [int(i) for i in input('What cards would you like to play? ').split()]
            idx = self.calculate_idx(cards)

            if idx < 0 or possibilities[idx] <= 0:
                print('Sorry, this is an invalid move.')
            else:
                return [(1 if i == idx else 0) for i in range(200)]

    def actionUpdate(self, observations, nextobs, action, reward, info):
        pass

    def observeOthers(self, envInfo):
        pass

    def matchUpdate(self, envInfo):
        pass

    def getReward(self, info, stateBefore, stateAfter):
        pass
    
    def calculate_idx(self, cardsPlayed):
        unique, counts = np.unique(cardsPlayed, return_counts=True)
        hand = dict(zip(unique, counts))

        # Pass
        if len(hand) == 0:
            return 199
        # Discard one joker
        elif len(hand) == 1 and 12 in hand.keys() and hand[12] == 1:
            return 198
        # Normal actions
        elif (len(hand) == 1 and not 12 in hand.keys()) or (len(hand) == 2 and 12 in hand.keys()):
            card_num = list(hand.keys())[0]
            joker_amnt = 0 if len(hand) == 1 else min(hand[12], 2)
            card_amnt = min(card_num, hand[card_num])
            offset = (3 * (card_num - 1) * card_num // 2) + (card_amnt - 1) * 3
            return np.clip(offset + joker_amnt, 0, 199)
        # Invalid action
        else:
            return -1

class UnityAgent(IAgent): # This method is used to connect the game environment to the Unity interface by the ip address.
    def __init__(self, name="HUMAN", ip='localhost', port=8000):
        self.name = name
        self.ip = socket.gethostbyname(socket.gethostname()) if ip == 'localhost' else ip
        self.port = port

    def getAction(self, observations):
        return np.array(self.fetchUnity(observations))

    def actionUpdate(self, observations, nextobs, action, reward, info):
        pass

    def observeOthers(self, envInfo):
        pass

    def matchUpdate(self, envInfo):
        pass

    def getReward(self, info, stateBefore, stateAfter):
        pass

    def sendUnity(self, sock: socket.socket, data):
        encoded = b''

        if type(data) == np.ndarray:
            if len(data) == 228:
                data = np.array(data * 13, dtype=int)
            data = data.tolist()
        
        if type(data) == list and len(data) > 0:
            if type(data[0]) == int:
                encoded = f'__list__int__{str(data).replace(",", "")[1:-1]}.EOF'.encode()
        elif type(data) == bool:
            encoded = f'__bool__{1 if data else 0}.EOF'.encode()
        elif type(data) == str:
            encoded = f'__string__{data}.EOF'.encode()
        
        if encoded != b'':
            sock.sendall(encoded)

    def receiveUnity(self, sock: socket.socket): # This method is used to receive information about the game board from the Unity interface.
        data = []
        while True:
            packet = sock.recv(1024)
            data.append(packet)
            if packet.endswith(b'.EOF'):
                break
        data = b''.join(data)[:-4].decode()

        decoded = ''
        if data.startswith('__list__int__'):
            decoded = [int(i) for i in data.replace('__list__int__', '').split()]

        return decoded
    
    def fetchUnity(self, data): # This method is used to connect both interfaces (Unity and Chef's Hat Environment)
        s = socket.socket()
        s.connect((self.ip, self.port))
        self.sendUnity(s, data)
        m = self.receiveUnity(s)
        s.close()
        return m
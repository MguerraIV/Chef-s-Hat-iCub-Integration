from ChefsHatGym.Agents import AgentNaive_Random, RemoteAgent, HumanAgent, UnityAgent
from ChefsHatGym.Rewards import RewardOnlyWinning
from ChefsHatGym.env import ChefsHatEnv
import gym
from multiprocessing import Process

if __name__ == '__main__':
    """Game parameters"""
    gameType = ChefsHatEnv.GAMETYPE["MATCHES"]
    gameStopCriteria = 1
    rewardFunction = RewardOnlyWinning()

    """Player Parameters"""
    agent1 = UnityAgent('UNI Agent', '192.168.0.107', 8000)

    agent2 = RemoteAgent('Remote Agent', '192.168.0.107', 8080)
    agent2_local = AgentNaive_Random("Random2")
    p = Process(target=agent2_local.listen, args=(agent2.port,), daemon=True)
    p.start()

    agent3 = AgentNaive_Random("Random3")
    agent4 = AgentNaive_Random("Random4")
    agentNames = [agent1.name, agent2.name, agent3.name, agent4.name]
    playersAgents = [agent1, agent2, agent3, agent4]

    rewards = []
    for r in playersAgents:
        rewards.append(r.getReward)

    """Experiment parameters"""
    saveDirectory = "examples/"
    verbose = False
    saveLog = False
    saveDataset = False
    episodes = 1


    """Setup environment"""
    env = gym.make('chefshat-v0') #starting the game Environment
    env.startExperiment(rewardFunctions=rewards, gameType=gameType, stopCriteria=gameStopCriteria, playerNames=agentNames, logDirectory=saveDirectory, verbose=verbose, saveDataset=True, saveLog=True)

    """Start Environment"""
    for _ in range(episodes):
        observations = env.reset()
        n = 0

        while not env.gameFinished:
            currentPlayer = playersAgents[env.currentPlayer]
            observations = env.getObservation()
            action = currentPlayer.getAction(observations)

            info = {"validAction":False}

            while not info["validAction"]:
                nextobs, reward, isMatchOver, info = env.step(action)

            if isMatchOver:
                n += 1
                print ("-------------")
                print ("Match:" + str(n))
                print ("Score:" + str(info["score"]))
                print("Performance:" + str(info["performanceScore"]))
                print("-------------")

    
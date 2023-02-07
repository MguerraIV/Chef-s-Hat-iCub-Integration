class RewardOnlyWinning():
    rewardName = "OnlyWinning"
    getReward = lambda self, thisPlayerPosition, matchFinished: 1 if matchFinished and thisPlayerPosition == 0 else -0.001

class RewardPerformanceScore():
    rewardName = "PerformanceScore"
    getReward = lambda self, thisPlayerPosition, performanceScore, matchFinished: (((3 - thisPlayerPosition) / 3) + performanceScore) if matchFinished else -0.001

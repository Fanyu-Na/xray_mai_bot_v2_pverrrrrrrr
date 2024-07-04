from typing import Dict, List

class Recommend:
    def __init__(self,musicRating):
        self.recommendData = {}
        self.recommendData["Rating"] = musicRating
        self.recommendData["RankSSSP"] = self.get_TargetDs(musicRating, 100.5)
        self.recommendData["RankSSS"] = self.get_TargetDs(musicRating, 100.0)
        self.recommendData["RankSSP"] = self.get_TargetDs(musicRating, 99.5)
        self.recommendData["RankSS"] = self.get_TargetDs(musicRating, 99.0)


    def getRatingRecommendData(self):
        return self.recommendData

    def computeRa(self,ds: float, achievement: float) -> int:
        baseRa = 22.4 
        if achievement < 50:
            baseRa = 7.0
        elif achievement < 60:
            baseRa = 8.0 
        elif achievement < 70:
            baseRa = 9.6 
        elif achievement < 75:
            baseRa = 11.2 
        elif achievement < 80:
            baseRa = 12.0 
        elif achievement < 90:
            baseRa = 13.6 
        elif achievement < 94:
            baseRa = 15.2 
        elif achievement < 97:
            baseRa = 16.8 
        elif achievement < 98:
            baseRa = 20.0 
        elif achievement < 99:
            baseRa = 20.3
        elif achievement < 99.5:
            baseRa = 20.8 
        elif achievement < 100:
            baseRa = 21.1 
        elif achievement < 100.5:
            baseRa = 21.6 

        return int(ds * (min(100.5, achievement) / 100) * baseRa)
    
    def get_TargetDs(self, ra: int, rank: float):
        for d in [x/10 for x in range(10,151)]:
            if self.computeRa(d, rank) in [ra, ra+1,ra+2]:
                return d
        return -1
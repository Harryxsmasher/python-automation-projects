import numpy as np

marks = np.array([85, 92, 78, 95, 88])
attendance = np.array([92, 88, 96, 81, 90])

class ReportGenerator:
    def __init__(self, max, min, sum, average, max_position, min_position):
        self.max = max
        self.min = min
        self.sum = sum
        self.average = average
        self.max_position = max_position
        self.min_position = min_position
        

    def getters(self):
        pass
import random

class Error:
    def isError(self):
        probability = random.randint(1,100)
        return probability > 75
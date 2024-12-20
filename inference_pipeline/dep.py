import random

class dependencies():
    def __init__(self):
        pass
    
    def roll_dice(self, total_faces, number_of_dices):
        rolls = [random.randint(1, total_faces) for _ in range(number_of_dices)]
        return rolls
    
    def drop_low_sum(self, total_faces, number_of_dices):
        rolls = self.roll_dice(total_faces, number_of_dices)
        rolls.remove(min(rolls))
        total = sum(rolls)
        return total
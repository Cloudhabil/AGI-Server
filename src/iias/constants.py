"""IIAS Constants - Brahim Numbers and PHI"""

import math

PHI = (1 + math.sqrt(5)) / 2  # 1.6180339887498949
CENTER = 107
SUM_CONSTANT = 214

BRAHIM_NUMBERS = [27, 42, 60, 75, 97, 117, 139, 154, 172, 187]
B = {i: BRAHIM_NUMBERS[i-1] for i in range(1, 11)}

LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
TOTAL_STATES = 840

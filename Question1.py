import numpy as np
from math import exp

def price(Asset, Volatility, IntRate, Strike, Expiry, NoSteps):

    timestep = int(Expiry)/NoSteps
    DiscountFactor = exp((-IntRate) * timestep)
    temp1 = exp((IntRate + (Volatility * Volatility)) * timestep)
    temp2 = 0.5 * (DiscountFactor + temp1)

    u = temp2 + ((temp2 * temp2) - 1) ** 0.5
    d = 1/u
    p = (exp((IntRate * timestep) - d)) / (u - d)
    S = np.zeros([NoSteps + 1, NoSteps + 1])

    for i in range(NoSteps + 1):
        for j in range(NoSteps + 1):
            S[j, i] = Asset * (u ** (i - j)) * (d ** j)

    option = np.zeros([NoSteps + 1, NoSteps + 1])
    option[:, NoSteps] = np.maximum((S[:, NoSteps] - Strike), np.zeros(NoSteps + 1))

    for i in range(NoSteps - 1, -1, -1):
        for j in range(0, i + 1):
            option[j, i] = DiscountFactor * (p * option[j, i + 1] + (1 - p)*(option[j+1, i+1]))

    return option
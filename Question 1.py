import numpy as np


'''

    Binomial Options Pricing Model -

    Arguments -

    S - spot price
    K - strike price
    T - time to expiration (years)
    r - risk free interest rate
    v - volatility
    q - dividend yield
    n - number of nodes
    option - 'C' for Call, 'P' for Put

'''


def Binomial(S, K, T, r, v, n, option):

    dt = T/(n - 1)
    u = np.exp(v * np.sqrt(dt))
    d = 1/u
    p = (np.exp(r * dt) - d) / (u - d)

    call_prices  = np.zeros([n, n])
    stock_prices = np.zeros([n, n])
    stock_prices[0, 0] = S

    for i in range(1, n):
        stock_prices[i, 0] = d * stock_prices[i - 1, 0]
        for j in range(1, i + 1):
            stock_prices[i, j] = u * stock_prices[i - 1, j - 1]

    if option == 'C':
        call_prices[-1:] = np.where((stock_prices[-1:] - K)[0][:] > 0, (stock_prices[-1:] - K)[0][:], 0)
    if option == 'P':
        call_prices[-1:] = np.where((K - stock_prices[-1:])[0][:] > 0, (K - stock_prices[-1:])[0][:], 0)

    for i in range(n - 2, -1, -1):
        for j in range(i + 1):
            call_prices[i, j] = np.exp(-r * dt) * (p * call_prices[i + 1, j + 1] + (1 - p) * call_prices[i + 1, j])

    return call_prices[0, 0]

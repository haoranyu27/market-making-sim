import numpy as np
import pandas as pd 

def simulate_price(rng, s0=100.0, sigma=0.01, n_steps=3600):
    """Random walk: one step per second, one hour by default."""
    shocks = rng.normal(0, sigma, n_steps)
    return s0 + np.concatenate([[0], shocks.cumsum()]) 

def fill_probability(distance, A=0.5, k=100):
    """Chance that a quote at this distance from the mid gets filled in one second."""
    return A * np.exp(-k * distance)

def run_market_maker(rng, prices, distance=0.01, A=0.5, k=100, skew=0.0):   # NEW: skew
    """Market maker quoting around a reservation price that shifts with inventory."""
    cash = 0.0
    inventory = 0
    records = []

    for t in range(len(prices) - 1):
        mid = prices[t]
        reservation = mid - skew * inventory                 # NEW
        bid = reservation - distance                         # NEW: around reservation
        ask = reservation + distance                         # NEW

        p_bid = fill_probability(mid - bid, A, k)            # NEW: each side has
        p_ask = fill_probability(ask - mid, A, k)            # NEW: its own chance

        if rng.random() < p_bid:      # a seller arrives: we BUY at our bid
            inventory += 1
            cash -= bid

        if rng.random() < p_ask:      # a buyer arrives: we SELL at our ask
            inventory -= 1
            cash += ask

        next_price = prices[t + 1]
        pnl = cash + inventory * next_price
        records.append({"mid": next_price, "inventory": inventory,
                        "cash": cash, "pnl": pnl})

    return pd.DataFrame(records) 
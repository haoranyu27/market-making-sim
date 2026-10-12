import numpy as np
import pandas as pd 

def simulate_price(rng, s0=100.0, sigma=0.01, n_steps=3600):
    """Random walk: one step per second, one hour by default."""
    shocks = rng.normal(0, sigma, n_steps)
    return s0 + np.concatenate([[0], shocks.cumsum()]) 

def fill_probability(distance, A=0.5, k=100):
    """Chance that a quote at this distance from the mid gets filled in one second."""
    return A * np.exp(-k * distance)

def run_market_maker(rng, prices, distance=0.01, A=0.5, k=100, skew=0.0,
                     informed_rate=0.0, horizon=60):                     # NEW
    """Market maker facing random traders and, optionally, informed traders."""
    cash = 0.0
    inventory = 0
    records = []
    last = len(prices) - 1

    for t in range(last):
        mid = prices[t]
        reservation = mid - skew * inventory
        bid = reservation - distance
        ask = reservation + distance

        p_bid = fill_probability(mid - bid, A, k)
        p_ask = fill_probability(ask - mid, A, k)

        # Random traders (as before)
        if rng.random() < p_bid:
            inventory += 1
            cash -= bid
        if rng.random() < p_ask:
            inventory -= 1
            cash += ask

        # NEW: informed trader, who knows the price `horizon` seconds ahead
        future = prices[min(t + horizon, last)]
        if rng.random() < informed_rate:
            if future > ask:          # price will rise above our ask: they buy
                inventory -= 1
                cash += ask
            elif future < bid:        # price will fall below our bid: they sell
                inventory += 1
                cash -= bid

        next_price = prices[t + 1]
        pnl = cash + inventory * next_price
        records.append({"mid": next_price, "inventory": inventory,
                        "cash": cash, "pnl": pnl})

    return pd.DataFrame(records)
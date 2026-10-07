import numpy as np
from src.simulation import simulate_price

def test_length_and_start():
    rng = np.random.default_rng(0)
    prices = simulate_price(rng, s0=50, n_steps=100)
    assert len(prices) == 101
    assert prices[0] == 50
"""
Module to read the state of vether pools.
"""

from .interface import (
    get_pools,
    get_price,
    get_veth_to_token_swap_amount,
    get_token_to_veth_swap_amount,
    get_volume,
    get_pooled_balance_for_address,
    get_reserves,
    get_exchange_address_for_pair,
)

__version__ = "0.0.1"
__author__ = "0x1d00ffff"

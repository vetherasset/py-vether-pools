# py-vether-pools
Library to interact with vether pools

## Usage
```py
from web3 import Web3
web3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))

# simple price
print('ETH/VETH price: {} VETH'.format(get_price(web3, "ETH")))

# accurate price (using a given swap amount)
from pyvetherpools import get_veth_to_token_swap_amount
from pyvetherpools import get_token_to_veth_swap_amount
print('10 Vether will swap for {} Ether'.format(get_veth_to_token_swap_amount(web3, 10, "ETH")))
print(' 1 Ether will swap for {} Vether'.format(get_token_to_veth_swap_amount(web3, 1, "ETH")))

# volume
from pyvetherpools import get_volume
veth_volume, other_volume = get_volume(web3, "ETH", num_hours=24)
print(f'ETH/VETH Pool Volume in the last 24 hours: {other_volume} Ether and {veth_volume} Vether')

# account liquidity balances
from pyvetherpools import get_pooled_balance_for_address
veth_balance, other_balance = get_pooled_balance_for_address(web3, "0x4Ba6dDd7b89ed838FEd25d208D4f644106E34279")
print('Account has pooled {other_balance} Ether and {veth_balance} Vether'.format(get_exchange_address_for_pair("ETH")))

# pool liquidity balances
from pyvetherpools import get_reserves
veth_balance, other_balance = get_reserves(web3, "ETH")
print(f'ETH/VETH Pool contains a total of {other_balance} Ether and {veth_balance} Vether')

# contract lookup
from pyvetherpools import get_exchange_address_for_pair
print('ETH/VETH Pool address: {}'.format(get_exchange_address_for_pair(web3, "ETH")))
```


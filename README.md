# py-vether-pools
Library to interact with vether pools

## Usage
```py
from web3 import Web3
web3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))

# list pools
from pyvetherpools import get_pools
print('Pools: {}'.format(list(get_pools(web3))))

# simple price
from pyvetherpools import get_price
print('ETH/VETH price: {} VETH'.format(get_price(web3, "ETH")))

# accurate price (using a given swap amount)
from pyvetherpools import get_veth_to_token_swap_amount
print('10 Vether will swap for {} Ether'.format(get_veth_to_token_swap_amount(web3, "ETH", 10)))
from pyvetherpools import get_token_to_veth_swap_amount
print(' 1 Ether will swap for {} Vether'.format(get_token_to_veth_swap_amount(web3, "ETH", 1)))

# volume
from pyvetherpools import get_volume
volume = get_volume(web3, num_hours=24)
print(f'Volume across all pools in the last 24 hours: {volume}')
volume = get_volume(web3, currency_symbol="ETH", num_hours=24)
print(f'Volume in ETH/VETH pool in the last 24 hours: {volume}')

# account liquidity balances
from pyvetherpools import get_pooled_balance_for_address
veth_balance, other_balance = get_pooled_balance_for_address(web3, "ETH", "0xa66E0D17970A01Ae4E309E2E0b66CE2C41a36C13")
print(f'Account has pooled {other_balance} Ether and {veth_balance} Vether in ETH/VETH pool')

# pool liquidity balances
from pyvetherpools import get_reserves
veth_balance, other_balance = get_reserves(web3, "ETH")
print(f'Total of {other_balance} Ether and {veth_balance} Vether in ETH/VETH Pool')

# contract lookup
from pyvetherpools import get_exchange_address_for_pair
print('ETH/VETH Pool address: {}'.format(get_exchange_address_for_pair(web3, "ETH")))

# show version
from pyvetherpools import __version__
print('Module version: {}'.format(__version__))
```
Example output:
```
Pools: [
    ('0x0000000000000000000000000000000000000000', '0x80A486d111885E59Ba35dB182551A84b3a715Db8'), 
    ('0x6B175474E89094C44Da98b954EedeAC495271d0F', '0x19186878BDC81B9CD5685A64344Ef10F01693DE4')]
ETH/VETH price: 61.13123578116094 VETH
10 Vether will swap for 0.15942955355298571 Ether
 1 Ether will swap for 52.496886597055585 Vether
Volume across all pools in the last 24 hours: defaultdict(<class 'int'>, {
    '0x4Ba6dDd7b89ed838FEd25d208D4f644106E34279': 37.19813825454537,
    '0x0000000000000000000000000000000000000000': 0.595409084181604})
Volume in ETH/VETH pool in the last 24 hours: defaultdict(<class 'int'>, {
    '0x4Ba6dDd7b89ed838FEd25d208D4f644106E34279': 37.19813825454537,
    '0x0000000000000000000000000000000000000000': 0.595409084181604})
Account has pooled 0.082155508201939 Ether and 5.022267742613834 Vether in ETH/VETH pool
Total of 12.640985641246395 Ether and 772.7590737413033 Vether in ETH/VETH Pool
ETH/VETH Pool address: 0x80A486d111885E59Ba35dB182551A84b3a715Db8
Module version: 0.0.1
```

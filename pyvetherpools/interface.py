from collections import defaultdict

from .router_vether_abi import router_vether_abi
from .utils_vether_abi import utils_vether_abi
from .pools_vether_abi import pools_vether_abi
from .erc20_abi import erc20_abi

_VETHER_ROUTER_ADDRESS = "0xe16e64Da1338d8E56dFd8355Ba7642D0A79e253c"
_VETHER_UTILS_ADDRESS = "0x0f216323076dfe029f01B3DeB3bC1682B1ea8A37"
_SECONDS_PER_ETH_BLOCK = 13.5  # average of Sep 2019 - Sep 2020

# list of tokens used by this module
# token name, token address, token decimals
_tokens = (
    ("SHUF", "0x3A9FfF453d50D4Ac52A6890647b823379ba36B9E", 18),
    ("DAI", "0x6B175474E89094C44Da98b954EedeAC495271d0F", 18),
    ("USDC", "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", 6),
    ("0xBTC", "0xB6eD7644C69416d67B522e20bC294A9a9B405B31", 8),
    ("ETH", "0x0000000000000000000000000000000000000000", 18),
    ("DONUT", "0xC0F9bD5Fa5698B6505F643900FFA515Ea5dF54A9", 18),
    ("USDT", "0xdAC17F958D2ee523a2206206994597C13D831ec7", 6),
)


def _currency_symbol_to_address(currency_symbol):
    currency_symbol = "ETH" if currency_symbol == "WETH" else currency_symbol
    return [i[1] for i in _tokens if i[0] == currency_symbol][0]


def _contract_calcSwapOutput(web3, x, X, Y):
    # y = (x * Y * X)/(x + X)^2
    numerator = x * Y * X
    denominator = (x + X) * (x + X)
    y = numerator / denominator
    return int(y)


def _get_pooldata_field_by_name(web3, currency_symbol, field_name):
    # TODO: pull these from the ABI somehow - or maybe the contract?
    #  struct PoolDataStruct {
    #     address tokenAddress;
    #     address poolAddress;
    #     uint genesis;
    #     uint baseAmt;
    #     uint tokenAmt;
    #     uint baseAmtStaked;
    #     uint tokenAmtStaked;
    #     uint fees;
    #     uint volume;
    #     uint txCount;
    #     uint poolUnits;
    # }
    pooldata_fields = (
        'tokenAddress', 'poolAddress', 'genesis', 'baseAmt', 'tokenAmt',
        'baseAmtStaked', 'tokenAmtStaked', 'fees', 'volume', 'txCount', 'poolUnits')
    currency_address = _currency_symbol_to_address(currency_symbol)
    utils = web3.eth.contract(address=_VETHER_UTILS_ADDRESS, abi=utils_vether_abi)
    pool_data = utils.functions.getPoolData(currency_address).call()
    return pool_data[pooldata_fields.index(field_name)]


def get_exchange_address_for_pair(web3, currency_symbol):
    currency_address = _currency_symbol_to_address(currency_symbol)
    router = web3.eth.contract(address=_VETHER_ROUTER_ADDRESS, abi=router_vether_abi)
    pool_address = router.functions.getPool(currency_address).call()
    return pool_address


def get_pools(web3):
    """Iterator over all pools. Returns tuples like (token_address, pool_address)."""
    router = web3.eth.contract(address=_VETHER_ROUTER_ADDRESS, abi=router_vether_abi)
    for index in range(router.functions.tokenCount().call()):
        token = router.functions.getToken(index).call()
        pool_address = router.functions.getPool(token).call()
        yield token, pool_address


def get_price(web3, currency_symbol):
    currency_address = _currency_symbol_to_address(currency_symbol)
    utils = web3.eth.contract(address=_VETHER_UTILS_ADDRESS, abi=utils_vether_abi)
    price = web3.fromWei(
        utils.functions.calcValueInToken(
            currency_address,
            web3.toWei(1, 'ether')).call(),
        'ether')
    return 1 / float(price)


def get_reserves(web3, currency_symbol):
    veth_amount = _get_pooldata_field_by_name(web3, currency_symbol, 'baseAmt')
    token_amount = _get_pooldata_field_by_name(web3, currency_symbol, 'tokenAmt')
    return (
        float(web3.fromWei(veth_amount, 'ether')),
        float(web3.fromWei(token_amount, 'ether')))


def get_veth_to_token_swap_amount(web3, currency_symbol, amount):
    pool_veth_balance, pool_token_balance = get_reserves(web3, currency_symbol)
    value_in_token = web3.fromWei(
        _contract_calcSwapOutput(
            web3,
            web3.toWei(amount, 'ether'),
            web3.toWei(pool_veth_balance, 'ether'),
            web3.toWei(pool_token_balance, 'ether')),
        'ether')
    return float(value_in_token)


def get_token_to_veth_swap_amount(web3, currency_symbol, amount):
    pool_veth_balance, pool_token_balance = get_reserves(web3, currency_symbol)
    value_in_veth = web3.fromWei(
        _contract_calcSwapOutput(
            web3,
            web3.toWei(amount, 'ether'),
            web3.toWei(pool_token_balance, 'ether'),
            web3.toWei(pool_veth_balance, 'ether')),
        'ether')
    return float(value_in_veth)


def get_pooled_balance_for_address(web3, currency_symbol, address):
    currency_address = _currency_symbol_to_address(currency_symbol)
    router = web3.eth.contract(address=_VETHER_ROUTER_ADDRESS, abi=router_vether_abi)
    pool_address = router.functions.getPool(currency_address).call()
    pool = web3.eth.contract(address=pool_address, abi=pools_vether_abi)

    balance = pool.functions.balanceOf(address).call()  # balance in liquidity tokens
    total_supply = pool.functions.totalSupply().call()
    ownership_percentage = balance / total_supply

    reserves = get_reserves(web3, currency_symbol)
    return reserves[0] * ownership_percentage, reserves[1] * ownership_percentage


def get_volume(web3, currency_symbol=None, num_hours=24):
    if currency_symbol is None:
        currency_address = None
    else:
        currency_address = _currency_symbol_to_address(currency_symbol)

    buy_and_sell_topic = "0x9231d8325e00e36dcd9b77484890cc00a0b5b0928605d0a4e6b7fbfeeac4c51b"
    # unstake_topic = "0x204fccf0d92ed8d48f204adb39b2e81e92bad0dedb93f5716ca9478cfb57de00"
    # stake_topic = "0xb4caaf29adda3eefee3ad552a8e85058589bf834c7466cae4ee58787f70589ed"
    token_volumes = defaultdict(int)
    current_eth_block = web3.eth.blockNumber
    router = web3.eth.contract(address=_VETHER_ROUTER_ADDRESS, abi=router_vether_abi)

    for event in web3.eth.getLogs({
            'fromBlock': current_eth_block - (int(60 * 60 * num_hours / _SECONDS_PER_ETH_BLOCK)),
            'toBlock': current_eth_block - 1,
            'address': _VETHER_ROUTER_ADDRESS}):
        topic0 = web3.toHex(event['topics'][0])
        if topic0 == buy_and_sell_topic:
            # print('swap in tx', web3.toHex(event['transactionHash']))
            receipt = web3.eth.getTransactionReceipt(event['transactionHash'])
            parsed_logs = router.events.Swapped().processReceipt(receipt)

            correct_log = None
            for log in parsed_logs:
                if log.address.lower() == router.address.lower():
                    correct_log = log
            if correct_log is None:
                print('bad swap transaction {}'.format(web3.toHex(event['transactionHash'])))
                continue

            inputAmount = float(correct_log.args.inputAmount)
            outputAmount = float(correct_log.args.outputAmount)
            tokenFrom = correct_log.args.tokenFrom
            tokenTo = correct_log.args.tokenTo
            # fee = float(correct_log.args.fee)

            # check if we are filtering by a particular pair
            if currency_address:
                # filter by a particular pool
                if (tokenFrom.lower() == currency_address.lower()
                        or tokenTo.lower() == currency_address.lower()):
                    token_volumes[tokenFrom] += inputAmount
                    token_volumes[tokenTo] += outputAmount
            else:
                # no filter; count volume across all pairs
                token_volumes[tokenFrom] += inputAmount
                token_volumes[tokenTo] += outputAmount

            # print(f"swap {inputAmount} of {tokenFrom} for {outputAmount} of {tokenTo}")
        else:
            # we only care about swaps, so ignore all else
            continue
            # logging.debug('unknown topic txhash {}'.format(web3.toHex(event['transactionHash'])))
            # logging.debug('unknown topic topic0 {}'.format(topic0))

    for token_address in token_volumes.keys():
        if token_address == "0x0000000000000000000000000000000000000000":
            decimals = 18
        else:
            token = web3.eth.contract(address=token_address, abi=erc20_abi)
            decimals = token.functions.decimals().call()
        token_volumes[token_address] /= 10**decimals
    return token_volumes

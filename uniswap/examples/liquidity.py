from typing import List

from web3 import Web3

from uniswap import Uniswap
from uniswap.types import AddressLike

address = Web3.toChecksumAddress("0x6Dc984c9bEd938F139CF4C89709c732EF34B3048")         # or None if you're not going to make transactions
private_key = "3bf1feeb9096db62f233631979749ee8e2e228b0dc593add4e11b4c98aadbb1d"  # or None if you're not going to make transactions
version = 3                       # specify which version of Uniswap to use
provider = "https://ropsten.infura.io/v3/4dbf951c82784ad4a9bda51af0a7e825"    # can also be set through the environment variable `PROVIDER`
uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider)

# Some token addresses we'll be using later in this guide
eth = Web3.toChecksumAddress("0x0000000000000000000000000000000000000000")
ins = Web3.toChecksumAddress("0x7e94f2be613c6846c40325b0f2712269a0d61d10")
dai = Web3.toChecksumAddress("0x31F42841c2db5173425b5223809CF3A38FEde360")

t1 = Web3.toChecksumAddress("0xaD6D458402F60fD3Bd25163575031ACDce07538D")
t2 = Web3.toChecksumAddress("0xc778417E063141139Fce010982780140Aa0cD5Ab")
recipient = Web3.toChecksumAddress("0x6Dc984c9bEd938F139CF4C89709c732EF34B3048")

def start():
#    uniswap.approve(ins, 1*10**9)
#    uniswap.approve(dai, 1*10**17)
#    result = uniswap.add_liquidity_v3(t1, dai, 10000, 10**7)
    #result = uniswap.deposit_liquidity_v3(dai, ins, 3000, 10**17, 1*10**9)
    #result = uniswap.deposit_liquidity_v3(t1, t2, 10000, -60400, -56000, 1*10**18, 0*10**8, 0, 0, recipient)
    #print(result)
    result = uniswap.decrease_liquidity_v3(11140, 2*10**17, 0, 0)
    print(result)
    #s= '-\xd6qM\xf0\xbe\x92L\xf2D\xbb\xadq[P\xe58\xa4\xd4\x0bjd%\xa9b \xf1r^1\xebH'.encode('utf-8')
    #print(s.hex())

if __name__ == "__main__":
#    usdt_to_vxv_v2()
    start()

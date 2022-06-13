from enum import Enum


class Currency_Info_Dic():

    get = {
        "ETH" : {
            "name": "Ethereum",
            "token_address": "",
            "decimals": 18,
            "quantum": "100000000"
        },
        "GODS" : {
            "name": "Gods Unchained",
            "token_address": "0xccc8cb5229b0ac8069c51fd58367fd1e622afd97",
            "decimals": 18,
            "quantum": "100000000"
        },
        "GOG" : {
            "name": "Guild Of Guardians Token",
            "token_address": "0x9ab7bb7fdc60f4357ecfef43986818a2a3569c62",
            "decimals": 18,
            "quantum": "100000000"
        },
        "IMX" : {
            "name": "Immutable X",
            "token_address": "0xf57e7e7c23978c3caec3c3548e3d615c346e79ff",
            "decimals": 18,
            "quantum": "100000000"
        },
        "OMI" : {
            "name": "OMI Token",
            "token_address": "0xed35af169af46a02ee13b9d79eb57d6d68c1749e",
            "decimals": 18,
            "quantum": "100000000000"
        },
        "USDC" : {
            "name": "USD Coin",
            "token_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            "decimals": 6,
            "quantum": "1"
        }
    }


class Currency(Enum):
    ETH = 1
    GODS = 2
    IMX = 3
    USDC = 4
    GOG = 5
    OMI = 6


    # eth_token_address = ""                                                token_type = ETH
    # gods_token_address = 0xccc8cb5229b0ac8069c51fd58367fd1e622afd97       token_type = ERC20
    # imx_token_address = 0xf57e7e7c23978c3caec3c3548e3d615c346e79ff        token_type = ERC20
    # usdc_token_address = 0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48       token_type = ERC20
    # guild_of_guardians = 0x9ab7bb7fdc60f4357ecfef43986818a2a3569c62       token_type = ERC20
    # omi_address = 0xed35af169af46a02ee13b9d79eb57d6d68c1749e              token_type = ERC20

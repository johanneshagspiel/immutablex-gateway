<img src=img/imx_gateway.JPG alt="IMX Gateway Logo" width="470" height="148">

--------------------------------------------------------------------------------
[![MIT-License](https://img.shields.io/github/license/johanneshagspiel/immutablex-gateway)](LICENSE)
[![Top Language](https://img.shields.io/github/languages/top/johanneshagspiel/immutablex-gateway)](https://github.com/johanneshagspiel/immutablex-gateway)
[![Latest Release](https://img.shields.io/github/v/release/johanneshagspiel/immutablex-gateway)](https://github.com/johanneshagspiel/immutablex-gateway/releases/)

# Immutable X Gateway

"Immutable X Gateway" is program created in order to engage more easily with the "Immutable X" API. 

["Immutable X"](https://www.immutable.com/) is a layer 2 protocol on the Ethereum blockchain that enables the user to trade NFTs instantaneously, with zero gas fees and in a carbon-neutral way. It also has an [open REST API](https://docs.x.immutable.com/reference) that empowers the user to programmatically interact with the blockchain to, for example look up all available sell orders for a particular NFT or create a trade. 
The "Immutable X Gateway" allows the user to engage with this open API in an easy, automated way.

## Features

With the "Immutable X Gateway", the user can:
- download all orders associated with an NFT that is listed on "Immutable X"
  - for the NFT "Gods Unchained", the "Immutable X Gateway" also download past games as well as the rank associated with the players of those games
- process this data to generate various kinds of information such as:
  - an up-to-date overview the cheapest price in the various crypto currencies that a NFT is available 
  - a historical overview over past sales of a particular NFT in terms of a variety of factors such as price, sales volume or price changes
  - for the NFT "Gods Unchained", the win rate of a particular card is calculated, for all ranks as well as the mythic rank
  - determine which users are employing bots through outlier detection 
- this information is then combined into one csv file that outlines whether arbitrage opportunities exist when one NFT is listed in different crypto currencies
- make automatic trades based on custom paramters to take advantage of these arbitrage opportunities

All of these tasks are parallelized and thus once all orders up to the current moment have been downloaded, then from that moment onwards the "Immutable X Gateway" batch processes all new orders as soon as they come in.

<img src=img/example_information_overview.png alt="Example Information Overview" width="896" height="493">

## Tools

| Purpose                | Name                                                         |
|------------------------|--------------------------------------------------------------|
| Programming language   | [Python 3.10](https://www.python.org/)                       |
| Dependency manager     | [Pipenv](https://pipenv.pypa.io/en/latest/)                  |
| Version control system | [Git](https://git-scm.com/)                                  |
| Testing framework      | [unittest](https://docs.python.org/3/library/unittest.html/) |
| IMX SDK 		             | [imxpy](https://github.com/Dimfred/imxpy/)   |

## Requirements

As of this writing, requests to the API are sent whenever they arise. For this reason the request limit per seconds as set by "Immutable X" frequently is hit. To overcome this limitation, the "Immutable X Gateway" assumes that the user has installed NordVPN so that the program can switch to a new server. Thus, the "Immutable X Gateway" currently requires the user to have an active subscription with NordVPN to be used.   

## Installation Process

If you want to import this project and resolve all the dependencies associated with it, it is assumed that you have installed [Python 3.10](https://www.python.org/downloads/windows/) as well as the [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/index.html) dependency manager and that your operating system is Windows.
To download all the dependencies, simply open this repository in a terminal and type

	pipenv install

The python wrapper for the IMX SDK, imxpy, is as of this writing, not on official package on pypi. Therefore, one has to clone the Github repository for that. First, move into the associated directory:

    cd src/util

In case there already is a folder called imxpy in this directory, delete it. Now clone [imxpy](https://github.com/Dimfred/imxpy/) via:

    git clone https://github.com/Dimfred/imxpy.git

Because the original IMX SDK was written in typescript, you also have to install [npm and Node.js](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) as well as [typescript](https://www.npmjs.com/package/typescript). Now you first move into the new imxpy folder:

    cd imxpy

Then install all typescript dependencies with: 

    npm install

Now, build the typescript file through this command:

    tsc

The `resources` directory and all subfolders have to be created via the `File_Handler.create_resources_folders()` command that is in main method at `src/main`. So simply run `main`.

Lastly, user information need to be added at three different locations:

- `resources/client_info/pk_info.json`: here, the users private key of the wallet and address of users account on the "Immutable X" blockchain need to be added so that the user can create trades through the IMX SDK
- `resources/client_info/coinapi_info_file.json`: here, the user needs to add an api key obtained from [CoinAPI](https://www.coinapi.io/pricing) so that the latest price changes can be obtained
- `resources/client_info/coinmarketcap_info.json`: here, the user needs to add an api key obtained from [CoinMarketCap](https://coinmarketcap.com/api/) so that historical price changes can be obtained

## Licence

The "Immutable X Gateway" is published under the MIT licence, which can be found in the [LICENSE](LICENSE) file.

## References

The base image for the logo was taken from the [official Immutable X website](https://assets-global.website-files.com/5f7eec37ff782e797edabe11/60e443ed35f546d0d2ede08f_logo-main-p-500.png).

## Disclaimer

This is not an official "Immutable X" programme nor is it endorsed by "Immutable X". Use it at your own risk. Particularly when it comes to the auto-trader functionality, no responsibility is assumed for any damage incurred.
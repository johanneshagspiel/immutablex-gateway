import time

from src.util.imxpy.imx_client import IMXClient
from src.util.imxpy.imx_objects import TransferParams, ERC20


class TestClient:

    @staticmethod
    def transfer_one_god_token(sender_pk, sender_address, receiver_address):

        transfer_card = ERC20(contract_addr="0xccc8cb5229b0ac8069c51fd58367fd1e622afd97",)

        transfer_params = TransferParams(sender=sender_address, receiver=receiver_address,
                                         token=transfer_card)

        imx_client = IMXClient(net="main", n_workers=32, pk=sender_pk)

        future = imx_client.transfer(transfer_params)

        while future.running():
            time.sleep(1)

        print(future.result())

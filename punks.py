from threading import Thread
import time
import json
from web3 import Web3, HTTPProvider
import asyncio
import urllib.request
import os


use_testnet = False
api_base = 'https://forgottenpunks-staging.vercel.app' if use_testnet else 'https://forgottenpunks.wtf'
eth_network = "goerli" if use_testnet else "mainnet"


class WebClient(object):
    @staticmethod
    def download(url, target, cache=True):
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if not os.path.exists(target) or not cache:
            try:
                urllib.request.urlretrieve(url, target)
            except:
                return None
        return target

    @staticmethod
    def get_json(url):
        with urllib.request.urlopen(url) as response:
            try:
                return json.loads(response.read())
            except:
                    return None


class ForgottenPunks(object):
    class Router(object):
        @staticmethod
        def meta_url(token_id):
            return "{}/api/meta/{}".format(api_base, token_id)

        @staticmethod
        def img_url(token_id):
            return "{}/api/img/{}".format(api_base, token_id)

    @staticmethod
    def get_meta(token_id):
        return WebClient.get_json(ForgottenPunks.Router.meta_url(token_id))

    @staticmethod
    def get_image(token_id, refresh=False):
        target = "{}/artwork/punks/{}.png".format(os.getcwd(), token_id)
        return WebClient.download(ForgottenPunks.Router.img_url(token_id), target)


    class Observer(object):
        abi_json = """
        [
            {
            "anonymous": false,
            "inputs": [
                {
                "indexed": true,
                "internalType": "address",
                "name": "from",
                "type": "address"
                },
                {
                "indexed": true,
                "internalType": "address",
                "name": "to",
                "type": "address"
                },
                {
                "indexed": true,
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
                }
            ],
            "name": "Transfer",
            "type": "event"
            }
        ]
        """
        contract = '0x4Ee75fC34F7c5b3dFAF53e74D22a83405686a9A3' if use_testnet else '0x4adDAc15971AB60Ead954B8F15a67518730450e0'

        def __init__(self, bot):
            self.bot = bot
            self.w3 = Web3(Web3.HTTPProvider('https://{}.infura.io/v3/84cf06de26f042d3be02fd0ee1cc7ba6'.format(eth_network)))
            self.contract = self.w3.eth.contract(address=ForgottenPunks.Observer.contract, abi=json.loads(ForgottenPunks.Observer.abi_json))
            self.worker = None

        def handle_event(self, event):
            try:
                from_addr = event['args']['from']
                # Ignore non-mint transfers
                if from_addr != "0x0000000000000000000000000000000000000000":
                    return
                to_addr = event['args']['to']
                token_id = event['args']['tokenId']
                if self.bot is not None:
                    self.bot.on_forgottenpunk_minted(token_id, to_addr)
                else:
                    print("Mint: ForgottenPunks #{} to {}".format(token_id, to_addr))
            except Exception as e:
                print(e)

        def log_loop(self, event_filter, poll_interval, check_history):
                # get old events if we're testing
                if check_history:
                    try:
                        for event in event_filter.get_all_entries():
                            self.handle_event(event)
                    except:
                        pass
                while True:
                    try:
                        for event in event_filter.get_new_entries():
                            self.handle_event(event)
                    except:
                        pass
                    time.sleep(poll_interval)

        def start_worker(self):
            if self.worker is None:
                block_filter = self.contract.events.Transfer.createFilter(fromBlock=0 if use_testnet else 'latest', toBlock='latest')
                self.worker = Thread(target=ForgottenPunks.Observer.log_loop, args=(self, block_filter, 10, use_testnet), daemon=True)
                self.worker.start()
            else:
                print("Attempting to start worker that is already running, ignored.")



################################################################################

async def main():
    # Test fetching resources
    print(ForgottenPunks.get_meta(3))
    print(ForgottenPunks.get_image(3))

    # Test observing on-chain events
    obv = ForgottenPunks.Observer(None)
    obv.start_worker()
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

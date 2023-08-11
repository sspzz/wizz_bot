
from threading import Thread
import time
import json
from web3 import Web3, HTTPProvider
import asyncio
import urllib.request
import requests
import os


use_testnet = False
api_base = 'https://quantum-portal-git-goerli-forgottenrunes.vercel.app' if use_testnet else 'https://portal.forgottenrunes.com'
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


class WeaponForge(object):
    class Router(object):
        @staticmethod
        def warrior_meta_url(token_id):
            return "{}/api/warriors/data/{}".format(api_base, token_id)

        @staticmethod
        def lock_url(token_id):
            return "{}/api/locks/img/{}".format('https://portal.forgottenrunes.com', token_id)

        @staticmethod
        def treat_url(token_id):
            return "{}/api/treats/img/{}".format('https://portal.forgottenrunes.com', token_id)

        @staticmethod
        def warrior_url(token_id):
            return "{}/api/warriors/img/{}".format(api_base, token_id)

        @staticmethod
        def weapon_url(token_id):
            return "{}/api/warriors/img/{}/forged-weapon".format(api_base, token_id)


    @staticmethod
    def get_warrior_meta(token_id):
        return WebClient.get_json(WeaponForge.Router.warrior_meta_url(token_id))

    @staticmethod
    def get_warrior(token_id, refresh=False):
        # if WeaponForge.get_forged_weapon(token_id) is not None:
        target = "{}/artwork/warriors-forge/{}.gif".format(os.getcwd(), token_id)
        return WebClient.download(WeaponForge.Router.warrior_url(token_id), target)

    @staticmethod
    def get_forged_weapon(token_id, refresh=False):
        target = "{}/artwork/warriors-forge/{}-weapon.gif".format(os.getcwd(), token_id)
        return WebClient.download(WeaponForge.Router.weapon_url(token_id), target)

    @staticmethod
    def get_lock(token_id, refresh=False):
        target = "{}/artwork/locks/{}.png".format(os.getcwd(), token_id)
        return WebClient.download(WeaponForge.Router.lock_url(token_id), target)

    class Observer(object):
        abi_json = """
        [
            {
              "anonymous": false,
              "inputs": [
                {
                  "indexed": true,
                  "internalType": "uint256",
                  "name": "warriorId",
                  "type": "uint256"
                },
                {
                  "indexed": false,
                  "internalType": "address",
                  "name": "burnableAddress",
                  "type": "address"
                },
                {
                  "indexed": false,
                  "internalType": "uint256",
                  "name": "burnableTokenId",
                  "type": "uint256"
                }
              ],
              "name": "WarriorWeaponForged",
              "type": "event"
            }
        ]
        """
        contract = '0xfBA35cec34BAF299B693f86D9eb851BcCBf34D29' if use_testnet else '0x2AA0Ad11Ab37d93f1189b2c5Ac2285AC8f6D4b68'

        def __init__(self, bot):
            self.bot = bot
            self.w3 = Web3(Web3.HTTPProvider('https://{}.infura.io/v3/84cf06de26f042d3be02fd0ee1cc7ba6'.format(eth_network)))
            self.forgeContract = self.w3.eth.contract(address=WeaponForge.Observer.contract, abi=json.loads(WeaponForge.Observer.abi_json))
            self.worker = None

        def handle_event(self, event):
            try:
                token_id = event['args']['warriorId']
                lock_id = event['args']['burnableTokenId']
                if self.bot is not None:
                    self.bot.on_warrior_weapon_forged(token_id, lock_id)
                else:
                    print("Forge event: Warrior #{}, Lock #{}".format(token_id, lock_id))
            except Exception as e:
                print(e)

        def log_loop(self, event_filter, poll_interval, check_history):
            try:
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
            except:
                pass

        def start_worker(self):
            if self.worker is None:
                block_filter = self.forgeContract.events.WarriorWeaponForged.createFilter(fromBlock=0 if use_testnet else 16176368, toBlock='latest')
                self.worker = Thread(target=WeaponForge.Observer.log_loop, args=(self, block_filter, 10, use_testnet), daemon=True)
                self.worker.start()
            else:
                print("Attempting to start worker that is already running, ignored.")



################################################################################

async def main():
    # Test fetching resources
    print(WeaponForge.get_warrior_meta(3))
    print(WeaponForge.get_warrior(3))
    print(WeaponForge.get_forged_weapon(3))
    print(WeaponForge.get_lock(0))

    # Test observing on-chain events
    obv = WeaponForge.Observer(None)
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

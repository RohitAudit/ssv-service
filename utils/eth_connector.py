from web3 import Web3
from web3.gas_strategies.rpc import rpc_gas_price_strategy
import web3


class EthNode:
    account = None
    eth_node = None
    local = False

    def __init__(self, rpc_url, private_key):
        self.eth_node = Web3(Web3.HTTPProvider(rpc_url))
        self.eth_node.eth.set_gas_price_strategy(rpc_gas_price_strategy)
        if '127.0.0.1' or 'localhost' in rpc_url:
            # w3.eth.accounts()[0]
            self.local = True
        else:
            pass
        self.account = self.eth_node.eth.account.privateKeyToAccount(
            private_key)


    def make_tx(self, tx):
        # self.eth_node.eth.call(tx)
        tx['nonce'] = self.eth_node.eth.get_transaction_count( self.account.address)
        if self.local:
            # tx.pop('maxPriorityFeePerGas')
            tx.pop('maxFeePerGas')
        signed_tx = self.eth_node.eth.account.sign_transaction(
            tx, self.account.key)
        tx_hash = self.eth_node.eth.send_raw_transaction(
            signed_tx.rawTransaction)
        tx_receipt = self.eth_node.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt.status == 1:
            print('TX successful')
            return True
        else:
            print('TX reverted')
            return False

    def get_balance(self, address):
        return self.eth_node.eth.get_balance(address) / 10 ** 18

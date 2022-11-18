from web3 import Web3


class SSVNetwork:
    abi = [{
        "inputs": [],
        "name": "getNetworkFee",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }]
    contract = None

    def __init__(self, ssv_address, web3: Web3):
        self.contract = web3.eth.contract(abi=self.abi, address=ssv_address)

    def get_network_fee(self):
        return self.contract.functions.getNetworkFee().call()


class SSVToken:
    abi = [{
        "inputs": [
            {
                "internalType": "address",
                "name": "account",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }, {
        "inputs": [
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
    ]

    def __init__(self, ssv_address, web3: Web3):
        self.contract = web3.eth.contract(abi=self.abi, address=ssv_address)

    def get_balance(self, account_address):
        return self.contract.functions.balanceOf(account_address).call()

    def transfer_token(self, address, amount, account_address):
        return self.contract.functions.transfer(address, amount).buildTransaction({"from": account_address})

from web3 import Web3


class StakingPool:
    abi = [{
        "inputs": [],
        "name": "WITHDRAWAL_ADDRESS",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }, {
        "inputs": [
            {
                "internalType": "bytes",
                "name": "pubkey",
                "type": "bytes"
            },
            {
                "internalType": "bytes",
                "name": "withdrawal_credentials",
                "type": "bytes"
            },
            {
                "internalType": "bytes",
                "name": "signature",
                "type": "bytes"
            },
            {
                "internalType": "bytes32",
                "name": "deposit_data_root",
                "type": "bytes32"
            }
        ],
        "name": "depositValidator",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }, {
        "inputs": [],
        "name": "getOperators",
        "outputs": [
            {
                "internalType": "uint256[4]",
                "name": "",
                "type": "uint256[4]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }, {
        "inputs": [
            {
                "internalType": "bytes",
                "name": "pubkey",
                "type": "bytes"
            },
            {
                "internalType": "uint32[]",
                "name": "operatorIds",
                "type": "uint32[]"
            },
            {
                "internalType": "bytes[]",
                "name": "sharesPublicKeys",
                "type": "bytes[]"
            },
            {
                "internalType": "bytes[]",
                "name": "sharesEncrypted",
                "type": "bytes[]"
            },
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "depositShares",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }]

    contract = None

    def __init__(self, stakepool_contract, web3: Web3):
        """

        :param keysmanager_address:
        """
        self.contract = web3.eth.contract(address=stakepool_contract, abi=self.abi)

    def get_withdrawal_address(self):
        return self.contract.functions.WITHDRAWAL_ADDRESS().call()

    def deposit_validator(self, pubkey, withdrawal_creds, signature, deposit_data_root, account_address):
        return self.contract.functions.depositValidator(pubkey, withdrawal_creds, signature,
                                                        deposit_data_root).buildTransaction({"from": account_address})

    def get_operator_ids(self):
        """

        :return:
        """
        return self.contract.functions.getOperators().call()

    def send_key_shares(self, pubkey, operator_ids, sharesPublicKeys, sharesEncrypted, amount, account_address):
        """

        :return:
        """
        print("=================================\n")
        print(pubkey)
        print("=================================\n")

        print(operator_ids)
        print("=================================\n")

        print(sharesPublicKeys)
        print("=================================\n")

        print(sharesEncrypted)
        print("=================================\n")

        print(amount)
        return self.contract.functions.depositShares(pubkey, operator_ids, sharesPublicKeys, sharesEncrypted,
                                                             amount).buildTransaction({"from": account_address})


if __name__ == '__main__':
    web3_eth = Web3(Web3.HTTPProvider("http://localhost:8545"))
    st = StakingPool("0xc351628EB244ec633d5f21fBD6621e1a683B1181", web3_eth)
    print(st.get_operator_ids())

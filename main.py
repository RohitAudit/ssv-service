import json
from collections import namedtuple
from eth_typing import HexAddress, HexStr
from ssv.ssv_cli import SSV, OperatorData
from staking_deposit.settings import GOERLI, Zheijang
from staking_deposit.key_handling.key_derivation.mnemonic import get_mnemonic
from staking_deposit.utils.constants import WORD_LISTS_PATH
import argparse
import time
from utils.eth_connector import EthNode
from utils.stakepool import StakingPool
from utils.ssv_network import SSVNetwork, SSVToken
import traceback
from staking_deposit.validator_key import ValidatorKey, DepositData
from ssv.ssv_cli import Operator


def read_file(file_path):
    """
    This is used to read params from json file and convert them to python Namespaces
    :param file_path: takes the json filepath
    :returns: it returns data in form of python Namespace
    """
    with open(file_path, "r") as file:
        data = json.load(file, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    file.close()
    return data


def create_keys(config_file):
    """
    This is an entry function for command line argument create-keys.
    It is used to create multiple validator keys and their deposit data.

    :param config_file: Refer sample_config(validator-config.json) folder for config file params
    :return: Null
    """
    config = read_file(config_file)
    validators = ValidatorKey()
    mnemonic = get_mnemonic(language="english", words_path=WORD_LISTS_PATH)
    keystores, deposit_data = validators.generate_keys(mnemonic, 0, config.validator_count, "", Zheijang,
                                                       config.keystore_password, config.withdrawal_creds)
    print("mnemonic used to generate validator keys:")
    print(mnemonic)
    print("Keystore files generated for your validators are:")
    print(keystores)
    print("deposit data for your validator keys are:")
    print(deposit_data)


def create_keyshares(config_file):
    """
    This is an entry function for command line argument generate-keyshares.
    It is used to create ssv keyshares for given validator keystores.

    :param config_file: Refer sample_config(keyshare-config.json) folder for config file params
    :return: Null
    """
    config = read_file(config_file)
    operators = [Operator(operator_data.id, operator_data.pubkey, operator_data.fee, operator_data.name) for
                 operator_data in config.operators]
    for keystore in config.keystore_files:
        ssv = SSV(keystore, config.keystore_password)
        keyshare_file = ssv.generate_shares(operators, config.ssv_fee)
        print("for following keystore file: {} \n keyshare generated is:{}".format(keystore, keyshare_file))


def deposit_keyshare(config_file):
    """
    This is an entry function for command line argument deposit-keyshares.
    It is used to submit keyshares to stakepool contract.

    :param config_file: Refer sample_config(deposit-keyshare.json) folder for config file params
    :return: Null
    """
    config = read_file(config_file)
    web3_eth = EthNode(config.eth.rpc, config.eth.priv_key)
    ssv_token = SSVToken(config.ssv_token, web3_eth.eth_node)
    stake_pool = StakingPool(config.stakepool_contract, web3_eth.eth_node)
    print(ssv_token.get_balance(web3_eth.eth_node.toChecksumAddress(config.stakepool_contract)))
    for file in config.keyshares:
        shares = read_file(file)
        if ssv_token.get_balance(web3_eth.eth_node.toChecksumAddress(config.stakepool_contract)) < int(
                shares.payload.readable.ssvAmount):
            print("ssv token balance of stakepool is less than the required amount. Sending some tokens")
            if ssv_token.get_balance(
                    web3_eth.eth_node.toChecksumAddress(web3_eth.account.address)) > 2 * int(
                shares.payload.readable.ssvAmount):
                tx = ssv_token.transfer_token(web3_eth.eth_node.toChecksumAddress(config.stakepool_contract),
                                              2 * int(shares.payload.readable.ssvAmount), web3_eth.account.address)
                web3_eth.make_tx(tx)
                print("Added SSV tokens to stakepool account")
            elif ssv_token.get_balance(web3_eth.eth_node.toChecksumAddress(web3_eth.account.address)) > int(
                    shares.payload.readable.ssvAmount):
                tx = ssv_token.transfer_token(web3_eth.eth_node.toChecksumAddress(config.contract_address.stakepool),
                                              int(shares.payload.readable.ssvAmount), web3_eth.account.address)
                web3_eth.make_tx(tx)
                print(
                    "WARNING!!!! Balance too low for account and stakepool for SSV tokens. Please add some")
            else:
                raise Exception(
                    "ERROR!!!! keys shares not added as your account doesn't have enough SSV tokens")
        operator_ids = [operator.id for operator in shares.data.operators]
        tx = stake_pool.send_key_shares(shares.payload.readable.validatorPublicKey, operator_ids,
                                        shares.payload.readable.sharePublicKeys,
                                        shares.payload.readable.sharePrivateKey,
                                        int(shares.payload.readable.ssvAmount),
                                        web3_eth.account.address)
        web3_eth.make_tx(tx)
        print("ssv shares submitted to the contract")


def deposit_validator(config_file):
    """
    This is an entry function for command line argument deposit-validator.
    It is used to submit validator to stakepool contract.

    :param config_file: Refer sample_config(deposit-validator.json) folder for config file params
    :return: Null
    """
    config = read_file(config_file)
    deposit_file = read_file(config.deposit_file)
    deposit_data = [DepositData(key.pubkey, key.withdrawal_credentials, key.signature, key.deposit_data_root) for key in
                    deposit_file]
    web3_eth = EthNode(config.eth.rpc, config.eth.priv_key)
    stake_pool = StakingPool(config.deposit_contract, web3_eth.eth_node)
    for deposit in deposit_data:
        print(deposit)
        tx = stake_pool.deposit_validator(deposit.pubkey,
                                          deposit.withdrawal_credentials,
                                          deposit.signature,
                                          deposit.deposit_data_root,
                                          web3_eth.account.address)
        if web3_eth.make_tx(tx):
            print("key deposited for validator: {}".format(deposit.pubkey))
        else:
            print("key deposit failed for validator: {}".format(deposit.pubkey))


def start_staking(config_file):
    """
    This is an entry function for command line argument stake.
    Following are the actions performed by it:
    [1] It is used to run the backend for stakepool contract.
    [2] It regularly monitors the balances of the stakepool contract and submits keys and keyshares.
    [3] It also monitors the balance of SSV token in the stakepool contract and sends some SSV token from whitelist address
    [4] In the case of script failure it creates a fallabck file which stores the state of the system. Upon resuming the
     service it
    :param config_file: Refer sample_config(stake-config.json) folder for config file params
    :return: Null
    """
    config = read_file(config_file)
    while True:
        mnemonic = get_mnemonic(language="english", words_path=WORD_LISTS_PATH)  # mnemonic
        web3_eth = EthNode(config.eth.rpc, config.eth.priv_key)
        if web3_eth.get_balance(config.contract_address.stakepool) >= 32:
            stake_pool = StakingPool(config.contract_address.stakepool, web3_eth.eth_node)
            print("balance of staking pool:" + str(web3_eth.get_balance(config.contract_address.stakepool)))
            num_validators = int(web3_eth.get_balance(config.contract_address.stakepool) / 32)
            print("creating validators")
            validators = ValidatorKey()
            keystores, deposit_file = validators.generate_keys(mnemonic=mnemonic, validator_start_index=1,
                                                               num_validators=num_validators, folder="",
                                                               chain=GOERLI,
                                                               keystore_password=config.keystore_pass,
                                                               eth1_withdrawal_address=HexAddress(
                                                                   HexStr(config.contract_address.withdrawal_contract)))
            print("keys created are:\n")
            print(keystores)
            print("submitting validators")
            for index, cred in enumerate(validators.get_deposit_data(deposit_file)):
                tx = stake_pool.deposit_validator(cred.pubkey,
                                                  cred.withdrawal_credentials,
                                                  cred.signature,
                                                  cred.deposit_data_root,
                                                  web3_eth.account.address)
                web3_eth.make_tx(tx)
                print("deposit the key" + str(cred.pubkey))
            print("submitted validators\n")
            operator_id = config.operator_id
            print("operator ids are:\n")
            print(operator_id)
            ssv_contract = SSVNetwork(config.contract_address.ssv_network, web3_eth.eth_node)
            ssv_token = SSVToken(config.contract_address.ssv_token, web3_eth.eth_node)
            operators = [ssv_contract.get_operator(id) for id in operator_id]
            op = [Operator(operator[3], operator[0], operator[1], operator[2]) for operator in operators]
            network_fees = 0 if ssv_contract.get_network_fee() is None else ssv_contract.get_network_fee()
            print("network fee is:\n")
            print(network_fees)
            for keystore in keystores:
                ssv = SSV(keystore, config.keystore_pass)
                file = ssv.generate_shares(op, network_fees)
                print(file)
                shares = ssv.get_keyshare(file)
                print("approve ssv network to take ssv token fee")
                tx_token = ssv_token.approve(config.contract_address.ssv_network, int(shares["ssvAmount"]),
                                             web3_eth.account.address)
                web3_eth.make_tx(tx_token)
                print("submit the ssv shares")
                tx = ssv_contract.register_validator(shares["validatorPublicKey"], operator_id,
                                                     shares["sharePublicKeys"], shares["sharePrivateKey"],
                                                     int(shares["ssvAmount"]),
                                                     web3_eth.account.address)
                web3_eth.make_tx(tx)
                print("ssv shares submitted to the contract")
        else:
            print("pool balance less than 32")
            time.sleep(10)
            print("trying again")


if __name__ == '__main__':
    """
    Command line parser that acts on the command passed to it
    """
    parser = argparse.ArgumentParser(description="Command line tool for SSV backend")
    subparses = parser.add_subparsers()
    stake = subparses.add_parser("stake",
                                 help="used to start a service that tracks stakinpool contract for keys and key shares")
    stake.set_defaults(which="stake")

    stake.add_argument("-c", "--config",
                       help="pass a config file with required params. Ex: sample_config/stake-config.json",
                       required=True)
    args = parser.parse_args()
    if args.which == "stake":
        start_staking(args.config)

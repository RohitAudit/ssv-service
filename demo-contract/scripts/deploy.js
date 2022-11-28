const {ethers, upgrades} = require("hardhat");

async function main() {
    const RoEth = await ethers.getContractFactory("RoEth");
    const Common = await ethers.getContractFactory("Common");
    // const KeysManager = await ethers.getContractFactory("KeysManager");
    const StakingPool = await ethers.getContractFactory("StakingPool");
    const operator_ids = [1, 2, 9, 42]
    const whitelist = "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65"
    const withdrawal_creds = "0xfabb0ac9d68b0b445fb7357272ff202c5651694a"
    const deposit_contract = "0x0DCd1Bf9A1b36cE34237eEaFef220932846BCD82"
    const ssv_network_contract = "0xA51c1fc2f0D1a1b8494Ed1FE312d7C3a78Ed91C0"
    const ssv_token_address = "0x610178dA211FEF7D417bC0e6FeD39F05609AD788"
    const oracle_address = "0xfabb0ac9d68b0b445fb7357272ff202c5651694a"
    const common = await Common.deploy();
    console.log("Common contract deployed to:", common.address)
    const roETH = await RoEth.deploy(common.address);
    // const roETH = await RoEth.attach("0x7a2088a1bFc9d81c55368AE168C2C02570cB814F");

    console.log("roETH deployed to:", roETH.address)
    const stakingpool = await StakingPool.deploy(whitelist, deposit_contract, common.address, withdrawal_creds, ssv_network_contract, ssv_token_address, operator_ids);
    console.log("staking pool deployed to:", stakingpool.address)
    tx = await roETH.setMinter(stakingpool.address);
    await tx.wait()
    console.log("adding values in common contract")
    tx = await common.changeStakingPool(stakingpool.address);
    await tx.wait();
    tx = await common.changeRoETH(roETH.address);
    await tx.wait();

    tx = await common.changeOracle(oracle_address);
    await tx.wait();


    console.log("added values in common contract");
    console.log(await common.getAdmin());


}

main()
    .then(() => process.exit(0))
    .catch(error => {
        console.error(error);
        process.exit(1);
    });
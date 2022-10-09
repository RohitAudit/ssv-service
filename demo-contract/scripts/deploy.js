const {ethers, upgrades} = require("hardhat");

async function main() {
    const RoEth = await ethers.getContractFactory("RoEth");
    const Common = await ethers.getContractFactory("Common");
    const KeysManager = await ethers.getContractFactory("KeysManager");
    const StakingPool = await ethers.getContractFactory("StakingPool");

    const common = await Common.deploy();
    console.log("Common contract deployed to:", common.address)
    const roETH = await RoEth.deploy(common.address);
    // const roETH = await RoEth.attach("0x7a2088a1bFc9d81c55368AE168C2C02570cB814F");

    console.log("roETH deployed to:", roETH.address)
    const stakingpool = await StakingPool.deploy("0xe7BB7b66d77E25656049e28638Df481c6D84072b", "0xff50ed3d0ec03ac01d4c79aad74928bff48a7b2b", common.address, "0xfabb0ac9d68b0b445fb7357272ff202c5651694a");
    console.log("staking pool deployed to:", stakingpool.address)
    const keymanager = await KeysManager.deploy("0xb9e155e65B5c4D66df28Da8E9a0957f06F11Bc04", "0x3a9f01091C446bdE031E39ea8354647AFef091E7", "0xe7BB7b66d77E25656049e28638Df481c6D84072b", [1, 2, 9, 42])
    // const keymanager = await KeysManager.attach("0xc5a5C42992dECbae36851359345FE25997F5C42d")
    console.log("keysmanager deployed to:", keymanager.address)
    // console.log(await keymanager.getOperators())

    tx = await roETH.setMinter(stakingpool.address);
    await tx.wait()
    console.log("adding values in common contract")
    tx = await common.changeStakingPool(stakingpool.address);
    await tx.wait();
    tx = await common.changeRoETH(roETH.address);
    await tx.wait();

    tx = await common.changeOracle("0xfabb0ac9d68b0b445fb7357272ff202c5651694a");
    await tx.wait();

    tx = await common.changeKeysManager(keymanager.address);
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
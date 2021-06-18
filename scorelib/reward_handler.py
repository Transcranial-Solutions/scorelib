from iconservice import *

class RewardHandler:

    def __init__(self, name: str, rscore_decimals: int, db: IconScoreDatabase, isb: IconScoreBase):
        self._reward_rate = VarDB(f"{name}_sum_reward_rate", db, int)
        self._entry_reward_rate = DictDB(f"{name}_entry_reward_rate", db, int)
        self._rewards = DictDB(f"{name}_rewards", db, int)
        self._rscore_decimals = rscore_decimals
        self._isb = isb

    def distribute_rewards(self, amount: int, total_supply: int):
        reward_rate = self._reward_rate.get()
        if total_supply:
            reward_rate = reward_rate + (self._loop_to_rscore(amount) // total_supply)
            self._reward_rate.set(reward_rate)
        else:
            revert("Total supply is zero.")

    def claim_rewards(self, address: Address):
        rewards = self._rscore_to_loop(self._rewards[address])
        self._isb.icx.transfer(address, rewards)

    def query_rewards(self, address: Address, balance: int) -> int:
        rewards = balance * (self._reward_rate.get() - self._entry_reward_rate[address]) + self._rewards[address]
        return self._rscore_to_loop(rewards)

    def update_rewards(self, address: Address, balance: int):
        rewards = balance * (self._reward_rate.get() - self._entry_reward_rate[address])
        self._rewards[address] += rewards
        self._entry_reward_rate[address] = self._reward_rate.get()

    def _rscore_to_loop(self, rscore: int) -> int:
        return rscore // 10**self._rscore_decimals

    def _loop_to_rscore(self, loop: int) -> int:
        return loop * 10**self._rscore_decimals
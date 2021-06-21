from iconservice import *

class TokenType:
    irc2 = 1
    icx = 2

class RewardHandler:
    """
    Handles distribution, tracking, and claiming of rewards. Both irc2 token rewards and icx rewards are supported.
    Used within the contract that keeps track of eligible balances.
    """

    def __init__(self, name: str, rscore_decimals: int, db: IconScoreDatabase, isb: IconScoreBase, token_type: TokenType = TokenType.irc2):
        self._reward_rate = VarDB(f"{name}_sum_reward_rate", db, int)
        self._entry_reward_rate = DictDB(f"{name}_entry_reward_rate", db, int)
        self._rewards = DictDB(f"{name}_rewards", db, int)
        self._rscore_decimals = rscore_decimals
        self._isb = isb
        self._token_type = token_type

    def distribute_rewards(self, amount: int, total_eligible_supply: int):
        """
        Trigger a reward distribution.

        Parameters:
        amount                 :  Amount of tokens to distribute.
        total_eligible_supply  :  Total amount of tokens eligible for rewards.
        """
        reward_rate = self._reward_rate.get()
        if total_eligible_supply:
            reward_rate = reward_rate + (self._loop_to_rscore(amount) // total_eligible_supply)
            self._reward_rate.set(reward_rate)
        else:
            revert("Total supply is zero.")

    def claim_rewards(self, address: Address, eligible_balance: int):
        """
        Claim rewards.

        Parameters:
        address  :  Address which will claim the rewards.
        eligible_balance  :  Number of tokens, at this point in time, the address has that are eligible for rewards.
        """
        self.update_rewards(address, eligible_balance)
        rewards = self._rscore_to_loop(self._rewards[address])
        if not rewards:
            revert("No rewards to claim.")

        if self._token_type == TokenType.irc2:
            self._isb.mint(address, rewards)
        elif self._token_type == TokenType.icx:
            self._isb.icx.transfer(address, rewards)
        else:
            revert("Tokentype not supported.")

        self._isb.icx.transfer(address, rewards)
        self._rewards[address] -= self._loop_to_rscore(rewards)

    def query_rewards(self, address: Address, eligible_balance: int) -> int:
        """
        Query the rewards avaiable for this address to claim.

        Parameters:
        address           :  Address to query rewards for.
        eligible_balance  :  Number of tokens, at this point in time, the address has that are eligible for rewards.
        """
        rewards = eligible_balance * (self._reward_rate.get() - self._entry_reward_rate[address]) + self._rewards[address]
        return self._rscore_to_loop(rewards)

    def update_rewards(self, address: Address, eligible_balance: int):
        """
        Computes all rewards up to this point in time and records them. Next, the entry reward is updated to the current
        reward rate. ALWAYS use this method before changing the eligible balance of an address (for example before
        staking and unstaking in the irc2 contract) If this is not done the reward tracking will not be accurate.

        Parameters
        address           :  Address to update rewards on.
        eligible_balance  :  Number of tokens, at this point in time, the address has that are eligible for rewards.
        """
        rewards = eligible_balance * (self._reward_rate.get() - self._entry_reward_rate[address])
        self._rewards[address] += rewards
        self._entry_reward_rate[address] = self._reward_rate.get()

    def _rscore_to_loop(self, rscore: int) -> int:
        """
        Convert rscore to loop. 
        """
        return rscore // 10**self._rscore_decimals

    def _loop_to_rscore(self, loop: int) -> int:
        """
        Convert loop to rscore.
        """
        return loop * 10**self._rscore_decimals
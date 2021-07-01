from ..scorelib import SCORELib
from tbears.libs.scoretest.score_test_case import ScoreTestCase


class TestSCORELib(ScoreTestCase):

    def setUp(self):
        super().setUp()
        self.score = self.get_score_instance(SCORELib, self.test_account1)
        self.reward_handler = self.score._reward_handler
        self.distribution_amount = 10 ** 21
        self.total_supply = 10 ** 23
        self.set_msg(self.test_account1, 10**22)
        
    def test_loop_to_rscore(self):
        self.assertEqual(self.reward_handler._loop_to_rscore(10**18), 10**36)

    def test_rscore_to_loop(self):
        self.assertEqual(self.reward_handler._rscore_to_loop(10**36), 10**18)

    def test_distribute_rewards(self):

        # Test if correct reward rate is saved.
        self.reward_handler.distribute_rewards(self.distribution_amount, self.total_supply)
        reward_rate = self.reward_handler._reward_rate.get()
        self.assertEqual(reward_rate, 10 ** 16)
        
        # Test if reward_rate is increased after each distribution event.
        self.reward_handler.distribute_rewards(self.distribution_amount, self.total_supply)
        reward_rate = self.reward_handler._reward_rate.get()
        self.assertEqual(reward_rate, 2 * 10 ** 16)

    def test_query_rewards(self):
        
        # Test that there are no rewards at first.
        rewards = self.reward_handler.query_rewards(self.test_account1, 10 ** 21)
        self.assertEqual(rewards, 0)

        # Test query method after distributing rewards.
        self.reward_handler.distribute_rewards(self.distribution_amount, self.total_supply)
        rewards = self.reward_handler.query_rewards(self.test_account1, 10 ** 21)
        self.assertEqual(rewards, 10**19)

        # Test if query_rewards gives double value after a second distribution.
        self.reward_handler.distribute_rewards(self.distribution_amount, self.total_supply)
        rewards = self.reward_handler.query_rewards(self.test_account1, 10 ** 21)
        self.assertEqual(rewards, 2 * 10**19)

        # Test if query_rewards gives same result after running update_rewards.
        self.reward_handler.update_rewards(self.test_account1, 10 ** 21)
        rewards = self.reward_handler.query_rewards(self.test_account1, 10 ** 21)
        self.assertEqual(rewards, 2 * 10**19)

    def test_update_rewards(self):

        # Distribute rewards.
        self.reward_handler.distribute_rewards(self.distribution_amount, self.total_supply)
        reward_rate = self.reward_handler._reward_rate.get()

        # Check entry_reward_rate and rewards
        entry_reward_rate = self.reward_handler._entry_reward_rate[self.test_account1]
        rewards = self.reward_handler._rewards[self.test_account1]
        self.assertEqual(entry_reward_rate, 0)
        self.assertEqual(rewards, 0)
        
        # Update rewards and check rewards and entry_reward_rate.
        self.reward_handler.update_rewards(self.test_account1, 10 ** 21)
        entry_reward_rate = self.reward_handler._entry_reward_rate[self.test_account1]
        rewards = self.reward_handler._rewards[self.test_account1]
        self.assertEqual(entry_reward_rate, reward_rate)
        self.assertEqual(rewards, 10**19 * 10**18)

        # Second distribute rewards.
        self.reward_handler.distribute_rewards(self.distribution_amount, self.total_supply)

        # Update rewards and check updated reward rate.
        self.reward_handler.update_rewards(self.test_account1, 10 ** 21)
        entry_reward_rate = self.reward_handler._entry_reward_rate[self.test_account1]
        rewards = self.reward_handler._rewards[self.test_account1]
        self.assertEqual(entry_reward_rate, reward_rate * 2)
        self.assertEqual(rewards, 2 * 10**19 * 10**18)
    
    def test_claim_rewards(self):

        # Check if correct rewards are returned with claim_rewards.
        self.reward_handler.distribute_rewards(self.distribution_amount, self.total_supply)
        rewards_1 = self.reward_handler.query_rewards(self.test_account1, 10 ** 21)
        rewards_2 = self.reward_handler.withdraw_rewards(self.test_account1, 10 ** 21)
        self.assertEqual(rewards_1, rewards_2)

        # Check if rewards are deducted after claim_rewards.
        rewards_3 = self.reward_handler.query_rewards(self.test_account1, 10 ** 21)
        self.assertEqual(rewards_3, 0)
        
        
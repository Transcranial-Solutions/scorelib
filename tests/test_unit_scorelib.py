from ..scorelib import SCORELib
from tbears.libs.scoretest.score_test_case import ScoreTestCase


class TestSCORELib(ScoreTestCase):

    def setUp(self):
        super().setUp()
        self.score = self.get_score_instance(SCORELib, self.test_account1)
        self.reward_handler = self.score._rewards

    def test_distribute_rewards(self):
        self.reward_handler.distribute_rewards(10, 10000)
        print(self.reward_handler.query_rewards(self.test_account1, 20))

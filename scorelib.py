from iconservice import *
from scorelib.lib.reward_tracker import RewardTracker
TAG = 'SCORELib'

class SCORELib(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._reward_handler = RewardTracker("rewards", db)

    def on_install(self) -> None:
        super().on_install()
        
    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def hello(self) -> str:
        Logger.debug(f'Hello, world!', TAG)
        return "Hello"

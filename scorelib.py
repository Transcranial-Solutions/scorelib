from iconservice import *
from .scorelib.reward_handler import RewardHandler

TAG = 'SCORELib'


class SCORELib(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._reward_handler = RewardHandler("rewards", 18, db, self)

    def on_install(self) -> None:
        super().on_install()
        
    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def hello(self) -> str:
        Logger.debug(f'Hello, world!', TAG)
        return "Hello"

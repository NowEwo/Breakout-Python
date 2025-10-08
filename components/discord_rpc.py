import discordrpc
from discordrpc.utils import timestamp

from components.logging import Logger

DISCORD_APPLICATION_ID = 1425483708424650772
START_TIMESTAMP = timestamp

class DiscordRPC:
    def __init__(self) -> None:
        self.logger = Logger("components.discord_rpc")

        self.logger.log(f"Creating Discord rich presence element with application ID {DISCORD_APPLICATION_ID}")
        self.rpc = discordrpc.RPC(app_id=DISCORD_APPLICATION_ID)

    def set_rich_presence(self, level=1):
        self.logger.success(f"Discord rich presence set to level {level}")
        self.rpc.set_activity(
            state=f"Level {level}",
            details="Playing with bricks",
            ts_start=START_TIMESTAMP
        )
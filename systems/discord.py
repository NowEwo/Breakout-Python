import discordrpc
from discordrpc.utils import timestamp

DISCORD_APPLICATION_ID = 1425483708424650772
START_TIMESTAMP = timestamp


class DiscordRPC:
    def __init__(self) -> None:
        self.rpc = discordrpc.RPC(app_id=DISCORD_APPLICATION_ID)

    def set_rich_presence(self, Title, Text):
        self.rpc.set_activity(
            state=Text,
            details=Title,
            ts_start=START_TIMESTAMP
        )

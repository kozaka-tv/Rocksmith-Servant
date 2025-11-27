import os
from twitchio.ext import commands

class RelayBot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=os.environ['BOT_OAUTH_TOKEN'],
            client_id=os.environ['BOT_CLIENT_ID'],
            client_secret=os.environ['BOT_CLIENT_SECRET'],
            prefix='!',
            initial_channels=['kozaka', 'kozakabot']
        )

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):
        # Avoid reacting to own messages
        if message.echo:
            return

        # Relay message from kozaka to kozakabot
        if message.channel.name == 'kozaka':
            target_channel = self.get_channel('kozakabot')
            if target_channel:
                await target_channel.send(message.content)

        await self.handle_commands(message)

if __name__ == '__main__':
    bot = RelayBot()
    bot.run()

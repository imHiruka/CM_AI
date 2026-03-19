import os

import discord

import bot_triggers
import random
from discord.ext import commands
from google import genai
from google.genai import types

# // -- DOCUMENTATION -- // #
# // go fuck yourself im too lazy to write documentation. // #

intents = discord.Intents.default()
intents.message_content = True

TOKEN = os.getenv("CM_AI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client_gemini = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = 'gemini-2.0-flash'

my_variable = 0

safety_config = [
    types.SafetySetting(
        category='HARM_CATEGORY_HATE_SPEECH',
        threshold='BLOCK_LOW_AND_ABOVE',
    ),
    types.SafetySetting(
        category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
        threshold='BLOCK_LOW_AND_ABOVE',
    ),
    types.SafetySetting(
        category='HARM_CATEGORY_HARASSMENT',
        threshold='BLOCK_LOW_AND_ABOVE',
    ),
]

bot = commands.Bot(command_prefix="//", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_input = message.content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()

    if bot.user.mentioned_in(message):
        chosen_response_message = chosen_response_message = random.choice(list(bot_triggers.responses))
        await message.channel.send(f"{message.author.mention}, {chosen_response_message}.")
        async with message.channel.typing():
            try:
                response = client_gemini.models.generate_content(
                    model=MODEL_ID,
                    contents=user_input,
                )
                await message.reply(response.text[:2000])
            except Exception as e:
                print(f"Error: {e}")

bot.run(TOKEN)
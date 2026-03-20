import asyncio
import os
import time

import discord
from pydantic_core.core_schema import model_schema

import bot_triggers
import random
from discord.ext import commands
from google import genai
from google.genai import types

from bot_triggers import load_config

intents = discord.Intents.default()
intents.message_content = True

TOKEN = os.getenv("CM_AI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = 'gemini-3-flash-preview'

min_time_to_wait = 5
max_time_to_wait = 15

min_chance_to_say_something = 1
max_chance_to_say_something = 10

client_gemini = genai.Client(api_key=GEMINI_API_KEY)

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
async def on_ready():
    await bot.change_presence(activity=discord.Game("Inside every demon is a rainbow!"), status=discord.Status.dnd)
    try:
        bot_triggers.load_memory()
        print(f"Loaded {len(bot_triggers.memory)} messages worth of saved memory.")
    except Exception as e1:
        print(f"Failed to load memory, ERR={e1}")
    try:
        bot_triggers.load_config()
        print("Loaded config!")
    except Exception as e2:
        print(f"Failed to load configs, ERR={e2}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    user_input = message.content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()
    if bot.user.mentioned_in(message):
        if user_input.startswith('//'):
            if len(user_input.strip()) <= 2:
                return
            prompt = user_input[2:].split(" ", 1)
            command_name = prompt[0].lower()
            if command_name == "change_mode":
                await message.channel.send("Sure! What mode would you like to use? Modes are: \"Gemini\", \"Stupid\" and \"NormalBot\".")
                def check(m):
                    return m.author == message.author and m.channel == message.channel
                try:
                    reply = await bot.wait_for('message', check=check, timeout=15.0)
                    match reply.content.lower():
                        case "gemini":
                            bot_triggers.current_mode = bot_triggers.MODES[0]
                            await message.channel.send(f"Current mode is now: {bot_triggers.MODES[0]}")
                        case "stupid":
                            bot_triggers.current_mode = bot_triggers.MODES[1]
                            await message.channel.send(f"Current mode is now: {bot_triggers.MODES[1]}")
                        case _:
                            bot_triggers.current_mode = bot_triggers.MODES[0]
                            await message.channel.send(f"Current mode is now: {bot_triggers.MODES[0]}")
                    bot_triggers.save_config()
                except asyncio.TimeoutError:
                    await message.channel.send("You took too long to respond!")
            elif command_name == "current_mode":
                await message.channel.send(f"Selected current mode is: {bot_triggers.current_mode}")
        if bot_triggers.current_mode == bot_triggers.MODES[0] and not user_input.startswith("//"):
            try:
                response = client_gemini.models.generate_content(
                    model=MODEL_ID,
                    contents=user_input,
                    config=types.GenerateContentConfig(safety_settings=safety_config),
                )
                if response.text:
                    await message.reply(response.text[:2000])
                else:
                    await message.reply("Haha... Let's not ask such silly questions!")
            except Exception as e:
                await message.reply(f"Got exception {e}")
    if bot_triggers.current_mode == bot_triggers.MODES[1]:
        if not user_input in bot_triggers.nono_words:
            bot_triggers.add_word(user_input, user=message.author)
        chance = random.randint(min_chance_to_say_something, max_chance_to_say_something)
        if chance > max_chance_to_say_something / 2:
            if len(bot_triggers.memory) < 1:
                await message.channel.send("Inside every demon is a rainbow!")
            else:
                chosen_message = random.choice(list(bot_triggers.memory))
                await message.channel.send(chosen_message)
        await bot.process_commands(message)
bot.run(TOKEN)
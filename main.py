import asyncio
import json
import os

import discord

import bot_triggers
import random
from discord.ext import commands
from google import genai
from google.genai import types

intents = discord.Intents.default()
intents.message_content = True

TOKEN = os.getenv("CM_AI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = 'gemini-3-flash-preview'

client_gemini = genai.Client(api_key=GEMINI_API_KEY)

my_variable = 0

saved_config = "saved_config.json"
global saved_config_data

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
    global saved_config_data
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
    with open(saved_config, "r") as f:
        saved_config_data = json.load(f)

def calc_random(v1, v2):
    v3 = random.randint(v1, v2)

    return v3

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
                        case "commands":
                            bot_triggers.current_mode = bot_triggers.MODES[2]
                            await message.channel.send(f"Current mode is now: {bot_triggers.MODES[2]}")
                        case _:
                            bot_triggers.current_mode = bot_triggers.MODES[0]
                            await message.channel.send(f"Current mode is now: {bot_triggers.MODES[0]}")
                    bot_triggers.save_config()
                except asyncio.TimeoutError:
                    await message.channel.send(f"You took too long to respond! Current respond_timeout is set to {bot_triggers.reply_timeout}")
            elif command_name == "current_mode":
                await message.channel.send(f"Selected current mode is: {bot_triggers.current_mode}")
            elif command_name == "add_nono_word":
                await message.channel.send("Please type the word you wish to add to the NoNo List!")
                def check(m):
                    return m.author == message.author and m.channel == message.channel
                try:
                    user_response = await bot.wait_for('message', check=check, timeout=bot_triggers.reply_timeout)
                    bad_word = user_response.content.lower().strip()
                    bot_triggers.nono_words.append(bad_word)
                    await message.channel.send(f"{bad_word} added to the NoNo List!")
                except asyncio.TimeoutError:
                    await message.channel.send(f"You took too long to respond! Current respond_timeout is set to {bot_triggers.reply_timeout}")
            elif command_name == "remove_nono_word":
                await message.channel.send("Please type the word you wish to remove from the NoNo List!")
                def check(m):
                    return m.author == message.author and m.channel == message.channel
                try:
                    user_response = await bot.wait_for('message', check=check, timeout=bot_triggers.reply_timeout)
                    bad_word = user_response.content.lower()
                    if not bad_word in bot_triggers.nono_words:
                        await message.channel.send("That word is not even in the NoNo Words list!")
                    else:
                        bot_triggers.nono_words.remove(bad_word)
                        await message.channel.send(f"Removed {bad_word} from the NoNo list!")
                except asyncio.TimeoutError:
                    await message.channel.send(f"You took too long to respond! Current respond_timeout is set to {bot_triggers.reply_timeout}")
        elif bot_triggers.current_mode == bot_triggers.MODES[0] and not user_input.startswith("//"):
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
    if bot_triggers.current_mode == bot_triggers.MODES[1] and not user_input.startswith("//"):
        if not user_input in bot_triggers.nono_words:
            bot_triggers.add_word(user_input, user=message.author)
        else:
            await message.channel.send("Let's not say that!")
            return
        chance = random.randint(bot_triggers.min_chance_to_say_something, bot_triggers.max_chance_to_say_something)
        if chance > bot_triggers.max_chance_to_say_something / 2:
            if len(bot_triggers.memory) > 0:
                all_words = list(bot_triggers.memory)
                selected_words = []
                for word in all_words:
                    if len(selected_words) < bot_triggers.max_words_to_collect:
                        selected_words.append(word)
                random.shuffle(selected_words)
                sentence = " ".join(selected_words)
                await message.channel.send(sentence)

        await bot.process_commands(message)
bot.run(TOKEN)
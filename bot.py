```python
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import database
import random
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🔔 PING USER ON EVERY MESSAGE
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    await message.channel.send(f"{message.author.mention}", delete_after=2)
    await bot.process_commands(message)

# 🔥 UI BAR
def bar(value):
    filled = "🟩" * (value // 10)
    empty = "⬜" * (10 - value // 10)
    return filled + empty

# 🛒 SHOP (50+ ITEMS)
shop_items = {
    "food": 20, "toy": 30, "super_food": 50,
    "mega_food": 80, "ultra_food": 120,
    "ball": 25, "rope": 40, "frisbee": 60,
    "golden_food": 200, "diamond_food": 500,
    "energy_drink": 100, "super_energy": 200,
    "mega_energy": 400, "ultra_energy": 800,
    "pet_bed": 150, "luxury_bed": 500,
    "royal_bed": 1000, "magic_bed": 2000,
    "healing_potion": 120, "mega_potion": 300,
    "ultra_potion": 700, "revive_potion": 1500,
    "xp_boost": 250, "mega_xp_boost": 600,
    "ultra_xp_boost": 1200,
    "coin_boost": 200, "mega_coin_boost": 500,
    "ultra_coin_boost": 1000,
    "treat": 50, "premium_treat": 150,
    "royal_treat": 400, "divine_treat": 1000,
    "toy_box": 300, "magic_toy": 700,
    "dragon_toy": 1500, "galaxy_toy": 3000,
    "pet_armor": 1000, "iron_armor": 3000,
    "diamond_armor": 8000, "god_armor": 20000,
    "luck_charm": 500, "mega_luck": 1500,
    "ultra_luck": 5000,
    "mystery_box": 1000, "epic_box": 5000,
    "legendary_box": 20000
}

# PET SHOP
pet_shop = {
    "fox": 30000, "wolf": 50000, "lion": 80000, "tiger": 120000,
    "panther": 200000, "bear": 400000, "eagle": 700000,
    "shark": 1000000, "griffin": 2000000, "phoenix": 5000000,
    "unicorn": 10000000, "hydra": 20000000, "kraken": 30000000,
    "demon_dog": 40000000, "celestial_cat": 50000000,
    "void_dragon": 60000000, "shadow_wolf": 70000000,
    "galaxy_lion": 80000000, "cosmic_tiger": 90000000,
    "god_dragon": 100000000
}

# EVOLUTIONS
evolutions = {
    "cat": ["Kitten", "Cat", "Tiger", "Mythic Lion"],
    "dog": ["Puppy", "Dog", "Wolf", "Direwolf"],
    "dragon": ["Hatchling", "Young Dragon", "Elder Dragon", "Legendary Dragon"]
}

def get_evolution(species, level):
    if species not in evolutions:
        return species
    if level >= 20:
        return evolutions[species][3]
    elif level >= 10:
        return evolutions[species][2]
    elif level >= 5:
        return evolutions[species][1]
    else:
        return evolutions[species][0]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(pet_decay_loop())

# START
@bot.command()
async def start(ctx):
    await ctx.send(f"""
🌟 **Welcome to Pet Simulator RPG!**
Use !adopt to start!
""")

# ADOPT
@bot.command()
async def adopt(ctx, species: str):
    species = species.lower()

    if species not in ["cat", "dog", "dragon"]:
        return await ctx.send("Choose: cat/dog/dragon")

    if database.get_pet(str(ctx.author.id)):
        return await ctx.send("Already have pet!")

    database.create_pet(str(ctx.author.id), species)
    await ctx.send(f"🐾 Adopted {species}!")

# PET
@bot.command()
async def pet(ctx):
    pet = database.get_pet(str(ctx.author.id))
    if not pet:
        return await ctx.send("No pet!")

    evo = get_evolution(pet[1], pet[2])

    embed = discord.Embed(title="🐾 Your Pet", color=discord.Color.purple())

    embed.add_field(name="Species", value=pet[1])
    embed.add_field(name="Evolution", value=evo)
    embed.add_field(name="Level", value=f"{pet[2]} (XP {pet[3]}/100)", inline=False)

    embed.add_field(name="🍗 Hunger", value=bar(pet[4]), inline=False)
    embed.add_field(name="😊 Happiness", value=bar(pet[5]), inline=False)
    embed.add_field(name="⚡ Energy", value=bar(pet[6]), inline=False)

    embed.add_field(name="💰 Coins", value=pet[7])

    await ctx.send(embed=embed)

# FEED
@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def feed(ctx):
    pet = database.get_pet(str(ctx.author.id))
    if not pet:
        return await ctx.send("❌ No pet!")

    hunger = max(0, pet[4] - 10)
    xp = pet[3] + 10
    level = pet[2]

    if xp >= 100:
        xp = 0
        level += 1

    database.update_pet(str(ctx.author.id), hunger=hunger, xp=xp, level=level)
    await ctx.send("🍖 Fed!")

# PLAY
@bot.command()
@commands.cooldown(1, 180, commands.BucketType.user)
async def play(ctx):
    pet = database.get_pet(str(ctx.author.id))
    if not pet:
        return await ctx.send("❌ No pet!")

    happiness = min(100, pet[5] + 10)
    energy = max(0, pet[6] - 5)

    database.update_pet(str(ctx.author.id), happiness=happiness, energy=energy)
    await ctx.send("🎾 Played!")

# REST
@bot.command()
@commands.cooldown(1, 240, commands.BucketType.user)
async def rest(ctx):
    pet = database.get_pet(str(ctx.author.id))
    if not pet:
        return await ctx.send("❌ No pet!")

    energy = min(100, pet[6] + 20)

    database.update_pet(str(ctx.author.id), energy=energy)
    await ctx.send("😴 Resting...")

# SHOP
@bot.command()
async def shop(ctx):
    embed = discord.Embed(title="🛒 Shop", color=discord.Color.green())
    for item, price in shop_items.items():
        embed.add_field(name=item, value=f"💰 {price}")
    await ctx.send(embed=embed)

# PETSHOP
@bot.command()
async def petshop(ctx):
    embed = discord.Embed(title="🐾 Pet Shop", color=discord.Color.gold())
    for pet, price in pet_shop.items():
        embed.add_field(name=pet, value=f"💰 {price}")
    await ctx.send(embed=embed)

# LOOP
async def pet_decay_loop():
    await bot.wait_until_ready()

    while not bot.is_closed():
        for user_id in database.get_all_users():
            pet = database.get_pet(user_id)
            if not pet:
                continue

            hunger = min(100, pet[4] + 5)
            happiness = max(0, pet[5] - 5)
            coins = pet[7]

            if hunger >= 80 or happiness <= 20:
                coins = max(0, coins - 10)

            database.update_pet(user_id, hunger=hunger, happiness=happiness, coins=coins)

        await asyncio.sleep(300)

bot.run(TOKEN)
```

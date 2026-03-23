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

# 🔥 UI BAR
def bar(value):
    filled = "🟩" * (value // 10)
    empty = "⬜" * (10 - value // 10)
    return filled + empty

# SHOP
shop_items = {
    "food": 20,
    "toy": 30,
    "super_food": 50
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

👣 Step 1: Adopt your pet
Use: !adopt cat / !adopt dog / !adopt dragon

🍖 Step 2: Take care of your pet
!feed → Reduce hunger + XP
!play → Increase happiness
!rest → Restore energy

📊 Step 3: Check stats
Use: !pet

🛒 Step 4: Buy items
!shop → View items
!buy food / toy

🎒 Step 5: Inventory
Use: !inventory

⚔️ Step 6: Battle players
Use: !battle @user

💎 Step 7: Buy powerful pets
Use: !petshop → then !buypet

🏆 Goal:
Level up, evolve, earn coins, and become #1!

🔥 Good luck!
""")

# HUNT
@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def hunt(ctx):
    user_id = str(ctx.author.id)
    pet = database.get_pet(user_id)

    if not pet:
        return await ctx.send("❌ You need a pet!")

    reward = random.randint(20, 80)
    database.update_pet(user_id, coins=pet[7] + reward)

    embed = discord.Embed(title="🏹 Hunt", description=f"💰 +{reward} coins!", color=discord.Color.orange())
    await ctx.send(embed=embed)

# SPIN
@bot.command()
@commands.cooldown(1, 20, commands.BucketType.user)
async def spin(ctx):
    user_id = str(ctx.author.id)
    pet = database.get_pet(user_id)

    if not pet:
        return await ctx.send("❌ You need a pet!")

    cost = 400
    coins = pet[7]

    if coins < cost:
        return await ctx.send("💸 Need 400 coins!")

    result = random.choice(["win", "lose", "jackpot"])

    if result == "win":
        reward = 5000
        coins += reward
        text = f"🎉 +{reward}"
        color = discord.Color.green()
    elif result == "jackpot":
        reward = 50000
        coins += reward
        text = f"🔥 JACKPOT +{reward}"
        color = discord.Color.gold()
    else:
        coins -= cost
        text = "😢 -400"
        color = discord.Color.red()

    database.update_pet(user_id, coins=coins)
    embed = discord.Embed(title="🎰 Spin", description=text, color=color)
    await ctx.send(embed=embed)

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
    happiness = min(100, pet[5] + 10)
    energy = max(0, pet[6] - 5)

    database.update_pet(str(ctx.author.id), happiness=happiness, energy=energy)
    await ctx.send("🎾 Played!")

# REST
@bot.command()
@commands.cooldown(1, 240, commands.BucketType.user)
async def rest(ctx):
    pet = database.get_pet(str(ctx.author.id))
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

# BUY PET
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def buypet(ctx, pet_name: str):
    pet_name = pet_name.lower()
    user_pet = database.get_pet(str(ctx.author.id))

    if pet_name not in pet_shop:
        return await ctx.send("Invalid pet!")

    if not user_pet:
        return await ctx.send("Adopt first!")

    if user_pet[7] < pet_shop[pet_name]:
        return await ctx.send("Not enough coins!")

    database.update_pet(str(ctx.author.id), coins=user_pet[7] - pet_shop[pet_name])
    database.create_pet(str(ctx.author.id), pet_name)

    await ctx.send(f"🎉 Bought {pet_name}!")

# INVENTORY
@bot.command()
async def inventory(ctx):
    items = database.get_inventory(str(ctx.author.id))
    if not items:
        return await ctx.send("Empty!")

    msg = "🎒 Inventory\n"
    for item, qty in items:
        msg += f"{item} x{qty}\n"

    await ctx.send(msg)

# USE
@bot.command()
async def use(ctx, item: str):
    user_id = str(ctx.author.id)
    pet = database.get_pet(user_id)

    if not pet:
        return await ctx.send("❌ No pet!")

    items = database.get_inventory(user_id)
    item_dict = {i[0]: i[1] for i in items}

    if item not in item_dict:
        return await ctx.send("No item!")

    hunger = pet[4]
    happiness = pet[5]

    if item == "food":
        hunger = max(0, hunger - 20)
    elif item == "toy":
        happiness = min(100, happiness + 20)

    database.update_pet(user_id, hunger=hunger, happiness=happiness)
    database.remove_item(user_id, item, 1)

    await ctx.send(f"✅ Used {item}")

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

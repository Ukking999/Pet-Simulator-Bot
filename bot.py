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
    bot.loop.create_task(pet_decay_loop())  # 👈 ADD THIS LINE

# 🆕 START COMMAND
@bot.command()
async def start(ctx):
    await ctx.send(f"""
🌟 **Welcome to Pet Simulator RPG!**

👣 **Step 1: Adopt your pet**
Use: `!adopt cat` / `!adopt dog` / `!adopt dragon`

🍖 **Step 2: Take care of your pet**
- !feed → Reduce hunger + XP
- !play → Increase happiness
- !rest → Restore energy

📊 **Step 3: Check stats**
Use: `!pet`

🛒 **Step 4: Buy items**
- !shop → View items
- !buy food / toy

🎒 **Step 5: Inventory**
Use: `!inventory`

⚔️ **Step 6: Battle players**
Use: `!battle @user`

💎 **Step 7: Buy powerful pets**
Use: `!petshop` → then `!buypet`

🏆 **Goal:**
Level up, evolve, earn coins, and become #1!

🔥 Good luck {ctx.author.mention}!
""")

# Hunt

@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def hunt(ctx):
    user_id = str(ctx.author.id)
    pet = database.get_pet(user_id)

    if not pet:
        return await ctx.send("❌ You need a pet!")

    reward = random.randint(20, 80)
    database.update_pet(user_id, coins=pet[7] + reward)

    await ctx.send(f"🏹 You went hunting and earned 💰 {reward} coins!")

# Casino 

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
        return await ctx.send("💸 You need 50 coins to spin!")

    result = random.choice(["win", "lose", "jackpot"])

    if result == "win":
        reward = 5000
        coins += reward
        msg = f"🎉 You won {reward} coins!"
    elif result == "jackpot":
        reward = 50000
        coins += reward
        msg = f"🔥 JACKPOT!!! You won {reward} coins!"
    else:
        coins -= cost
        msg = "😢 You lost 400 coins!"

    database.update_pet(user_id, coins=coins)

    await ctx.send(f"🎰 Spin Result: {msg}")

# 🐾 ADOPT
@bot.command()
async def adopt(ctx, species: str):
    species = species.lower()
    if species not in ["cat", "dog", "dragon"]:
        return await ctx.send("Choose: cat, dog, dragon")

    if database.get_pet(str(ctx.author.id)):
        return await ctx.send("You already have a pet!")

    database.create_pet(str(ctx.author.id), species)
    await ctx.send(f"{ctx.author.mention} adopted a {species}! 🐾")

# 📊 PET
@bot.command()
async def pet(ctx):
    pet = database.get_pet(str(ctx.author.id))
    if not pet:
        return await ctx.send("No pet!")

    evo = get_evolution(pet[1], pet[2])

    await ctx.send(f"""
🐾 **Pet**
Species: {pet[1]}
Evolution: {evo}
Level: {pet[2]} (XP {pet[3]}/100)

🍗 Hunger: {pet[4]}
😊 Happiness: {pet[5]}
⚡ Energy: {pet[6]}
💰 Coins: {pet[7]}
""")

# 🍖 FEED
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

# 🎾 PLAY
@bot.command()
@commands.cooldown(1, 180, commands.BucketType.user)
async def play(ctx):
    pet = database.get_pet(str(ctx.author.id))
    happiness = min(100, pet[5] + 10)
    energy = max(0, pet[6] - 5)

    database.update_pet(str(ctx.author.id), happiness=happiness, energy=energy)
    await ctx.send("🎾 Played!")

# 😴 REST
@bot.command()
@commands.cooldown(1, 240, commands.BucketType.user)
async def rest(ctx):
    pet = database.get_pet(str(ctx.author.id))
    energy = min(100, pet[6] + 20)

    database.update_pet(str(ctx.author.id), energy=energy)
    await ctx.send("😴 Resting...")

# 🛒 SHOP
@bot.command()
async def shop(ctx):
    msg = "🛒 Shop\n"
    for item, price in shop_items.items():
        msg += f"{item} - {price}\n"
    await ctx.send(msg)
@bot.command()
async def petshop(ctx):
    msg = "🐾 Pet Shop\n"
    for pet, price in pet_shop.items():
        msg += f"{pet} - {price} coins\n"
    await ctx.send(msg)
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def buypet(ctx, pet_name: str):
    pet_name = pet_name.lower()

    if pet_name not in pet_shop:
        return await ctx.send("❌ Invalid pet name!")

    user_pet = database.get_pet(str(ctx.author.id))

    if not user_pet:
        return await ctx.send("❌ You need a pet first! Use !adopt")

    coins = user_pet[7]
    price = pet_shop[pet_name]

    if coins < price:
        return await ctx.send("💸 Not enough coins!")

    # 💰 Deduct coins
    database.update_pet(str(ctx.author.id), coins=coins - price)

    # 🐾 Give new pet (replace old one OR store separately)
    database.create_pet(str(ctx.author.id), pet_name)

    await ctx.send(f"🎉 You bought a {pet_name}!")

# 💰 BUY
@bot.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def buy(ctx, item: str):
    pet = database.get_pet(str(ctx.author.id))

    if item not in shop_items:
        return await ctx.send("Invalid item")

    if pet[7] < shop_items[item]:
        return await ctx.send("Not enough coins")

    database.update_pet(str(ctx.author.id), coins=pet[7] - shop_items[item])
    database.add_item(str(ctx.author.id), item, 1)

    await ctx.send(f"Bought {item}")

# 🎒 INVENTORY
@bot.command()
async def inventory(ctx):
    items = database.get_inventory(str(ctx.author.id))
    if not items:
        return await ctx.send("Empty!")

    msg = "🎒 Inventory\n"
    for item, qty in items:
        msg += f"{item} x{qty}\n"
    await ctx.send(msg)
@bot.command()
async def use(ctx, item: str):
    user_id = str(ctx.author.id)
    pet = database.get_pet(user_id)

    if not pet:
        return await ctx.send("❌ You don't have a pet!")

    items = database.get_inventory(user_id)
    item_dict = {i[0]: i[1] for i in items}

    if item not in item_dict or item_dict[item] <= 0:
        return await ctx.send("❌ You don't have this item!")

    hunger = pet[4]
    happiness = pet[5]
    energy = pet[6]

    if item == "food":
        hunger = max(0, hunger - 20)
    elif item == "toy":
        happiness = min(100, happiness + 20)
    elif item == "super_food":
        hunger = max(0, hunger - 30)
        happiness = min(100, happiness + 10)
    else:
        return await ctx.send("❌ Cannot use this item!")

    # update pet
    database.update_pet(user_id, hunger=hunger, happiness=happiness, energy=energy)

    # remove item
    database.remove_item(user_id, item, 1)

    await ctx.send(f"✅ Used {item}!")

# ⚔️ BATTLE
@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def battle(ctx, opponent: discord.Member):
    p1 = database.get_pet(str(ctx.author.id))
    p2 = database.get_pet(str(opponent.id))

    hp1 = 50 + p1[2]*10
    hp2 = 50 + p2[2]*10

    while hp1 > 0 and hp2 > 0:
        await asyncio.sleep(1)
        hp2 -= p1[2]*random.randint(2,5)
        if hp2 <= 0:
            break
        hp1 -= p2[2]*random.randint(2,5)

    if hp1 > 0:
        winner, loser = ctx.author, opponent
        win_pet, lose_pet = p1, p2
    else:
        winner, loser = opponent, ctx.author
        win_pet, lose_pet = p2, p1

    database.update_pet(str(winner.id), coins=win_pet[7] + 150)
    database.update_pet(str(loser.id), coins=max(0, lose_pet[7] - 40))

    await ctx.send(f"🏆 {winner.mention} wins! 💰 +150\n💀 {loser.mention} loses 40")

# ⏳ COOLDOWN ERROR
@bot.event
async def on_command_error(ctx, error):
    from discord.ext.commands import CommandOnCooldown
    if isinstance(error, CommandOnCooldown):
        await ctx.send(f"⏳ Wait {round(error.retry_after,1)}s")

async def pet_decay_loop():
    await bot.wait_until_ready()

    while not bot.is_closed():
        all_users = database.get_all_users()

        for user_id in all_users:
            pet = database.get_pet(user_id)

            if not pet:
                continue

            hunger = min(100, pet[4] + 5)
            happiness = max(0, pet[5] - 5)
            coins = pet[7]

            # 💀 penalty
            if hunger >= 80 or happiness <= 20:
                coins = max(0, coins - 10)

            database.update_pet(
                user_id,
                hunger=hunger,
                happiness=happiness,
                coins=coins
            )

        await asyncio.sleep(300)  # every 5 minutes

print("TOKEN =", TOKEN)
bot.run(TOKEN)

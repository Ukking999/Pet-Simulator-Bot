```python
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import database
import random
import asyncio

# ================== SETUP ==================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================== UI HELPERS ==================
def bar(value):
    filled = "🟩" * (value // 10)
    empty = "⬜" * (10 - value // 10)
    return filled + empty

def create_embed(title, description, color=discord.Color.blue()):
    return discord.Embed(title=title, description=description, color=color)

# ================== MESSAGE PING ==================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    await message.channel.send(f"{message.author.mention}", delete_after=2)
    await bot.process_commands(message)

# ================== SHOP ==================
shop_items = {
    f"item_{i}": random.randint(10, 5000) for i in range(1, 60)
}

# add main items
shop_items.update({
    "food": 20, "toy": 30, "super_food": 50,
    "mega_food": 80, "ultra_food": 120,
    "energy_drink": 100, "xp_boost": 250,
    "coin_boost": 200, "legendary_box": 20000
})

# ================== PET SHOP ==================
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

# ================== EVOLUTIONS ==================
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

# ================== READY ==================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    bot.loop.create_task(pet_decay_loop())

# ================== START ==================
@bot.command()
async def start(ctx):
    embed = create_embed(
        "🌟 Pet Simulator RPG",
        "Use !adopt to begin your journey!\n\nChoose: cat / dog / dragon",
        discord.Color.green()
    )
    await ctx.send(embed=embed)

# ================== ADOPT ==================
@bot.command()
async def adopt(ctx, species: str):
    species = species.lower()

    if species not in ["cat", "dog", "dragon"]:
        return await ctx.send("❌ Choose: cat/dog/dragon")

    if database.get_pet(str(ctx.author.id)):
        return await ctx.send("❌ You already have a pet!")

    database.create_pet(str(ctx.author.id), species)
    await ctx.send(f"🐾 {ctx.author.mention} adopted a **{species}**!")

# ================== PET ==================
@bot.command()
async def pet(ctx):
    pet = database.get_pet(str(ctx.author.id))
    if not pet:
        return await ctx.send("❌ No pet!")

    evo = get_evolution(pet[1], pet[2])

    embed = discord.Embed(title=f"{ctx.author.name}'s Pet 🐾", color=discord.Color.purple())

    embed.add_field(name="Species", value=pet[1])
    embed.add_field(name="Evolution", value=evo)
    embed.add_field(name="Level", value=f"{pet[2]} (XP {pet[3]}/100)", inline=False)

    embed.add_field(name="🍗 Hunger", value=bar(pet[4]), inline=False)
    embed.add_field(name="😊 Happiness", value=bar(pet[5]), inline=False)
    embed.add_field(name="⚡ Energy", value=bar(pet[6]), inline=False)

    embed.add_field(name="💰 Coins", value=pet[7])

    await ctx.send(embed=embed)

# ================== FEED ==================
@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def feed(ctx):
    pet = database.get_pet(str(ctx.author.id))
    if not pet:
        return await ctx.send("❌ No pet!")

    hunger = max(0, pet[4] - 15)
    xp = pet[3] + 15
    level = pet[2]

    if xp >= 100:
        xp = 0
        level += 1

    database.update_pet(str(ctx.author.id), hunger=hunger, xp=xp, level=level)
    await ctx.send(f"🍖 {ctx.author.mention} fed the pet!")

# ================== PLAY ==================
@bot.command()
@commands.cooldown(1, 180, commands.BucketType.user)
async def play(ctx):
    pet = database.get_pet(str(ctx.author.id))
    if not pet:
        return await ctx.send("❌ No pet!")

    happiness = min(100, pet[5] + 15)
    energy = max(0, pet[6] - 10)

    database.update_pet(str(ctx.author.id), happiness=happiness, energy=energy)
    await ctx.send(f"🎾 {ctx.author.mention} played!")

# ================== REST ==================
@bot.command()
@commands.cooldown(1, 240, commands.BucketType.user)
async def rest(ctx):
    pet = database.get_pet(str(ctx.author.id))
    if not pet:
        return await ctx.send("❌ No pet!")

    energy = min(100, pet[6] + 30)

    database.update_pet(str(ctx.author.id), energy=energy)
    await ctx.send(f"😴 {ctx.author.mention} is resting...")

# ================== HUNT ==================
@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def hunt(ctx):
    pet = database.get_pet(str(ctx.author.id))
    if not pet:
        return await ctx.send("❌ No pet!")

    reward = random.randint(50, 150)
    database.update_pet(str(ctx.author.id), coins=pet[7] + reward)

    embed = create_embed("🏹 Hunt", f"You earned 💰 {reward} coins!", discord.Color.orange())
    await ctx.send(embed=embed)

# ================== SPIN ==================
@bot.command()
@commands.cooldown(1, 20, commands.BucketType.user)
async def spin(ctx):
    pet = database.get_pet(str(ctx.author.id))
    if not pet:
        return await ctx.send("❌ No pet!")

    cost = 400
    if pet[7] < cost:
        return await ctx.send("💸 Need 400 coins!")

    result = random.choice(["win", "lose", "jackpot"])
    coins = pet[7]

    if result == "win":
        coins += 5000
        msg = "🎉 You won 5000!"
    elif result == "jackpot":
        coins += 50000
        msg = "🔥 JACKPOT 50000!"
    else:
        coins -= cost
        msg = "😢 You lost 400"

    database.update_pet(str(ctx.author.id), coins=coins)
    await ctx.send(msg)

# ================== SHOP ==================
@bot.command()
async def shop(ctx):
    embed = discord.Embed(title="🛒 Shop", color=discord.Color.green())

    for item, price in list(shop_items.items())[:25]:
        embed.add_field(name=item, value=f"💰 {price}")

    embed.set_footer(text="Use !buy <item>")
    await ctx.send(embed=embed)

# ================== BUY ==================
@bot.command()
async def buy(ctx, item: str):
    user_id = str(ctx.author.id)
    pet = database.get_pet(user_id)

    if not pet:
        return await ctx.send("❌ No pet!")

    if item not in shop_items:
        return await ctx.send("❌ Invalid item!")

    if pet[7] < shop_items[item]:
        return await ctx.send("💸 Not enough coins!")

    database.update_pet(user_id, coins=pet[7] - shop_items[item])
    database.add_item(user_id, item, 1)

    await ctx.send(f"✅ Bought {item}!")

# ================== INVENTORY ==================
@bot.command()
async def inventory(ctx):
    items = database.get_inventory(str(ctx.author.id))
    if not items:
        return await ctx.send("🎒 Empty!")

    msg = "🎒 Inventory\n\n"
    for item, qty in items:
        msg += f"• {item} x{qty}\n"

    await ctx.send(msg)

# ================== DECAY LOOP ==================
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

# ================== RUN ==================
bot.run(TOKEN)
```


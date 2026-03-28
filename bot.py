import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import database
import random
import asyncio

# ================= SETUP =================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= UI =================
def bar(value):
    if value < 0:
        value = 0
    if value > 100:
        value = 100
    filled = "🟩" * (value // 10)
    empty = "⬜" * (10 - value // 10)
    return filled + empty

def make_embed(title, desc, color=discord.Color.blue()):
    return discord.Embed(title=title, description=desc, color=color)

# ================= MESSAGE EVENT =================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    # Removed the spammy mention - you can add something else later if you want
    await bot.process_commands(message)

# ================= SHOP ITEMS =================
shop_items = {f"item_{i}": random.randint(50, 5000) for i in range(1, 60)}
shop_items.update({
    "food": 20,
    "toy": 30,
    "super_food": 50,
    "mega_food": 100,
    "energy_drink": 120,
    "xp_boost": 250,
    "coin_boost": 200,
    "legendary_box": 20000
})

# ================= PET SHOP =================
pet_shop = {
    "fox": 30000,
    "wolf": 50000,
    "lion": 80000,
    "tiger": 120000
}

# ================= EVOLUTION =================
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

# ================= READY =================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(pet_decay_loop())

# ================= START =================
@bot.command()
async def start(ctx):
    await ctx.send(embed=make_embed(
"🌟 Welcome to Pet Simulator RPG!
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

🔥 Good luck!",
        "Use `!adopt cat/dog/dragon` to start your journey!",
        discord.Color.green()
    ))

# ================= ADOPT =================
@bot.command()
async def adopt(ctx, species: str):
    species = species.lower()
    user = str(ctx.author.id)

    if species not in ["cat", "dog", "dragon"]:
        await ctx.send("❌ Choose from: `cat`, `dog`, or `dragon`")
        return

    if database.get_pet(user):
        await ctx.send("❌ You already have a pet!")
        return

    database.create_pet(user, species)
    await ctx.send(f"{ctx.author.mention} adopted a **{species}**! 🐾")

# ================= PET =================
@bot.command()
async def pet(ctx):
    pet_data = database.get_pet(str(ctx.author.id))
    if not pet_data:
        await ctx.send("❌ You don't have a pet yet! Use `!adopt`")
        return

    evo = get_evolution(pet_data[1], pet_data[2])

    em = discord.Embed(title="🐾 Your Pet", color=discord.Color.purple())
    em.add_field(name="Species", value=pet_data[1].capitalize(), inline=True)
    em.add_field(name="Evolution", value=evo, inline=True)
    em.add_field(name="Level", value=f"{pet_data[2]} (XP: {pet_data[3]}/100)", inline=False)
    em.add_field(name="Hunger", value=bar(pet_data[4]), inline=False)
    em.add_field(name="Happiness", value=bar(pet_data[5]), inline=False)
    em.add_field(name="Energy", value=bar(pet_data[6]), inline=False)
    em.add_field(name="Coins", value=f"💰 {pet_data[7]}", inline=False)

    await ctx.send(embed=em)

# ================= FEED =================
@bot.command()
async def feed(ctx):
    user = str(ctx.author.id)
    pet = database.get_pet(user)
    if not pet:
        await ctx.send("❌ No pet found!")
        return

    hunger = max(0, pet[4] - 15)
    xp = pet[3] + 15
    level = pet[2]

    if xp >= 100:
        xp = 0
        level += 1

    database.update_pet(user, hunger=hunger, xp=xp, level=level)
    await ctx.send("🍖 Fed your pet! +15 XP")

# ================= PLAY =================
@bot.command()
async def play(ctx):
    user = str(ctx.author.id)
    pet = database.get_pet(user)
    if not pet:
        await ctx.send("❌ No pet found!")
        return

    happiness = min(100, pet[5] + 15)
    energy = max(0, pet[6] - 10)

    database.update_pet(user, happiness=happiness, energy=energy)
    await ctx.send("🎾 Played with your pet!")

# ================= REST =================
@bot.command()
async def rest(ctx):
    user = str(ctx.author.id)
    pet = database.get_pet(user)
    if not pet:
        await ctx.send("❌ No pet found!")
        return

    energy = min(100, pet[6] + 25)
    database.update_pet(user, energy=energy)
    await ctx.send("😴 Your pet is resting...")

# ================= HUNT =================
@bot.command()
async def hunt(ctx):
    user = str(ctx.author.id)
    pet = database.get_pet(user)
    if not pet:
        await ctx.send("❌ No pet found!")
        return

    reward = random.randint(50, 150)
    database.update_pet(user, coins=pet[7] + reward)
    await ctx.send(embed=make_embed("🏹 Hunt", f"You earned **{reward}** coins!", discord.Color.orange()))

# ================= SHOP =================
@bot.command()
async def shop(ctx):
    em = discord.Embed(title="🛒 Pet Shop", color=discord.Color.green())
    for item, price in list(shop_items.items())[:25]:   # Show only first 25 items
        em.add_field(name=item.replace("_", " ").title(), value=f"💰 {price} coins", inline=True)
    await ctx.send(embed=em)

# ================= BUY =================
@bot.command()
async def buy(ctx, item: str):
    user = str(ctx.author.id)
    pet = database.get_pet(user)
    if not pet:
        await ctx.send("❌ You need a pet first!")
        return

    if item not in shop_items:
        await ctx.send("❌ Item not found in shop!")
        return

    price = shop_items[item]
    if pet[7] < price:
        await ctx.send("❌ Not enough coins!")
        return

    database.update_pet(user, coins=pet[7] - price)
    database.add_item(user, item, 1)
    await ctx.send(f"✅ Successfully bought **{item}** for {price} coins!")

# ================= INVENTORY =================
@bot.command()
async def inventory(ctx):
    items = database.get_inventory(str(ctx.author.id))
    if not items:
        await ctx.send("📦 Your inventory is empty!")
        return

    msg = "**Your Inventory:**\n"
    for item, qty in items:
        msg += f"• {item} ×{qty}\n"
    await ctx.send(msg)

# ================= DECAY LOOP =================
async def pet_decay_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        for user in database.get_all_users():
            pet = database.get_pet(user)
            if not pet:
                continue
            hunger = min(100, pet[4] + 5)
            happiness = max(0, pet[5] - 5)
            coins = pet[7]
            if hunger >= 80 or happiness <= 20:
                coins = max(0, coins - 10)
            database.update_pet(user, hunger=hunger, happiness=happiness, coins=coins)
        await asyncio.sleep(300)  # every 5 minutes

# ================= RUN BOT =================
bot.run(TOKEN)

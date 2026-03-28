
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

# ================= UI =================

def bar(value):
filled = "🟩" * (value // 10)
empty = "⬜" * (10 - value // 10)
return filled + empty

def embed(title, desc, color=discord.Color.blue()):
return discord.Embed(title=title, description=desc, color=color)

# ================= PING =================

@bot.event
async def on_message(message):
if message.author.bot:
return

```
await message.channel.send(f"{message.author.mention}", delete_after=2)
await bot.process_commands(message)
```

# ================= SHOP =================

shop_items = {f"item_{i}": random.randint(20, 5000) for i in range(1, 60)}

shop_items.update({
"food": 20, "toy": 30, "super_food": 50,
"mega_food": 80, "ultra_food": 120,
"energy_drink": 100, "xp_boost": 250,
"coin_boost": 200, "legendary_box": 20000
})

# ================= PET SHOP =================

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
await ctx.send(embed("🌟 Pet Simulator", "Use !adopt cat/dog/dragon to start!", discord.Color.green()))

# ================= ADOPT =================

@bot.command()
async def adopt(ctx, species: str):
species = species.lower()

```
if species not in ["cat", "dog", "dragon"]:
    return await ctx.send("❌ Choose: cat/dog/dragon")

if database.get_pet(str(ctx.author.id)):
    return await ctx.send("❌ You already have a pet!")

database.create_pet(str(ctx.author.id), species)
await ctx.send(f"{ctx.author.mention} adopted a **{species}**!")
```

# ================= PET =================

@bot.command()
async def pet(ctx):
pet = database.get_pet(str(ctx.author.id))
if not pet:
return await ctx.send("❌ No pet!")

```
evo = get_evolution(pet[1], pet[2])

em = discord.Embed(title=f"{ctx.author.name}'s Pet 🐾", color=discord.Color.purple())
em.add_field(name="Species", value=pet[1])
em.add_field(name="Evolution", value=evo)
em.add_field(name="Level", value=f"{pet[2]} (XP {pet[3]}/100)", inline=False)
em.add_field(name="Hunger", value=bar(pet[4]), inline=False)
em.add_field(name="Happiness", value=bar(pet[5]), inline=False)
em.add_field(name="Energy", value=bar(pet[6]), inline=False)
em.add_field(name="Coins", value=f"💰 {pet[7]}")

await ctx.send(embed=em)
```

# ================= FEED =================

@bot.command()
async def feed(ctx):
pet = database.get_pet(str(ctx.author.id))
if not pet:
return await ctx.send("❌ No pet!")

```
database.update_pet(str(ctx.author.id),
    hunger=max(0, pet[4]-15),
    xp=pet[3]+15
)
await ctx.send("🍖 Fed!")
```

# ================= PLAY =================

@bot.command()
async def play(ctx):
pet = database.get_pet(str(ctx.author.id))
if not pet:
return await ctx.send("❌ No pet!")

```
database.update_pet(str(ctx.author.id),
    happiness=min(100, pet[5]+15),
    energy=max(0, pet[6]-10)
)
await ctx.send("🎾 Played!")
```

# ================= REST =================

@bot.command()
async def rest(ctx):
pet = database.get_pet(str(ctx.author.id))
if not pet:
return await ctx.send("❌ No pet!")

```
database.update_pet(str(ctx.author.id),
    energy=min(100, pet[6]+25)
)
await ctx.send("😴 Resting...")
```

# ================= HUNT =================

@bot.command()
async def hunt(ctx):
pet = database.get_pet(str(ctx.author.id))
if not pet:
return await ctx.send("❌ No pet!")

```
reward = random.randint(50, 150)
database.update_pet(str(ctx.author.id), coins=pet[7]+reward)

await ctx.send(embed("🏹 Hunt", f"You earned 💰 {reward}", discord.Color.orange()))
```

# ================= SPIN =================

@bot.command()
async def spin(ctx):
pet = database.get_pet(str(ctx.author.id))
if not pet:
return await ctx.send("❌ No pet!")

```
if pet[7] < 400:
    return await ctx.send("Need 400 coins!")

result = random.choice(["win", "lose", "jackpot"])

if result == "win":
    coins = pet[7] + 5000
    msg = "🎉 You won 5000!"
elif result == "jackpot":
    coins = pet[7] + 50000
    msg = "🔥 JACKPOT 50000!"
else:
    coins = pet[7] - 400
    msg = "😢 Lost 400"

database.update_pet(str(ctx.author.id), coins=coins)
await ctx.send(msg)
```

# ================= SHOP =================

@bot.command()
async def shop(ctx):
em = discord.Embed(title="🛒 Shop", color=discord.Color.green())

```
for item, price in list(shop_items.items())[:25]:
    em.add_field(name=item, value=f"💰 {price}")

await ctx.send(embed=em)
```

# ================= BUY =================

@bot.command()
async def buy(ctx, item: str):
user = str(ctx.author.id)
pet = database.get_pet(user)

```
if not pet:
    return await ctx.send("❌ No pet!")

if item not in shop_items:
    return await ctx.send("Invalid item!")

if pet[7] < shop_items[item]:
    return await ctx.send("Not enough coins!")

database.update_pet(user, coins=pet[7]-shop_items[item])
database.add_item(user, item, 1)

await ctx.send(f"Bought {item}!")
```

# ================= INVENTORY =================

@bot.command()
async def inventory(ctx):
items = database.get_inventory(str(ctx.author.id))

```
if not items:
    return await ctx.send("Empty!")

msg = "🎒 Inventory\n"
for i, q in items:
    msg += f"{i} x{q}\n"

await ctx.send(msg)
```

# ================= LOOP =================

async def pet_decay_loop():
await bot.wait_until_ready()

```
while not bot.is_closed():
    for user in database.get_all_users():
        pet = database.get_pet(user)
        if not pet:
            continue

        hunger = min(100, pet[4]+5)
        happiness = max(0, pet[5]-5)
        coins = pet[7]

        if hunger >= 80 or happiness <= 20:
            coins = max(0, coins-10)

        database.update_pet(user, hunger=hunger, happiness=happiness, coins=coins)

    await asyncio.sleep(300)
```

bot.run(TOKEN)



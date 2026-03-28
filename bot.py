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

```
filled = "🟩" * (value // 10)
empty = "⬜" * (10 - value // 10)
return filled + empty
```

def make_embed(title, desc, color=discord.Color.blue()):
return discord.Embed(title=title, description=desc, color=color)

# ================= MESSAGE EVENT =================

@bot.event
async def on_message(message):
if message.author.bot:
return

```
await message.channel.send(message.author.mention, delete_after=2)
await bot.process_commands(message)
```

# ================= SHOP =================

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

```
if level >= 20:
    return evolutions[species][3]
elif level >= 10:
    return evolutions[species][2]
elif level >= 5:
    return evolutions[species][1]
else:
    return evolutions[species][0]
```

# ================= READY =================

@bot.event
async def on_ready():
print(f"Logged in as {bot.user}")
bot.loop.create_task(pet_decay_loop())

# ================= START =================

@bot.command()
async def start(ctx):
await ctx.send(embed=make_embed(
"🌟 Pet Simulator",
"Use !adopt cat/dog/dragon to start!",
discord.Color.green()
))

# ================= ADOPT =================

@bot.command()
async def adopt(ctx, species: str):
species = species.lower()
user = str(ctx.author.id)

```
if species not in ["cat", "dog", "dragon"]:
    await ctx.send("Choose: cat/dog/dragon")
    return

if database.get_pet(user):
    await ctx.send("You already have a pet!")
    return

database.create_pet(user, species)
await ctx.send(f"{ctx.author.mention} adopted a {species}!")
```

# ================= PET =================

@bot.command()
async def pet(ctx):
pet = database.get_pet(str(ctx.author.id))

```
if not pet:
    await ctx.send("No pet!")
    return

evo = get_evolution(pet[1], pet[2])

em = discord.Embed(title="🐾 Your Pet", color=discord.Color.purple())
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
user = str(ctx.author.id)
pet = database.get_pet(user)

```
if not pet:
    await ctx.send("No pet!")
    return

hunger = max(0, pet[4] - 15)
xp = pet[3] + 15
level = pet[2]

if xp >= 100:
    xp = 0
    level += 1

database.update_pet(user, hunger=hunger, xp=xp, level=level)
await ctx.send("Fed your pet!")
```

# ================= PLAY =================

@bot.command()
async def play(ctx):
user = str(ctx.author.id)
pet = database.get_pet(user)

```
if not pet:
    await ctx.send("No pet!")
    return

happiness = min(100, pet[5] + 15)
energy = max(0, pet[6] - 10)

database.update_pet(user, happiness=happiness, energy=energy)
await ctx.send("Played with pet!")
```

# ================= REST =================

@bot.command()
async def rest(ctx):
user = str(ctx.author.id)
pet = database.get_pet(user)

```
if not pet:
    await ctx.send("No pet!")
    return

energy = min(100, pet[6] + 25)
database.update_pet(user, energy=energy)

await ctx.send("Pet is resting...")
```

# ================= HUNT =================

@bot.command()
async def hunt(ctx):
user = str(ctx.author.id)
pet = database.get_pet(user)

```
if not pet:
    await ctx.send("No pet!")
    return

reward = random.randint(50, 150)
database.update_pet(user, coins=pet[7] + reward)

await ctx.send(embed=make_embed("Hunt", f"You earned {reward} coins!", discord.Color.orange()))
```

# ================= SHOP =================

@bot.command()
async def shop(ctx):
em = discord.Embed(title="Shop", color=discord.Color.green())

```
count = 0
for item, price in shop_items.items():
    em.add_field(name=item, value=f"{price} coins")
    count += 1
    if count >= 25:
        break

await ctx.send(embed=em)
```

# ================= BUY =================

@bot.command()
async def buy(ctx, item: str):
user = str(ctx.author.id)
pet = database.get_pet(user)

```
if not pet:
    await ctx.send("No pet!")
    return

if item not in shop_items:
    await ctx.send("Invalid item!")
    return

price = shop_items[item]

if pet[7] < price:
    await ctx.send("Not enough coins!")
    return

database.update_pet(user, coins=pet[7] - price)
database.add_item(user, item, 1)

await ctx.send(f"Bought {item}!")
```

# ================= INVENTORY =================

@bot.command()
async def inventory(ctx):
items = database.get_inventory(str(ctx.author.id))

```
if not items:
    await ctx.send("Inventory empty!")
    return

msg = "Inventory:\n"
for item, qty in items:
    msg += f"{item} x{qty}\n"

await ctx.send(msg)
```

# ================= DECAY LOOP =================

async def pet_decay_loop():
await bot.wait_until_ready()

```
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

    await asyncio.sleep(300)
```

# ================= RUN =================

bot.run(TOKEN)

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
shop_items = {
    "food": 20,
    "toy": 30,
    "super_food": 50,
    "mega_food": 100,
    "energy_drink": 120,
    "xp_boost": 250,
    "coin_boost": 200,
    "legendary_box": 20000
}

# Add 15 random mystery items
for i in range(1, 16):
    shop_items[f"mystery_{i}"] = random.randint(300, 2500)

# Add some random items (max 20)
for i in range(1, 21):
    shop_items[f"item_{i}"] = random.randint(100, 3000)

# ================= PET SHOP =================
pet_shop = {
    "fox": 30000,
    "wolf": 50000,
    "lion": 80000,
    "tiger": 120000,
    "Unicorn": 500000
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
    desc = (
        "🌟 **Welcome to Pet Simulator RPG!**\n\n"
        "👣 **Step 1: Adopt your pet**\n"
        "`!adopt cat`  |  `!adopt dog`  |  `!adopt dragon`\n\n"
        "🍖 **Step 2: Take care of your pet**\n"
        "`!feed` → Reduce hunger + Gain XP\n"
        "`!play` → Increase happiness\n"
        "`!rest` → Restore energy\n\n"
        "📊 **Step 3: Check your pet**\n"
        "`!pet`\n\n"
        "🛒 **Step 4: Shop & Buy items**\n"
        "`!shop` → View shop\n"
        "`!buy <item>` → Buy food, toy, etc.\n\n"
        "🎒 **Step 5: Check Inventory**\n"
        "`!inventory`\n\n"
        "⚔️ **Step 6: Battle (Coming Soon)**\n"
        "`!battle @user`\n\n"
        "💎 **Step 7: Pet Shop**\n"
        "`!petshop` → Buy rare pets\n\n"
        "🏆 **Goal:** Level up, evolve your pet, earn coins & become #1!\n\n"
        "🔥 **Good luck, Trainer!** 🐾"
    )

    await ctx.send(embed=make_embed(
        "🌟 Pet Simulator RPG",
        desc,
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
        await ctx.send(f"{ctx.author.mention} ❌ You don't have a pet yet! Use `!adopt`")
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
    
    await ctx.send(f"{ctx.author.mention}", embed=em)

# ================= FEED =================
@bot.command()
@commands.cooldown(1, 12, commands.BucketType.user)
async def feed(ctx):
    user = str(ctx.author.id)
    pet = database.get_pet(user)
    if not pet:
        await ctx.send(f"{ctx.author.mention} ❌ No pet found!")
        return
    
    hunger = max(0, pet[4] - 15)
    xp = pet[3] + 15
    level = pet[2]
    
    if xp >= 100:
        xp = 0
        level += 1
    
    database.update_pet(user, hunger=hunger, xp=xp, level=level)
    await ctx.send(f"{ctx.author.mention} 🍖 Fed your pet! +15 XP")

# ================= PLAY =================
@bot.command()
@commands.cooldown(1, 19, commands.BucketType.user)
async def play(ctx):
    user = str(ctx.author.id)
    pet = database.get_pet(user)
    if not pet:
        await ctx.send(f"{ctx.author.mention} ❌ No pet found!")
        return
    
    happiness = min(100, pet[5] + 15)
    energy = max(0, pet[6] - 10)
    
    database.update_pet(user, happiness=happiness, energy=energy)
    await ctx.send(f"{ctx.author.mention} 🎾 Played with your pet!")

# ================= REST =================
@bot.command()
@commands.cooldown(1, 20, commands.BucketType.user)
async def rest(ctx):
    user = str(ctx.author.id)
    pet = database.get_pet(user)
    if not pet:
        await ctx.send(f"{ctx.author.mention} ❌ No pet found!")
        return
    
    energy = min(100, pet[6] + 25)
    database.update_pet(user, energy=energy)
    await ctx.send(f"{ctx.author.mention} 😴 Your pet is resting...")

# ================= HUNT =================
@bot.command()
@commands.cooldown(1, 19, commands.BucketType.user)
async def hunt(ctx):
    user = str(ctx.author.id)
    pet = database.get_pet(user)
    if not pet:
        await ctx.send(f"{ctx.author.mention} ❌ No pet found!")
        return
    
    reward = random.randint(50, 150)
    database.update_pet(user, coins=pet[7] + reward)
    
    # Updated embed with mention
    embed = make_embed(
        "🏹 Hunt", 
        f"You earned **{reward}** coins!", 
        discord.Color.orange()
    )
    await ctx.send(f"{ctx.author.mention}", embed=embed)
# ================= SHOP =================
@bot.command()
async def shop(ctx):
    em = discord.Embed(
        title="🛒 Pet Shop",
        description="Use `!buy <item_name>` to purchase items.\nExample: `!buy food` or `!buy mystery_3`",
        color=discord.Color.green()
    )

    # Special Items First (Nice & Useful)
    special = ["food", "toy", "super_food", "mega_food", "energy_drink", 
               "xp_boost", "coin_boost", "legendary_box"]

    for item in special:
        if item in shop_items:
            name = item.replace("_", " ").title()
            price = shop_items[item]
            em.add_field(name=f"**{name}**", value=f"💰 **{price}** coins", inline=True)

    # Mystery Items
    em.add_field(name="──────────────────", value="**Mystery Items**", inline=False)

    for item, price in shop_items.items():
        if item.startswith("mystery_"):
            name = item.replace("_", " ").title()
            em.add_field(name=name, value=f"💰 {price} coins", inline=True)

    em.set_footer(text="Tip: After buying, use !use <item> to use it on your pet!")
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
        await ctx.send(f"{ctx.author.mention} 📦 Your inventory is empty!")
        return
    
    msg = f"**{ctx.author.display_name}'s Inventory:**\n"
    for item, qty in items:
        msg += f"• {item} ×{qty}\n"
    
    await ctx.send(f"{ctx.author.mention}\n{msg}")

# ================= USE ITEM =================
@bot.command()
async def use(ctx, item: str):
    user = str(ctx.author.id)
    pet = database.get_pet(user)
    if not pet:
        await ctx.send(f"{ctx.author.mention} ❌ You don't have a pet!")
        return
    
    # Check if user has the item
    inventory = database.get_inventory(user)
    item_qty = next((qty for it, qty in inventory if it == item), 0)
    
    if item_qty <= 0:
        await ctx.send(f"{ctx.author.mention} ❌ You don't have **{item}** in your inventory!")
        return
    
    # Remove 1 quantity from inventory
    database.remove_item(user, item, 1)

    # Apply effects based on item
    if item == "food":
        hunger = max(0, pet[4] - 25)
        xp = pet[3] + 10
        database.update_pet(user, hunger=hunger, xp=xp)
        await ctx.send(f"{ctx.author.mention} 🍖 Fed your pet! Hunger -25 | +10 XP")

    elif item == "super_food":
        hunger = max(0, pet[4] - 40)
        xp = pet[3] + 25
        database.update_pet(user, hunger=hunger, xp=xp)
        await ctx.send(f"{ctx.author.mention} 🍗 Super Food used! Hunger -40 | +25 XP")

    elif item == "mega_food":
        hunger = max(0, pet[4] - 60)
        xp = pet[3] + 40
        database.update_pet(user, hunger=hunger, xp=xp)
        await ctx.send(f"{ctx.author.mention} 🍔 Mega Food used! Hunger -60 | +40 XP")

    elif item == "toy":
        happiness = min(100, pet[5] + 30)
        database.update_pet(user, happiness=happiness)
        await ctx.send(f"{ctx.author.mention} 🧸 Played with toy! Happiness +30")

    elif item == "energy_drink":
        energy = min(100, pet[6] + 40)
        database.update_pet(user, energy=energy)
        await ctx.send(f"{ctx.author.mention} ⚡ Energy Drink used! Energy +40")

    elif item == "xp_boost":
        xp = pet[3] + 50
        level = pet[2]
        if xp >= 100:
            xp -= 100
            level += 1
        database.update_pet(user, xp=xp, level=level)
        await ctx.send(f"{ctx.author.mention} ✨ XP Boost used! +50 XP")

    elif item == "coin_boost":
        coins = pet[7] + 150
        database.update_pet(user, coins=coins)
        await ctx.send(f"{ctx.author.mention} 💎 Coin Boost used! +150 coins")

    else:
        # For mystery items - random small effect
        effect = random.choice(["hunger", "happiness", "energy"])
        if effect == "hunger":
            database.update_pet(user, hunger=max(0, pet[4] - 20))
            await ctx.send(f"{ctx.author.mention} 🎁 Mystery item used! Hunger reduced a bit.")
        elif effect == "happiness":
            database.update_pet(user, happiness=min(100, pet[5] + 20))
            await ctx.send(f"{ctx.author.mention} 🎁 Mystery item used! Happiness increased.")
        else:
            database.update_pet(user, energy=min(100, pet[6] + 20))
            await ctx.send(f"{ctx.author.mention} 🎁 Mystery item used! Energy restored.")

    await ctx.send(f"{ctx.author.mention} ✅ Successfully used **{item}**!")


# ================= PET SHOP =================
@bot.command()
async def petshop(ctx):
    em = discord.Embed(
        title="💎 Premium Pet Shop",
        description="Buy rare pets here!\nUse `!buypet <pet_name>` to purchase.",
        color=discord.Color.gold()
    )
   
    for pet_name, price in pet_shop.items():
        name = pet_name.capitalize()
        em.add_field(
            name=f"**{name}**",
            value=f"💰 **{price}** coins\n`!buypet {pet_name}`",
            inline=False
        )
   
    em.set_footer(text="Note: Buying a new pet will replace your current one!")
    await ctx.send(embed=em)


# ================= BUY PET =================
@bot.command()
async def buypet(ctx, species: str):
    species = species.lower()
    user = str(ctx.author.id)
    pet = database.get_pet(user)

    if species not in pet_shop:
        await ctx.send("❌ Invalid pet! Available: fox, wolf, lion, tiger")
        return

    price = pet_shop[species]

    if not pet:
        await ctx.send("❌ You need to adopt a basic pet first using `!adopt`!")
        return

    if pet[7] < price:
        await ctx.send(f"❌ Not enough coins! You need **{price}** coins.")
        return

    # Replace current pet with new one (reset to level 1)
    database.create_pet(user, species)

    await ctx.send(f"🎉 {ctx.author.mention} successfully bought a **{species}** for **{price}** coins!\n"
                   f"Your new pet is now a **{species.capitalize()}**! 🐾")

# ================= BATTLE =================
@bot.command()
async def battle(ctx, opponent: discord.Member = None):
    if not opponent:
        await ctx.send(f"{ctx.author.mention} ❌ Please mention a user to battle! Example: `!battle @user`")
        return
    
    if opponent == ctx.author:
        await ctx.send(f"{ctx.author.mention} ❌ You can't battle yourself!")
        return

    user1 = str(ctx.author.id)
    user2 = str(opponent.id)

    pet1 = database.get_pet(user1)
    pet2 = database.get_pet(user2)

    if not pet1:
        await ctx.send(f"{ctx.author.mention} ❌ You don't have a pet!")
        return
    if not pet2:
        await ctx.send(f"{opponent.mention} ❌ They don't have a pet yet!")
        return

    # Simple stats calculation
    def get_stats(pet):
        level = pet[2]
        evo = get_evolution(pet[1], level)
        
        # Base stats + level bonus
        attack = 20 + level * 3 + (10 if "Tiger" in evo or "Dragon" in evo or "Wolf" in evo else 0)
        defense = 15 + level * 2
        hp = 80 + level * 5
        speed = 10 + level * 1
        
        return {"name": pet[1].capitalize(), "evo": evo, "hp": hp, "max_hp": hp, 
                "attack": attack, "defense": defense, "speed": speed}

    stats1 = get_stats(pet1)
    stats2 = get_stats(pet2)

    # Battle Simulation
    hp1 = stats1["hp"]
    hp2 = stats2["hp"]

    battle_log = []
    turn = 1

    while hp1 > 0 and hp2 > 0 and turn <= 15:  # Max 15 turns
        # Pet 1 attacks
        damage1 = max(5, stats1["attack"] - stats2["defense"] // 2)
        hp2 -= damage1
        battle_log.append(f"**Turn {turn}:** {ctx.author.display_name}'s **{stats1['evo']}** dealt **{damage1}** damage!")

        if hp2 <= 0:
            break

        # Pet 2 attacks
        damage2 = max(5, stats2["attack"] - stats1["defense"] // 2)
        hp1 -= damage2
        battle_log.append(f"**Turn {turn}:** {opponent.display_name}'s **{stats2['evo']}** dealt **{damage2}** damage!")

        turn += 1

    # Determine Winner
    if hp1 > 0 and hp2 <= 0:
        winner = ctx.author
        loser = opponent
        reward = random.randint(80, 200)
        database.update_pet(user1, coins=pet1[7] + reward, xp=pet1[3] + 25)
        result = f"🏆 **{winner.display_name} WINS!** +{reward} coins & +25 XP"
        color = discord.Color.green()
    elif hp2 > 0 and hp1 <= 0:
        winner = opponent
        loser = ctx.author
        reward = random.randint(80, 200)
        database.update_pet(user2, coins=pet2[7] + reward, xp=pet2[3] + 25)
        result = f"🏆 **{winner.display_name} WINS!** +{reward} coins & +25 XP"
        color = discord.Color.green()
    else:
        result = "🤝 **It's a Draw!** Both pets fought well."
        color = discord.Color.gold()

    # Create Battle Embed
    em = discord.Embed(title="⚔️ Pet Battle Arena", description=result, color=color)
    
    em.add_field(
        name=f"{ctx.author.display_name}'s Pet",
        value=f"**{stats1['evo']}**\nHP: `{max(0, hp1)}/{stats1['max_hp']}`\nAttack: `{stats1['attack']}`",
        inline=True
    )
    em.add_field(
        name=f"{opponent.display_name}'s Pet",
        value=f"**{stats2['evo']}**\nHP: `{max(0, hp2)}/{stats2['max_hp']}`\nAttack: `{stats2['attack']}`",
        inline=True
    )

    em.add_field(name="Battle Log", value="\n".join(battle_log[-8:]) or "Battle started...", inline=False)
    
    await ctx.send(f"{ctx.author.mention} vs {opponent.mention}", embed=em)

# ================= COMMAND ERROR HANDLER (Cooldown) =================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        # Calculate remaining time
        remaining = round(error.retry_after)
        
        msg = await ctx.send(
            f"{ctx.author.mention} ⏳ This command is on cooldown!\n"
            f"Please wait **{remaining} seconds** before using it again."
        )
        # Auto delete the message after 5 seconds
        await asyncio.sleep(5)
        await msg.delete()
        
    # Optional: Uncomment if you want to see other errors in console
    # else:
    #     raise error

# ================= DECAY LOOP =================
async def pet_decay_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        for user in database.get_all_users():
            pet = database.get_pet(user)
            if not pet:
                continue
            hunger = min(10000, pet[4] + 5)
            happiness = max(0, pet[5] - 5)
            coins = pet[7]
            if hunger >= 80 or happiness <= 20:
                coins = max(0, coins - 10)
            database.update_pet(user, hunger=hunger, happiness=happiness, coins=coins)
        await asyncio.sleep(300)  # every 5 minutes

# ================= RUN BOT =================
bot.run(TOKEN)

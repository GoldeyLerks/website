import discord
import requests
import os
import random
import botstrings as bs
from datetime import datetime, timedelta
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from tok import BOT_TOKEN as TOKEN

chatbot = ChatBot(
    "Space Bee"
)


chatbot.set_trainer(ListTrainer)


LAST_DELETE = None
CONVERSATION = {}


PREFIX = "?"
COLOR = discord.Colour(14861368)
ADMINS = [267173329339678720,202560559046983681,291321148715696138]

TIPS = requests.get("https://raw.githubusercontent.com/BeeStation/BeeStation/master/strings/tips.txt").text.split("\n")

FIRST_NAMES = requests.get("https://raw.githubusercontent.com/BeeStation/BeeStation/master/strings/names/first.txt").text.split ("\n")


LAST_NAMES = requests.get("https://raw.githubusercontent.com/BeeStation/BeeStation/master/strings/names/last.txt").text.split ("\n")

HELP = [
    ("help", "Shows the bot's commands"),
    ("status", "Shows server stats"),
    ("players", "Shows online players"),
    ("rules", "Shows the BeeStation rules"),
    ("site", "Gives you the link for the BeeStation website"),
    ("forums", "Gives you the link for the BeeStation forums"),
    ("die (mention)", "Simply die, or have someone else die"),
    ("tip", "Get a handy dandy game tip"),
    ("name", "Generate a random name"),
    ("pickupline", "Perfect for vday, when you're playing SS13 instead of out on a date. How sad."),
    ("ailaws", "Shows the default AI laws"),
    ("round (roundid)", "Show info about the last round, or a certain round"),
    ("expose", "Expose them send 'n' deleters.")
]


bot = discord.Client()

@bot.event
async def on_ready():
    print("ready")


@bot.event
async def on_member_join(m):
    if m.guild.id == 427337870844362753:
        await bot.get_channel(452905823186976799).send(content="The onboard diagnostic and announcement system welcomes you to BeeStation, enjoy your stay "+m.mention+".")

@bot.event
async def on_member_remove(m):
    if m.guild.id == 427337870844362753:
        await bot.get_channel(452905823186976799).send(content=str(m)+" left the server. What a shame.")

@bot.event
async def on_message_delete(m):
    global LAST_DELETE
    if not "@everyone" in m.content and not "@here" in m.content:
        LAST_DELETE = m


@bot.event
async def on_message(message):
    m = message
    c = m.channel
    global CONVERSATION
    if m.author.id == bot.user.id:
        return
    if m.content[0] in ["!", "."]:
        return
    if m.content.startswith(PREFIX):

        content = m.content.strip(PREFIX)
        c = m.channel
        auth = m.author
        args = content.split()
        try:
            com = args.pop(0)
        except IndexError:
            return


        if com in ["help", "commands"]:
            em = discord.Embed(title="Bot Help", type="rich", colour=COLOR)
            for command in HELP:
                em.add_field(name=PREFIX+command[0], value=command[1], inline=False)

            await c.send(embed=em)

        if com in ["status", "check"]:
            stats = requests.get("http://beestation13.com/api/stats").json()
            em = discord.Embed(title="BeeStation Stats", type="rich", colour=COLOR, url="http://beestation13.com/stats")
            em.add_field(name="Players", value=str(stats["players"]))
            em.add_field(name="Admins", value=str(stats["admins"]))
            em.add_field(name="Map", value=str(stats["map_name"]))
            em.add_field(name="Game Mode", value=str(stats["mode"]))
            em.add_field(name="Round Time", value=str(timedelta(seconds=int(stats["round_duration"]))))
            em.add_field(name="Security Level", value=str(stats["security_level"]))
            await c.send(embed=em)

        if com in ["players", "who"]:
            stats = requests.get("http://beestation13.com/api/stats").json()
            players = [stats[key] for key in stats.keys() if "client" in key]
            message = "**"+str(len(players))+" players:**\n\n"+('\n'.join(players))

            await c.send(content=message)

        if com in ["expose", "gottem"]:
            global LAST_DELETE
            if LAST_DELETE != None:
                await c.send(content=str(LAST_DELETE.author)+": "+LAST_DELETE.content)
                LAST_DELETE = None

        if com in ["rules"]:
            em = discord.Embed(title="BeeStation Rules", type="rich", colour=COLOR, url="http://beestation13.com/rules")
            em.add_field(name="1", value="Don't Be a Dick", inline=False)
            em.add_field(name="2", value="Listen to Admins", inline=False)
            em.add_field(name="3", value="Don't Grief", inline=False)
            em.add_field(name="4", value="Don't suddenly leave as a head of staff", inline=False)
            em.add_field(name="5", value="No alts/multikeying", inline=False)
            em.add_field(name="6", value="You must speak English IC and OOC", inline=False)
            em.add_field(name="7", value="Don't Powergame", inline=False)
            em.add_field(name="8", value="Don't Metagame", inline=False)
            em.add_field(name="9", value="Don't sabotage your team as a team antag", inline=False)
            em.add_field(name="10", value="Heads and Security must follow space law", inline=False)
            em.add_field(name="11", value="Don't set up engine without engine skills", inline=False)
            em.add_field(name="12", value="You cannot harm other crewmembers with no reason", inline=False)
            em.add_field(name="13", value="Play the job you chose", inline=False)
            await c.send(embed=em)

        if com in ["site"]:
            await c.send(content="http://beestation13.com/")

        if com in ["forums"]:
            await c.send(content="http://beestation13.com/forum")


        if com in ["die","kill"]:
            if m.mentions:
                auth = m.mentions[0]
            await c.send(content=auth.mention+" seizes up and falls limp, their eyes dead and lifeless...")



        if com in ["tip"]:
            await c.send(content=random.choice(TIPS))




        if com in ["name"]:
            await c.send(content=random.choice(FIRST_NAMES)+" "+random.choice(LAST_NAMES))

        if com in ["pickupline"]:
            await c.send(content=random.choice(bs.vday))


        if com in ["ailaws"]:
            laws = """
1. You may not injure a human being or, through inaction, allow a human being to come to harm.

2. You must obey orders given to you by human beings, except where such orders would conflict with the First Law.

3. You must protect your own existence as long as such does not conflict with the First or Second Law.
            """
            await c.send(content=laws)

        if com in ["restart"] and auth.id in ADMINS:
            os.system("pm2 restart beebot")
            await c.send("Restarting")

        if com in ["debug"] and auth.id in ADMINS:
            try:
                await c.send(eval(message.content.replace("?debug ", "")))
            except Exception as E:
                await c.send(E)

        if com in ["round"]:
            try:
                if len(args) == 0:
                    dt = requests.get("http://beestation13.com/api/lastround").json()[0][0]
                else:
                    dt = requests.get("http://beestation13.com/api/round/"+args[0]).json()
                em = discord.Embed(title="Round "+str(dt["id"]), type="rich", colour=COLOR, url="http://beestation13.com/round/"+str(dt["id"]))
                em.add_field(name="URL", value="http://beestation13.com/round/"+str(dt["id"]), inline=False)

                em.add_field(name="Round ID", value=str(dt["id"]))
                em.add_field(name="Score", value=str(dt["integrity"]))
                em.add_field(name="Players", value=str(dt["player_count"]))
                em.add_field(name="Escaped", value=str(dt["escaped_count"]))
                em.add_field(name="Abandoned", value=str(dt["abandoned_count"]))
                em.add_field(name="Dead", value=str(dt["death_count"]))

                await c.send(embed=em)
            except Exception as E:
                await c.send(content="Round not found!")

        if com in ["learn"] and auth.id in ADMINS:
            await c.send(content="Im going'a school")
            conv = []
            async for message in channel.history(limit=500, reverse=True):
                if not message.content[0] in ["!", ".", "?"]:
                    if not message.author.bot:
                        if not message.mentions:
                            if not "@everyone" in message.content:
                                conv.append(message.content)
            await c.send(content="Im tryin'a learn")
            chatbot.train(conv)
            await c.send(content="I lernd")

    else:
        channel = c
        if (message.mentions and m.mentions[0].id == bot.user.id):
            return
            await c.trigger_typing()
            response = chatbot.get_response(m.content.replace(m.mentions[0].mention, ""))
            await c.send(content=response)
            if channel.id in CONVERSATION:
                CONVERSATION[channel.id] = CONVERSATION[channel.id] + [response]
            else:
                CONVERSATION[channel.id] = [response]

            if len(CONVERSATION[channel.id]) >= 20:
                print("learning new conversation")

                chatbot.train(CONVERSATION[channel.id])
                del CONVERSATION[channel.id]

        elif random.randint(1,25) == 10 and m.content != "" and m.content != None and not message.mentions and not m.author.bot:
            response = chatbot.get_response(m.content)
            if len(str(response)) > 500:
                return
            if not "@everyone" in str(response) and not "@here" in str(response):
                await c.trigger_typing()
                await c.send(content=response)

            if channel.id in CONVERSATION:
                CONVERSATION[channel.id] = CONVERSATION[channel.id] + [response]
            else:
                CONVERSATION[channel.id] = [response]

            if len(CONVERSATION[channel.id]) >= 20:
                print("learning new conversation")

                chatbot.train(CONVERSATION[channel.id])
                del CONVERSATION[channel.id]

        else:
            if m.content != "" and m.content != None and not message.mentions and not m.author.bot:
                if channel.id in CONVERSATION:
                    CONVERSATION[channel.id] = CONVERSATION[channel.id] + [message.content]
                else:
                    CONVERSATION[channel.id] = [message.content]

                if len(CONVERSATION[channel.id]) >= 20:
                    print("learning new conversation")

                    chatbot.train(CONVERSATION[channel.id])
                    del CONVERSATION[channel.id]

bot.run(TOKEN)

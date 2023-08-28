import discord
import asyncio
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender = os.getenv("Mail")
password = os.getenv("MailPssw")

intents = discord.Intents.default()  # This enables the default intents
intents.presences = True
intents.message_content = True
intents.guilds = True

intents.members = True
intents.voice_states = True
intents.guilds = True

save = []
emailToUser = {}


def removelist(item):
    save.remove(item)


def clearlist():
    print("cleared list (saved)")
    save.clear()


def removelist(item):
    save.remove(item)


async def tryEveryone(channel):
    global save
    if "@everyone" in save:
        save.clear()
        members = channel.members
        # mention_list = [member.mention for member in members]
        for text in members:
            if not text.bot:
                save.append(text.mention)


async def tryHere(channel):
    global save
    if "@here" in save:
        save.clear()
        members = channel.members
        for text in members:
            if not text.bot or text.status != "offline" or text.status != "dnd":
                save.append(text.mention)


async def send_private_mail(channel, client, important_message, clean, link):
    for text in save:
        await channel.send(f"{text} got informed")

        last_colon_index = text.rfind("@")
        mm = text[last_colon_index + 1 :].strip()
        idraw = mm.replace(">", "")

        for key in emailToUser:
            if str(key) in idraw:
                receiver = emailToUser[key]
                subject = "Important Message - Discord Reminder - Margelo Bot"

                msg = MIMEMultipart()

                msg["From"] = sender
                msg["To"] = receiver
                msg["subject"] = subject

                body = f"Here is the Link to the Conversation you have missed:\n{link}\n\n{clean}"

                msg.attach(MIMEText(body, "plain"))

                text = msg.as_string()

                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender, password)

                server.sendmail(sender, receiver, text)
                print("Email has been sent!")

        user = await client.fetch_user(idraw)

    try:
        if user:
            response = (
                f"----------------------Reminder----------------------\n"
                f"Here is the Link to the Conversation you have missed:\n{link}\n"
                f"\n{important_message}"
            )
            await user.send(response)

            save.remove(user)
    except Exception as e:
        print(e)


def run_discord_bot():
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"{client.user} is now running!")
        print(f"{client.user} is now running!")
        print(f"{client.user} is now running!")

    @client.event
    async def on_message(message):
        usermessage = str(message.content)

        if usermessage == "!help":
            await message.channel.send(
                f"```*What does this bot do?\n The main purpose of the Margelo-Bot is to make important \n messages hard to overlook. \n\n*Commands: \n !help -> shows currently available commands \n !email your@mail.com -> makes you reachable via email \n !allemails -> shows all emails given to the bot \n \n*Reactions:\n ⚠️ -> makes a message important \n ✅ -> confirms that you've seen the message\n \n*Contact me:\n -if you find bugs\n -or have feature requests \n -Discord: montchy``` "
            )

        if usermessage.startswith("!email"):
            sps = message.content.split(" ")
            mail = sps[1]
            messauth = message.author.id
            if "@" in mail and "." in mail:
                await message.channel.send(f"{mail} works!")
                emailToUser[messauth] = mail
            else:
                await message.channel.send(f"{mail} does not work!")

        if usermessage == "!allemails":
            await message.channel.send("Current Emails:")
            for key in emailToUser:
                try:
                    user = await client.fetch_user(key)
                    await message.channel.send(
                        f"User: {user.mention} | Email: {emailToUser[key]}"
                    )

                except Exception as e:
                    await message.channel.send(
                        f"User: {key} | Email: {emailToUser[key]}"
                    )
                    print(e)

    @client.event
    async def on_reaction_add(reaction, user):
        message = reaction.message.content
        cleanmessage = reaction.message.clean_content
        message_link = f"https://discord.com/channels/{reaction.message.guild.id}/{reaction.message.channel.id}/{reaction.message.id}"

        if reaction.emoji == "⚠️":
            af_space = message.split(" ")
            af_space = [text for text in af_space if "@" in text]
            for text in af_space:
                save.append(text)
            bstring = f"I will message {af_space} within 24 hours if they do not respond to this message."
            response = await reaction.message.channel.send(bstring)
            await tryEveryone(reaction.message.channel)
            await tryHere(reaction.message.channel)
            await response.add_reaction("✅")
            await asyncio.sleep(86400)  # ein tag (24*60*60)
            await send_private_mail(
                reaction.message.channel, client, message, cleanmessage, message_link
            )
            await reaction.message.channel.send(f"Time for {message_link} is up!")
            clearlist()

        if reaction.message.author == client.user:
            if reaction.emoji == "✅":
                if user.mention in save:
                    removelist(user.mention)
                    response = f"{user.mention} will not be messaged"
                    await reaction.message.channel.send(response)

    client.run(os.getenv("TOKEN"))

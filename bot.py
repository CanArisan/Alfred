import asyncio
import os
import random
import audioread
import discord

from english_words import english_words_set
from dotenv import load_dotenv
from discord.ext import commands
from YTDLSource import YTDLSource

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILDS = os.getenv('DISCORD_GUILDS').split(',')
MY_USER = os.getenv('MY_USER')
MY_NAME = os.getenv('MY_NAME')
UPDATE_NOTIFICATION_GUILD = os.getenv('UPDATE_NOTIFICATION_GUILD')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

commands_active = True

username_map = {}
for pair in os.getenv('USERS').split(','):
    mapping = pair.split(':')
    username_map[mapping[0]] = mapping[1]

playlist_dict = {}
for pair in os.getenv('PLAYLISTS').split(','):
    mapping = pair.split(';')
    playlist_dict[mapping[0]] = mapping[1]

with open('hangman_visual.txt', 'r') as f:
    hangman_visuals = f.read().split(':')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    server = discord.utils.get(bot.guilds, name=UPDATE_NOTIFICATION_GUILD)
    # Send a message to general text channels
    channel = list(filter(lambda x: 'gene' in x.name, server.channels))[0]
    await channel.send('I was just updated by Master {}.'.format(MY_NAME))


@bot.event
async def on_member_join(member):
    server = member.guild
    # Send a message to the general text channel
    channel = list(filter(lambda x: 'gene' in x.name, server.channels))[0]
    with open(os.path.join('images', 'Welcome.jpeg'), 'rb') as f:
        picture = discord.File(f)
        await channel.send(f'Welcome Master {member.name} to the Wayne Mansion. '
                           f'I am at your service. Type !help to learn about my services.',
                           file=picture)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        if 'I am ready for rock, paper, scissors. Make your selection' in message.content:
            result = await play_rps(message)
            print('Result: {}'.format(result))
    if commands_active:
        await bot.process_commands(message)


@bot.command(name='hello', help='Greet Alfred.', aliases=['hi'])
async def greet(ctx):
    response = 'Hello, I am Alfred Pennyworth. The loyal butler of Bruce Wayne and his friends. At your service.'
    await ctx.send(response)


@bot.command(name='rest', help='Send Alfred to rest. Only Master {} can call him back.'.format(MY_NAME), aliases=['r'])
async def logout(ctx):
    response = 'As you wish. I\'ll be resting until Master {} calls me back.'.format(MY_NAME)
    await ctx.send(response)
    await bot.logout()


@bot.command(name='fall', help='Learn a lesson from wise Alfred Pennyworth.', aliases=['f'])
async def fall(ctx):
    response = 'Why do we fall, Master Wayne? So that we can learn to pick ourselves up.'
    await ctx.send(response)


@bot.command(name='roll', help='Simulates rolling dice. Takes number of dice as an argument.')
async def roll(ctx, number_of_dice: int = 1):
    if number_of_dice > 100 or number_of_dice < 1:
        await ctx.send('I can\'t roll that many dice')
    else:
        dice = [
            str(random.choice(range(1, 7)))
            for _ in range(number_of_dice)
        ]
        await ctx.send(', '.join(dice))


@bot.command(name='rng', help='Returns a random integer between two integers (inclusive).')
async def rng(ctx, fro: int, to: int):
    response = str(random.choice(range(fro, to + 1)))
    await ctx.send(response)


@bot.command(name='image', help='Send a random picture of Alfred.', aliases=['i'])
async def image(ctx):
    image_name = os.path.join('images', '{}.jpeg'.format(str(random.choice(range(1, 4)))))
    with open(image_name, 'rb') as f:
        picture = discord.File(f)
        await ctx.send('Here\'s a picture of me', file=picture)


@bot.command(name='rps', help='Play rock, paper, scissors with Alfred.')
async def rps(ctx):
    await ctx.send('I am ready for rock, paper, scissors. Make your selection Master {}.'
                   .format(username_map.get(ctx.author.name)))


@bot.command(name='groovy', help='Show Spotify playlist links.', aliases=['g'])
async def groovy(ctx):
    message = 'Here are some playlist links, Master {}:\n'.format(username_map.get(ctx.author.name))
    for key in playlist_dict.keys():
        message += '{}:\n'.format(key)
        message += '{}:\n'.format(playlist_dict.get(key))
    await ctx.send(message)


@bot.command(name='me', help='See a picture of yourself with Master {}.'.format(MY_NAME), aliases=['my-pic'])
async def my_pic(ctx):
    image_name = os.path.join('images', '{}.jpeg'.format(username_map.get(ctx.author.name)))
    try:
        with open(image_name, 'rb') as f:
            picture = discord.File(f)
            if ctx.author.name == MY_USER:
                await ctx.send('Here\'s a picture of you, Master {}.'.format(MY_NAME), file=picture)
            else:
                await ctx.send('Hello Master {}. Here\'s a picture of you with Master {}.'
                               .format(username_map.get(ctx.author.name), MY_NAME), file=picture)
    except IOError:
        name = username_map.get(ctx.author.name)
        if name is None:
            await ctx.send('I could not recognize you, Master.', file=picture)
        else:
            await ctx.send('I could not find a picture of you with Master {}, Master {}.'
                           .format(MY_NAME, username_map.get(ctx.author.name)))


@bot.command(name='talk', help='Alfred talks to you', aliases=['t'])
async def talk(ctx):
    user = ctx.author
    # only play music if user is in a voice channel
    if user.voice is not None:
        voice_channel = user.voice.channel
        vc = await voice_channel.connect()
        await ctx.guild.change_voice_state(channel=voice_channel, self_deaf=True)
        filepath = os.path.join('sounds', '{}.mp3'.format(str(random.choice(range(1, 4)))))
        vc.play(discord.FFmpegPCMAudio(filepath))
        with audioread.audio_open(filepath) as f:
            await asyncio.sleep(f.duration + 2)
        await vc.disconnect()
    else:
        await ctx.send('You are not in a voice channel, Master {}.'.format(username_map.get(ctx.author.name)))


@bot.command(name='youtube', help='Alfred plays the youtube video you requested.', aliases=['yt'])
async def youtube(ctx, url):
    print(url)
    user = ctx.author
    if user.voice is not None:
        voice_channel = user.voice.channel
        async with ctx.typing():
            ytdl_response = await YTDLSource.from_url(url, loop=bot.loop)
            player = ytdl_response[0]
            vc = await voice_channel.connect()
            await ctx.guild.change_voice_state(channel=voice_channel, self_deaf=True)
        await ctx.send('Now playing: {}'.format(player.title))
        vc.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await asyncio.sleep(ytdl_response[1] + 2)
        await vc.disconnect()
        os.remove(ytdl_response[2])
        print('File {} Removed.'.format(ytdl_response[2]))
    else:
        await ctx.send('You are not in a voice channel, Master {}.'.format(username_map.get(ctx.author.name)))


@bot.command(name='hangman', help='Play hangman with Alfred.', aliases=['hang'])
async def hangman(ctx):
    global commands_active
    commands_active = False
    await ctx.send('I am ready to play hangman. You have 6 guesses in total.')
    await ctx.send('You can guess a letter by typing it.')
    await ctx.send('I won\'t listen to your other commands until the game ends. To end the game type: end')
    word = random.sample(english_words_set, 1)[0].upper()
    print('My word: {}'.format(word))
    await ctx.send('Here\'s my word: {}\n{}'.format(' '.join(['#' * len(word)]), hangman_visuals[0]))
    await play_hangman(ctx, list(word))
    commands_active = True


async def play_rps(message) -> int:
    rock = '\u270A'
    paper = '\u270B'
    scissors = '\u270C'
    emojis = [rock, paper, scissors]
    for emoji in emojis:
        await message.add_reaction(emoji)
    alfred_selection = emojis[random.choice(range(0, 3))]
    await asyncio.sleep(3)
    player_selection = ''
    for reaction in message.reactions:
        if reaction.count > 1:
            if player_selection == '':
                player_selection = reaction.emoji
            else:
                await message.channel.send('You should have selected only one.')
                return 1
    to_remove = list(filter(lambda e: e != alfred_selection and e != player_selection, emojis))
    for emoji in to_remove:
        await message.clear_reaction(emoji)
    if player_selection != '':
        if alfred_selection == player_selection:
            await message.channel.send('It\'s a draw.')
            return 0
        elif (alfred_selection == rock and player_selection == scissors) or (alfred_selection == scissors and player_selection == paper) or (alfred_selection == paper and player_selection == rock):
            await message.channel.send('I won.')
            return 1
        else:
            await message.channel.send('You won.')
            return 2
    else:
        await message.channel.send('Time\'s up.')
        return -1


async def play_hangman(ctx, word):
    tries = 0
    channel = ctx.message.channel
    current_string = ['#'] * len(word)
    prev_letters = []
    while tries < 6:
        message = channel.last_message
        if message.author == bot.user:
            await asyncio.sleep(0.1)
        else:
            message_content = message.content.upper()
            if len(message_content) == 1:
                if message_content not in prev_letters:
                    prev_letters.append(message_content)
                if message_content in word:
                    for i in range(len(word)):
                        if word[i] == message_content:
                            current_string[i] = message_content
                            if '#' not in current_string:
                                await ctx.send(' '.join(current_string))
                                await ctx.send('You won!')
                                return
                    await ctx.send(hangman_visuals[tries])
                    await ctx.send('Letters tried: {}'.format(','.join(sorted(prev_letters))))
                    await ctx.send(' '.join(current_string))
                else:
                    tries += 1
                    await ctx.send(hangman_visuals[tries])
                    await ctx.send('Letters tried: {}'.format(', '.join(sorted(prev_letters))))
                    await ctx.send(' '.join(current_string))
                    if tries == 6:
                        await ctx.send('Game Over. The word was {}.'.format(''.join(word)))
                        await ctx.invoke(bot.get_command('fall'))
                        return
            elif message_content == 'END':
                await ctx.send('Alright. Game over.')
                return
            else:
                await ctx.send('That was not a letter. Please enter a single letter or type "end" if you are bored.')
    return


bot.run(TOKEN)

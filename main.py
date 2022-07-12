import random
import discord
import requests
from bs4 import BeautifulSoup
import json
from time import sleep
from discord.ext import commands
from config import TOKEN
from threading import Thread
from timeit import default_timer
from youtube_dl import YoutubeDL

vc = None
qe = []
lenght = 0
zero = 0
YDL_OPTIONS = {'format': 'worstaudio/best', 'noplaylist': 'False', 'simulate': 'True',
               'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
client = commands.Bot(command_prefix='GG ')


def wait(ctx, arg, tme=False):
    global lenght, zero, vc
    if tme:
        print(lenght - tme)
        sleep(lenght - tme)
    print(12)
    if arg[-1] == 'txt:true':
        src = ' '.join(arg[:-1])
        text(ctx, src)
    else:
        src = ' '.join(arg)
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{src}", download=False)['entries'][0]
    url = info['formats'][0]['url']
    lenght = info['duration']
    vc.play(discord.FFmpegPCMAudio(executable="bin\\ffmpeg.exe", source=url, **FFMPEG_OPTIONS))
    zero = default_timer()



@client.command()
async def анек(ctx):
    with open('aneks.txt', 'r') as file:
        data = file.read().split('\naboba\n')
        for el in data:
            if not el:
                del data[data.index(el)]
    await ctx.send(random.choice(data))


@client.command(pass_context=True)
async def запоминай_анек(ctx, *args):
    anek = ' '.join(args)
    with open('aneks.txt', 'r') as file:
        data = file.read().split('\naboba\n')
    with open('aneks.txt', mode='a') as file:
        if anek not in data:
            file.write(anek)
            file.write('\naboba\n')
            await ctx.send('запомнил')
        else:
            await ctx.send('уже знаю')


@client.command(pass_context=True)
async def русская_рулетка(ctx, *args):
    rnd = random.randint(1, 6)
    if not 0 < int(args[0]) < 6:
        await ctx.send(f'застрелян за читерство')
        return None
    if rnd == int(args[0]):
        await ctx.send(f'застрелился')
    else:
        await ctx.send(f'стрелял, но не попал. Выпало {rnd}')


@client.command(pass_context=True)
async def text(ctx, *args):
    url = f'https://genius.com/api/search/multi?per_page=5&q={"%20".join(args)}'
    page = requests.get(url)
    url2 = page.text
    try:
        url2 = json.loads(url2)["response"]["sections"][1]["hits"][0]["result"]["url"]
    except:
        await ctx.send("не найдено текста по этому запросу")
        return None
    print(url2)
    page2 = requests.get(url2)
    soup = BeautifulSoup(page2.text, "html.parser")
    res = soup.select_one("#lyrics-root > div.Lyrics__Container-sc-1ynbvzw-6.YYrds")
    autor = soup.select_one(".SongHeaderdesktop__Artist-sc-1effuo1-11")
    embed = discord.Embed(title=f"текст вашей песни:", url="https://realdrewdata.medium.com/", description="```" + autor.get_text() + "\n" + res.get_text("\n") + "```", color=0xa35de0)
    await ctx.send(embed=embed)


@client.command(pass_context=True)
async def брось_кубик(ctx, *args):
    try:
        rd = random.randint(int(args[0]), int(args[1]))
        await ctx.send(f'выпало {rd}')
    except:
        await ctx.send(f'с головой все в порядке?')


@client.command(pass_context=True)
async def play(ctx, *arg, end=False, tm=False):
    global vc, qe
    if end:
        qe.append(arg)
    else:
        qe.insert(0, arg)
    print(arg)
    try:
        vc = await ctx.message.author.voice.channel.connect()
    except:
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_channel.stop()
    while qe:
        th1 = Thread(target=wait, args=[ctx, qe[0], tm])
        th1.start()
        del qe[0]


@client.command()
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.stop()


@client.command()
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.pause()


@client.command()
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.resume()


@client.command()
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()


@client.command(pass_context=True)
async def queue(ctx, *arg):
    global zero
    src = ' '.join(arg)
    await ctx.send('добавлено')
    print(default_timer() - zero)
    await play(ctx, src, end=True, tm=default_timer() - zero)




client.run(TOKEN)

from nextcord.ext import commands
import nextcord, datetime, pytz, wavelink as nextwave, math

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='', intents=intents)

@client.event
async def on_ready():   
    i = datetime.datetime.now()
    print(f"{client.user.name}봇은 준비가 완료 되었습니다.")
    print(f"[!] 참가 중인 서버 : {len(client.guilds)}개의 서버에 참여 중")
    print(f"[!] 이용자 수 : {len(client.users)}와 함께하는 중")
    guild_list = client.guilds
    client.loop.create_task(node_connect())

@client.event
async def on_wavelink_node_ready(node: nextwave.Node):
    print(f"[!] {node.identifier} is ready!")

async def node_connect():
    await client.wait_until_ready()
    await nextwave.NodePool.create_node(bot=client, host='lavalinkinc.ml', port=443, password='incognito', https=True)

@client.event
async def on_voice_state_update(member, before, after):
    if member.id == 봇ID and before.channel is not None and after.channel is None:
        vc: nextwave.Player = member.guild.voice_client
        vc.queue.clear()
        await vc.disconnect()

class music_buttons(nextcord.ui.View):

    def __init__(self):
        super().__init__(timeout=math.inf)
        self.value = None

    @nextcord.ui.button(label = "⏯️-정지/재생", style = nextcord.ButtonStyle.blurple)
    async def pause(self, button : nextcord.ui.Button, inter : nextcord.Interaction):
        if not inter.guild.voice_client:
            return await inter.response.send_message("음성채널에 들어가주세요!", ephemeral=True)
        elif not inter.user.voice:
            return await inter.response.send_message("음성채널에 들어가주세요!", ephemeral=True)
        try:
            if inter.user.voice.channel.id != inter.guild.me.voice.channel.id:
                return await inter.response.send_message("유저님의 음성 채널 봇의 음성 채널이 달라요!", ephemeral=True)
        except:
            return await inter.response.send_message("봇이 음성채널에 없어요!", ephemeral=True)
        vc: nextwave.Player = inter.guild.voice_client
        if vc.is_paused():
            await vc.resume()
            return await inter.response.send_message(f"**{vc.track.title}**을/를 다시 재생 했습니다!", ephemeral=True)
        await vc.pause()
        await inter.response.send_message(f"**{vc.track.title}**을/를 일시정지 했습니다!", ephemeral=True)
    @nextcord.ui.button(label="⏭️-스킵", style=nextcord.ButtonStyle.blurple)
    async def skip(self, button: nextcord.ui.Button, inter:nextcord.Interaction):
        try:
            if inter.user.voice.channel.id != inter.guild.me.voice.channel.id:
                return await inter.response.send_message("유저님의 음성 채널 봇의 음성 채널이 달라요!", ephemeral=True)
        except:
            return await inter.response.send_message("봇이 음성채널에 없거나 유저가 음성채널에 없어요!", ephemeral=True)
        vc: nextwave.Player = inter.guild.voice_client
        try:
            next_song = vc.queue.get()
            await vc.play(next_song)
            return await inter.response.send_message(f"노래가 스킵되었어요! 새로 재생중인 음악 : {next_song}", ephemeral=True)
        except:
            return await inter.response.send_message(f"재생 목록이 비었어요!", ephemeral=True)
    @nextcord.ui.button(label = "🔁-재생목록", style = nextcord.ButtonStyle.green)
    async def queue(self, button : nextcord.ui.Button, inter : nextcord.Interaction):
        try:
            if inter.user.voice.channel.id != inter.guild.me.voice.channel.id:
                return await inter.response.send_message("유저님의 음성 채널 봇의 음성 채널이 달라요!", ephemeral=True)
        except:
            return await inter.response.send_message("봇이 음성채널에 없거나 유저가 음성채널에 없어요!", ephemeral=True)
        vc: nextwave.Player = inter.guild.voice_client
        if vc.queue.is_empty:
            return await inter.send("재생 목록이 비었어요!")
        queue = vc.queue.copy()
        song_count = 0
        msg = ""
        for song in queue:
            song_count += 1
            msg += f"**{song_count}번째 노래** : **{song.title}**\n"
        return await inter.response.send_message(f"재생 목록!\n{msg}", ephemeral=True)
    @nextcord.ui.button(label = "🔁-반복재생", style = nextcord.ButtonStyle.green)
    async def loop(self, button : nextcord.ui.Button, inter : nextcord.Interaction):
        try:
            if inter.user.voice.channel.id != inter.guild.me.voice.channel.id:
                return await inter.response.send_message("유저님의 음성 채널 봇의 음성 채널이 달라요!", ephemeral=True)
        except:
            return await inter.response.send_message("봇이 음성채널에 없거나 유저가 음성채널에 없어요!", ephemeral=True)
        vc: nextwave.Player = inter.guild.voice_client
        if not vc.loop:
            vc.loop ^= True
            await inter.response.send_message(f"이제부터 {vc.track.title}을/를 반복재생 합니다!", ephemeral=True)
        else:
            setattr(vc, "loop", False)
            vc.loop ^= True
            await inter.response.send_message(f"{vc.track.title}을/를 반복을 비활성화 합니다!", ephemeral=True)
        
        self.value = True
    @nextcord.ui.button(label = "⏹️-나가", style = nextcord.ButtonStyle.red)
    async def disconnect(self, button : nextcord.ui.Button, inter : nextcord.Interaction):
        try:
            if inter.user.voice.channel.id != inter.guild.me.voice.channel.id:
                return await inter.response.send_message("유저님의 음성 채널 봇의 음성 채널이 달라요!", ephemeral=True)
        except:
            return await inter.response.send_message("봇이 음성채널에 없거나 유저가 음성채널에 없어요!", ephemeral=True)
        vc: nextwave.Player = inter.guild.voice_client
        await vc.disconnect()
        await inter.response.send_message(f"봇이 음성채널에서 나갔어요!", ephemeral=True)
        self.value = True

@client.event   
async def on_wavelink_track_end(player:nextwave.Player, track: nextwave.Track, reason):
    vc: player = inter.guild.voice_client
    if vc.loop:
        return await vc.play(track)
    elif vc.queue.is_empty:
        await inter.send(f"노래 재생이 다 끝났어요!")
        return await vc.disconnect()
    next_song = vc.queue.get()
    await vc.play(next_song)

@client.slash_command(name='재생', description='노래를 재생할 수 있습니다.')
async def play(inter: nextcord.Interaction, 검색: str):
    view = music_buttons()
    search = await nextwave.YouTubeTrack.search(query=검색, return_first=True)
    text = search.title
    if not inter.guild.voice_client:
        vc : nextwave.Player = await inter.user.voice.channel.connect(cls=nextwave.Player)
    elif not inter.user.voice:
        return await inter.send("음성 채널에 들어가주세요!")
    else:
        vc: nextwave.Player = inter.guild.voice_client
    if vc.queue.is_empty and not vc.is_playing():
        await vc.play(search)
        embed = nextcord.Embed(title=f"{text}을/를 재생합니다!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/fJ264IM.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        await inter.send(embed=embed, view=view)
        await view.wait()
    else:
        await vc.queue.put_wait(search)
        embed = nextcord.Embed(title=f"{text}을/를 재생목록에 넣었어요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/fJ264IM.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        msg = await inter.send(embed=embed)
    vc.inter = inter
    try:
      setattr(vc, "loop", False)
    except:
      setattr(vc, "loop", False)
      
#=================================================================================================================================

@client.slash_command(name='일시정지', description='재생되는 노래를 일시정지할 수 있습니다.')
async def play(inter: nextcord.Interaction):
    if not inter.guild.voice_client:
        embed = nextcord.Embed(title=f"음성 채널에 먼저 들어가 주세요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    elif not inter.user.voice:
        embed = nextcord.Embed(title=f"음성 채널에 들어가주세요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    try:
        if inter.user.voice.channel.id != inter.guild.me.voice.channel.id:
            embed = nextcord.Embed(title=f"유저님의 음성 채널 봇의 음성 채널이 달라요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
            color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
            embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
            embed.set_footer(text="Bot made by", icon_url="푸터 URL")
            return await inter.send(embed=embed)
    except:
        embed = nextcord.Embed(title=f"봇이 음성 채널에 없어요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    vc: nextwave.Player = inter.guild.voice_client
    await vc.pause()
    embed = nextcord.Embed(title=f"{vc.track.title}을/를 일시정지 했습니다!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!", 
    color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
    embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
    embed.set_footer(text="Bot made by", icon_url="푸터 URL")
    await inter.send(embed=embed)

#=================================================================================================================================

@client.slash_command(name='다시재생', description='일시정지 된 노래를 다시 재생할 수 있습니다.')
async def play(inter: nextcord.Interaction):
    if not inter.guild.voice_client:
        embed = nextcord.Embed(title=f"음성 채널에 먼저 들어가 주세요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/EtUro3U.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    elif not inter.user.voice:
        embed = nextcord.Embed(title=f"음성 채널에 들어가주세요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/EtUro3U.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    try:
        if inter.user.voice.channel.id != inter.guild.me.voice.channel.id:
            embed = nextcord.Embed(title=f"유저님의 음성 채널 봇의 음성 채널이 달라요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
            color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
            embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
            embed.set_footer(text="Bot made by", icon_url="푸터 URL")
            return await inter.send(embed=embed)
    except:
        embed = nextcord.Embed(title=f"봇이 음성 채널에 없어요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    else:
        vc: nextwave.Player = inter.guild.voice_client
    try:
        await vc.resume()
    except:
        embed = nextcord.Embed(title=f"이미 재생중이에요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/EtUro3U.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    embed = nextcord.Embed(title=f"{vc.track.title}을/를 다시 재생 했습니다!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!", 
    color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
    embed.set_image(url="https://i.imgur.com/EtUro3U.png")
    embed.set_footer(text="Bot made by", icon_url="푸터 URL")
    await inter.send(embed=embed)

#=================================================================================================================================

@client.slash_command(name='나가', description='봇을 음성 채널에서 내보낼 수 있습니다.')
async def play(inter: nextcord.Interaction):
    if not inter.guild.voice_client:
        embed = nextcord.Embed(title=f"음성 채널에 먼저 들어가 주세요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    elif not inter.user.voice:
        embed = nextcord.Embed(title=f"음성 채널에 들어가주세요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    try:
        if inter.user.voice.channel.id != inter.guild.me.voice.channel.id:
            embed = nextcord.Embed(title=f"유저님의 음성 채널 봇의 음성 채널이 달라요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
            color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
            embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
            embed.set_footer(text="Bot made by", icon_url="푸터 URL")
            return await inter.send(embed=embed)
    except:
        embed = nextcord.Embed(title=f"봇이 음성 채널에 없어요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    else:
        vc: nextwave.Player = inter.guild.voice_client
    
    await vc.disconnect()
    embed = nextcord.Embed(title=f"봇이 음성 채널에서 나갔습니다!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
    color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
    embed.set_image(url="https://i.imgur.com/zPhmAMr.png")
    embed.set_footer(text="Bot made by", icon_url="푸터 URL")
    return await inter.send(embed=embed)

#=================================================================================================================================

@client.slash_command(name='들어와', description='봇을 음성 채널에 부를 수 있습니다.')
async def play(inter: nextcord.Interaction):
    if not inter.guild.voice_client:
        embed = nextcord.Embed(title=f"음성 채널에 먼저 들어가 주세요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/zPhmAMr.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    elif not inter.user.voice:
        embed = nextcord.Embed(title=f"음성 채널에 들어가주세요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/zPhmAMr.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    else:
        vc: nextwave.Player = inter.guild.voice_client
    
    await vc.connect()
    embed = nextcord.Embed(title=f"봇이 음성 채널에 입장했습니다!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
    color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
    embed.set_image(url="https://i.imgur.com/zPhmAMr.png")
    embed.set_footer(text="Bot made by", icon_url="푸터 URL")
    return await inter.send(embed=embed)

#=================================================================================================================================

@client.slash_command(name='반복재생', description='노래를 반복할 수 있습니다.')
async def loop(inter: nextcord.Interaction):
    if not inter.guild.voice_client:
        embed = nextcord.Embed(title=f"음성 채널에 먼저 들어가 주세요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/E8qyOoO.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    elif not inter.user.voice:
        embed = nextcord.Embed(title=f"음성 채널에 들어가주세요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/E8qyOoO.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    try:
        if inter.user.voice.channel.id != inter.guild.me.voice.channel.id:
            embed = nextcord.Embed(title=f"유저님의 음성 채널 봇의 음성 채널이 달라요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
            color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
            embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
            embed.set_footer(text="Bot made by", icon_url="푸터 URL")
            return await inter.send(embed=embed)
    except:
        embed = nextcord.Embed(title=f"봇이 음성 채널에 없어요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    else:
        vc: nextwave.Player = inter.guild.voice_client
    if not vc.loop:
        vc.loop ^= True
        embed = nextcord.Embed(title=f"반복이 활성화 되었어요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/E8qyOoO.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    else:
        setattr(vc, "loop", False)
        embed = nextcord.Embed(title=f"반복이 비활성화 되었어요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/E8qyOoO.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)

#=================================================================================================================================

@client.slash_command(name='재생목록', description='재생 목록을 확인 할 수 있습니다.')
async def queue(inter: nextcord.Interaction):
    if not inter.guild.voice_client:
        embed = nextcord.Embed(title=f"음성 채널에 먼저 들어가 주세요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/j4glhMy.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    elif not inter.user.voice:
        embed = nextcord.Embed(title=f"음성 채널에 들어가주세요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/j4glhMy.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    try:
        if inter.user.voice.channel.id != inter.guild.me.voice.channel.id:
            embed = nextcord.Embed(title=f"유저님의 음성 채널 봇의 음성 채널이 달라요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
            color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
            embed.set_image(url="https://i.imgur.com/j4glhMy.png")
            embed.set_footer(text="Bot made by", icon_url="푸터 URL")
            return await inter.send(embed=embed)
    except:
        embed = nextcord.Embed(title=f"봇이 음성 채널에 없어요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/j4glhMy.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    else:
        vc: nextwave.Player = inter.guild.voice_client

    if vc.queue.is_empty:
        return await inter.send("재생 목록이 비었어요!")

    embed = nextcord.Embed(title=f"재생 목록!",color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
    embed.set_image(url="https://i.imgur.com/j4glhMy.png")
    embed.set_footer(text="Bot made by", icon_url="푸터 URL")
    queue = vc.queue.copy()
    song_count = 0
    for song in queue:
        song_count += 1
        embed.add_field(name=f"대기중인 {song_count}번째 노래", value=f"{song.title}")
    
    return await inter.send(embed=embed)

#=================================================================================================================================

@client.slash_command(name='현재재생', description='현재 재생중인 음악을 확인하실 수 있습니다.')
async def queue(inter: nextcord.Interaction):
    if not inter.guild.voice_client:
        embed = nextcord.Embed(title=f"음성 채널에 먼저 들어가 주세요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/P3EhfEd.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    elif not inter.user.voice:
        embed = nextcord.Embed(title=f"음성 채널에 들어가주세요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/P3EhfEd.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    try:
        if inter.user.voice.channel.id != inter.guild.me.voice.channel.id:
            embed = nextcord.Embed(title=f"유저님의 음성 채널 봇의 음성 채널이 달라요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
            color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
            embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
            embed.set_footer(text="Bot made by", icon_url="푸터 URL")
            return await inter.send(embed=embed)
    except:
        embed = nextcord.Embed(title=f"봇이 음성 채널에 없어요!", description="노래가 중간의 멈출 수 있습니다!\n봇을 강제로 내보내면 에러가 납니다!",
        color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_image(url="https://i.imgur.com/Q0lTAoz.png")
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.send(embed=embed)
    else:
        vc: nextwave.Player = inter.guild.voice_client
    
    embed = nextcord.Embed(title=f"현재 {vc.track.title}을 재생중이에요!",color=0xffcccc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
    embed.set_image(url="https://i.imgur.com/P3EhfEd.png")
    embed.set_footer(text="Bot made by", icon_url="푸터 URL")

client.run("토큰 입력")

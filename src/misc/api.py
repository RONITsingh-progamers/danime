import discord
from discord.ext import commands, tasks
import requests
import pymongo
from pymongo import MongoClient
import datetime
import re

 
class danimeapi(commands.Cog, name="danimeapi"):
	def __init__(self, Bot):
		self.Bot = Bot
		self.sendstats.start()


	def is_dev(ctx):
		access = [825591911782940713,427436602403323905, 353922674684329987,811823086193999892, 814953152640974869, 360087319992074251] 
		if ctx.author.id in access:
			return True
		return False

	@commands.command()
	@commands.check(is_dev)
	@commands.guild_only()
	async def addimage(self, ctx, collection:str, url:str): 
		if url == None:
			return await ctx.send(f"Bruh!")

		urls = list(url.split("+"))
		db = self.Bot.db2['AbodeDB']
		collections = collection.split("+")
		for collection in collections:
			added = []
			collection = db [f'{collection}']
			check = db.list_collection_names()
			if not collection.name in check:
				await ctx.send("No result for the db query.")
				continue
			for url in urls:
				try:
					data = {"_id": url}
					collection.insert_one(data)
					added.append(collection.name)
				except:
					await ctx.send("It seems the image is already added.")
			await ctx.send("Added image to " + ", ".join(added))
	@commands.group(pass_context=True)
	@commands.check(is_dev)
	@commands.guild_only()
	async def removeimage(self, ctx, collection:str, url:str):
		if ctx.invoked_subcommand is None:
			if url == None:
				return await ctx.send(f"Bruh!")

			urls = list(url.split("+"))
			db = self.Bot.db2['AbodeDB']
			collections = collection.split("+")
			for collection in collections:
				collection = db [f'{collection}']
				check = db.list_collection_names()
				if not collection.name in check:
					await ctx.send("No result for the db query.")
					continue
				removed = 0
				for url in urls:
					try:
						query = {"_id": url}
						search = collection.find_one(query)
						collection.delete_one(query)
						removed += 1

					except:
						await ctx.send("This image is not in the databse, try contacting the owner in our support server.")
				message = f"Removed `{removed}` imagesg(s) from `{collection.name}` tag."
				await ctx.send(message)
	
	@commands.command()
	@commands.check(is_dev)
	async def deleteimage(self, ctx, url:str):
		await ctx.send("This command will delete the image from all the database if matched, please use this wisley.", delete_after=7)
		db = self.Bot.db2['AbodeDB']
		collections = db.list_collection_names()
		urls = list(url.split("+"))
		for url in urls:
			deleted = 0
			for collection in collections:
				activeCollection = db[f'{collection}']
				query = {"_id" : url}
				search = activeCollection.find_one(query)
				if search != None:
					deleted += 1
					activeCollection.delete_one({"_id" : url})
				else:
					continue
			await ctx.send(f"Image `{url}` {deleted} times on total.")


	@commands.command()
	@commands.check(is_dev)
	@commands.guild_only()
	async def moveimage(self, ctx, collection:str, url:str, collection2:str):
		if url == None:
			return await ctx.send(f"Bruh!")

		urls = list(url.split("+"))
		db = self.Bot.db2['AbodeDB']
		check = db.list_collection_names()
		collection = db [f'{collection}']
		collection2 = db[collection2]

		if not collection.name in check or not collection2.name in check:
			return await ctx.send("Check failed, wrong db given.")
		moved_images = 0
		for url in urls:
			try:
				query = {"_id": url}
				search = collection.find_one(query)
				search2 = collection2.find_one(query)
				if search != None:
					collection.delete_one(query)
				if search2 != None:
					await ctx.send("Image already exists at the moved folder.")
				
				collection2.insert_one({"_id" : url})
				moved_images += 1				
			except:
				await ctx.send("This image is not in the databse, try contacting the owner in our support server.")
		await ctx.send(f"{moved_images} Images moved from `{collection.name}` to `{collection2.name}`")


	
	@commands.command()
	@commands.check(is_dev)
	async def linkstatus(self, ctx, link:str):
		db = self.Bot.db2['AbodeDB']
		collections = db.list_collection_names()
		matches = []
		for collection in collections:
			activeCollection = db[f'{collection}']
			query = {"_id" : link}
			search = activeCollection.find_one(query)
			if search != None:
				collection = collection
				matches.append(collection)
			else:
				continue
		matches = ['No matches'] if len(matches)== 0 else matches
		r = requests.get(link).content
		try:
			status = 200
		except:
			status = r.status_code
		# try:
		embed = discord.Embed()
		embed.description = f"Link status  || [Link]({link})"
		embed.add_field(name = "Collections", value = f", ".join(matches))
		embed.add_field(name = "Status Code", value= status)
		embed.add_field(name = "Remove it?", value= f"`dh removeimage <collection> {link}`", inline=False)
		await ctx.send(embed=embed)
		# except:
		# 	return await ctx.send("Something went wrong.")
	
	@commands.command()
	@commands.guild_only()
	@commands.check(is_dev)
	async def sendallimages(self, ctx, id:int):
		channel = self.Bot.get_channel(id)
		z = await ctx.send("Working on it!!")
		db = self.Bot.db2['AbodeDB']

		collection= db[f'anal']
		collection2 = db[f'anal2']
		search1 = collection.find()
		search2 = collection2.find()
		search2url = []
		for value in search2:
			search2url.append(value['_id'])

		for value in search1:
			url = value["_id"]
			if not url in search2url:
				await channel.send(url)




	@commands.command()
	@commands.guild_only()
	@commands.check(is_dev)
	async def getallimages(self, ctx, id_:int,collection:str, amount:int=3000):
		z = await ctx.send("Working on it!!")
		db = self.Bot.db2['AbodeDB']
		check = db.list_collection_names()

		if not collection in check:
			check = " , ".join(check)
			return await ctx.send(f"DB not found for the given query. Available queries {check}. **NOTE EVERYTHING IS CASE SENSETIVE**")
		
		collection= db[f'{collection}']
		firstList = []
		secondList = []

		result = collection.find()
		for r in result:
			firstList.append(r['_id'])
		channel = self.Bot.get_channel(id_)
		async for message in channel.history(limit=amount):
			# try:
			# 	# if message.content.startswith("&upload_images") or message.content.startswith("+jsk debug upload_images"):
			# 	# 	await ctx.send(f"Scraped images till [Here]({message.jump_url})")
			# 	# 	break
				url = message.content
				
				if message.attachments != None:
					for attachments in message.attachments:
						content = attachments.url
						if content.startswith("https"):
							check = self.is_url(content)
							if check == True:
								secondList.append(content)

				# if url.endswith("mp4") or url.endswith("gif"):
				# 	continue
				if not url.startswith("https"):
					continue
				if url in firstList:
					continue
				secondList.append(url)
			# except:
			# 	pass
		
		for x in secondList:
			if x.startswith("https") and x not in firstList:
				# await ctx.send(x)
				data = {"_id": x}
				try:
					collection.insert_one(data)
				except:
					print(f"Couldn't send {x}")

		message = f"Process completed, with addition of `{len(secondList)}` images to the tag `{collection.name}`, now the tag has total of `{len(firstList) + len(secondList)}` images."
		await ctx.send(embed=discord.Embed(description = message))

	@commands.command()
	@commands.check(is_dev)
	async def apistatus(self, ctx):
		url = " https://discordstatus.com/api/v2/status.json"
		r = requests.get(url).json()
		name = r['page']['name']
		url = r['page']['url']
		time_zone = r['page']['time_zone']
		updated_at = r['page']['updated_at']
		status = r['status']['description']
		em = discord.Embed(timestamp = datetime.datetime.fromisoformat(updated_at))
		em.description = f"Api Status for [{name}]({url})"
		em.add_field(name = "TimeZone", value = time_zone)
		em.add_field(name = "Status", value = status, inline = False)
		em.set_footer(text="Last Updated")
		await ctx.send(embed=em)

	def is_url(self, message):
		pattern =  re.compile(r"^https?://\S+(\.jpg|\.png|\.jpeg|\.webp]|\.gif|\.mp4|\.mov|\.webm)$")
		if not pattern.match(message):
			return False
		return True

	@commands.command()
	@commands.check(is_dev)
	async def updateapiinfo(self, ctx):
		db = self.Bot.db2['AbodeDB']
		collections = db.list_collection_names()
		collections.sort()
		results = []
		n = 1
		total = 0
		for collection in collections:
			activeCollection = db[f'{collection}']
			total += activeCollection.count()
			if activeCollection.count() > 60:
				string = f"`{n}.` {activeCollection.name.capitalize()} : `{activeCollection.count()}`"
				results.append(string)
				n+=1
		embed = discord.Embed(timestamp=datetime.datetime.now())
		embed.title = "Information on the DanimeAPI database collections."
		embed.description = "\n".join(results)
		embed.set_thumbnail(url = ctx.me.avatar_url)
		embed.set_footer(text=f"Total images : {total} | Last updated ", )
		message = await self.Bot.get_channel(856616097625145375).fetch_message(868719331515723826)
		await message.edit(embed=embed)
		await ctx.send("Message updated.")

	@commands.command()
	@commands.check(is_dev)
	async def sendapiimages(self, ctx, tag, amount):
		return await self.send_image(ctx, tag, amount)

	async def send_image(self, ctx, tag:str, amount:int):
		urls = requests.get(f"{self.Bot.api_url}{tag}/{amount}").json()['urls']
		a = 0 
		b = 5
		while len(urls) >= a:
			try:
				await ctx.send("\n".join(urls[a:b]))
			except Exception:
				break
			a += 5
			b += 5
	@tasks.loop(seconds=60)
	async def sendstats(self):
		await self.Bot.wait_until_ready()
		if self.Bot.DEFAULT_PREFIX == "&":
			return
		db = self.Bot.db2['AbodeDB']
		collection = db['1avialablepaths']

		now = datetime.datetime.utcnow()
		elapsed = now - self.Bot.starttime
		seconds = elapsed.seconds
		minutes, seconds = divmod(seconds, 60)
		hours, minutes = divmod(minutes, 60) 
		users = 0
		for guild in self.Bot.guilds:
		    try:
		        users += guild.member_count
		    except:
		        pass

		guilds = len(self.Bot.guilds)
		uptime = f"{elapsed.days}d {hours}h {minutes}m"
		discordpy = discord.__version__

		data = {"_id" : 2 , "guilds" : guilds, "users " :users ,  
				"uptime" : uptime, "discordpy" :  discordpy, "botinvite" : self.Bot.invite
				, "github" : self.Bot.github, "support_server" : self.Bot.support}
		search = collection.find_one({"_id" : 2})
		if search == None:
			collection.insert_one(data)
			return
		collection.update_one({"_id" : 2}, {"$set" : data})
		
		

def setup (Bot):
	Bot.add_cog(danimeapi(Bot))
	print("DanimeAPI is working.")

# Alfred

A multi purpose discord bot resembling Alfred Pennyworth, the loyal butler of Bruce Wayne.


### Local Setup

For Alfred to work properly, you need to update the images folder and the environment variables in the .env file.

**.env:**

	DISCORD_TOKEN=<Bot token> // Contact me to get this
	DISCORD_GUILDS=<Guild_name1,Guild_name2,...>
	MY_USER=<Discord Account name of the main "Master" of Alfred>
	MY_NAME=<Your Name of the main "Master" of Alfred>
	USERS=<Discord_name1:Real_name1,Discord_name2:Real_name2,...> // For all users in the guild
	PLAYLISTS=<Spotify_list_name1;Spotify_link1,Spotify_list_name2;Spotify_link2,...>

**images:** 

Add a welcome image to be shown to new users joining your servers. Name it as:

	Welcome.jpeg

Add an image for each user in the USERS list above in this form: 
	
	<Real_name>.jpeg

Run the bot in terminal with:

	python bot.py

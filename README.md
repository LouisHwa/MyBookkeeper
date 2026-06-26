A multi-agent system that i created for my personalization usage. 
It reads my TNG transactions that i sent into my discord channel and a discord bot will read the sent messages and processes it and sent to the agent. 
The agent will then read, store and sumamrizes it. I've developed the agent models through google-ADK

To provide a guideline of what i did: 
1. You need LLM models, either you used models from open-source provider like Ollama, or use APIs
2. You need to create a discord bot to read messages in your private channel

The environment requirements (dependencies) for developing this system written in requirements.txt 


Steps to create a discord bot: 
1. go to https://discord.com/developers/applications
2. Create a new application and direct to bot
3. Create a bot, copy its token and make sure allow 'Message Content Intent'
4. Use OAuth2 → URL Generator to invite the bot to a Discord server.

How to run: 
in your terminal(pointed to your venv), run 'python discord_bot.py'

Flow: 
<img width="701" height="580" alt="image" src="https://github.com/user-attachments/assets/174815c6-df06-4ac1-8ec6-a6d339c63a99" />

import discord
import os
from dotenv import load_dotenv 
from bookkeeper.agent import setup_session_and_runner, USER_ID, SESSION_ID
from utils import prepare_agent_input

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True # Required to read what you type
client = discord.Client(intents=intents)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID=os.getenv("DISCORD_CHANNEL_ID")

async def process_with_agent(message):
    try:
        
        content = await prepare_agent_input(message)
        session, runner = await setup_session_and_runner()
        events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
        agent_reply = "Processing..."
        async for event in events:
            if event.is_final_response():
                agent_reply = event.content.parts[0].text
        
        return agent_reply
    
    except ValueError as e:
        if "Tool" in str(e) and "not found" in str(e):
            return "❌ Agent error: The AI tried to use an incorrect tool. Please try rephrasing your request."
        return f"❌ Error: {str(e)}"
    except Exception as e:
        print(f"Error in process_with_agent: {e}")
        return "❌ Sorry, something went wrong processing your request."


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    if message.channel.id != int(DISCORD_CHANNEL_ID):
        return

    print(f"Received from Discord: {message.content}")
    
    async with message.channel.typing():
        response = await process_with_agent(message)
    
    await message.channel.send(response)

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
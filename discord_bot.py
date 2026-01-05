import discord
import os
import io
from dotenv import load_dotenv 
from google.genai import types
from bookkeeper.agent import setup_session_and_runner, USER_ID, SESSION_ID
from PIL import Image

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True # Required to read what you type
client = discord.Client(intents=intents)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID=os.getenv("DISCORD_CHANNEL_ID")

async def process_with_agent(message):
    try:
        has_image = "NO"
        request = message.content
        parts_list=[]

        if message.attachments:
            has_image = "YES"
            request = "Attached is an transaction image for your analysis and write it down in expenses.csv"

            attachment = message.attachments[0]
            if attachment.content_type and attachment.content_type.startswith('image/'):
                image_bytes = await attachment.read()
                with Image.open(io.BytesIO(image_bytes)) as img:
                    img.thumbnail((512, 512))

                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG", quality=65) # JPEG saves more space than PNG
                    image_bytes = buffered.getvalue()

                image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                parts_list.append(image_part)

        timestamp = message.created_at.strftime("%d/%m/%Y %H:%M:%S")
        text_part = types.Part(text=(
            f"Date and time sent: {timestamp} "
            f"User Request: {request} "
            f"Contains Image: {has_image} "
        ))
        parts_list.insert(0, text_part)

        
        print(f"Combined Prompt for Agent: {parts_list}")
        content = types.Content(role='user', parts=parts_list)

        session, runner = await setup_session_and_runner()
        
        events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
        
        agent_reply = "Processing..."
        async for event in events:
            # print(event)
            if event.content and event.content.parts:
                for part in event.content.parts:
                    # We look specifically for the "function_response" object
                    if part.function_response:
                        # Extract the dictionary we returned from Python
                        # Based on your log: {'result': 'Saved, terminate the task.'}
                        result_data = part.function_response.response
                        result_text = str(result_data.get('result', ''))
                        
                        # YOUR REQUESTED LOGIC:
                        if "Image analyzed successfully" in result_text:
                            # Stop the agent immediately and return success to Discord
                            return f"✅ {result_text}!"

            if event.is_final_response() and event.content.parts:
                text = event.content.parts[0].text
                # Only update if it's actual text, not a tool call
                if text and not text.strip().startswith('{'):
                    agent_reply = text
        
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
    
    # Send "Typing..." status so it feels responsive
    async with message.channel.typing():
        response = await process_with_agent(message)
    
    # Reply back on Discord
    await message.channel.send(response)

# 4. RUN THE BOT
if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
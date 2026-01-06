import io
from PIL import Image
from google.genai import types

async def prepare_agent_input(message):
    """
    Takes a raw Discord message and converts it into the Google ADK 
    Content format (handling image resizing, text formatting, etc).
    """
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

    return types.Content(role='user', parts=parts_list)

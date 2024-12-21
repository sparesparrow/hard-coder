from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import anthropic
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
claude_client = anthropic.Anthropic()
elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

@app.post("/api/stream-claude")
async def stream_claude(request: Request):
    data = await request.json()
    prompt = data["prompt"]

    async def generate():
        try:
            with claude_client.messages.stream(
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
                model="claude-3-5-sonnet-20241022"
            ) as stream:
                async for chunk in stream:
                    if chunk.type == "content_block_delta":
                        yield f"data: {json.dumps({'text': chunk.delta.text})}\n\n"
                yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/api/text-to-speech")
async def text_to_speech(request: Request):
    data = await request.json()
    text = data["text"]

    try:
        audio = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id="pNInz6obpgDQGcFmaJgB",  # Adam voice
            model_id="eleven_flash_v2_5",  # Using flash model for low latency
            output_format="mp3_22050_32",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True
            )
        )
        
        return StreamingResponse(audio, media_type="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/sound-effects")
async def generate_sound_effect(request: Request):
    data = await request.json()
    description = data["description"]
    
    try:
        audio = elevenlabs_client.text_to_sound_effects.convert(
            text=description,
            duration_seconds=data.get("duration", 5)
        )
        return StreamingResponse(audio, media_type="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    
    try:
        conversation = Conversation(
            client=elevenlabs_client,
            AGENT_ID=os.getenv("AGENT_ID"),
            requires_auth=True,
            callback_agent_response=lambda response: websocket.send_text(json.dumps({"type": "response", "content": response}))
        )
        
        await conversation.start_session()
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "user_input":
                # Process user input through ElevenLabs conversation
                await conversation.process_input(message["content"])
            
    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "content": str(e)}))
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
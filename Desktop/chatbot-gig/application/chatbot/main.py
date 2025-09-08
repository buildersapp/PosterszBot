from fastapi import FastAPI,File,UploadFile,Form
from AI import extract_intent_entities
from service import citilytic_request
from utils import ensure_session_id
from AI import get_business_data
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.post("/chat",status_code=200)
async def chat(
    session_id: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    # Ensure session id always exists

    if image:  
        if session_id is None:
            return JSONResponse(
            status_code=400,
            content={"bot_message": "Please start with a text message to tell me your intent before uploading an image."}
        )
        # ---- Image flow ----
        citilytic_data = await citilytic_request(image_data=image)
        result = get_business_data(json_data=citilytic_data, session_id=session_id)
        return {"type": "image", "data": result, "session_id": session_id}

    elif message:  
        session_id = ensure_session_id(session_id)
        # ---- Text flow ----
        response = extract_intent_entities(message, session_id=session_id)
        return response

    else:
        # Neither message nor image provided
        return {"bot_message": "Please provide either a text message or an image."}










# @app.post("/chat")
# def chat(chat:ChatRequest):
#     session_id = ensure_session_id(chat.session_id)
#     response = extract_intent_entities(chat.message,session_id=session_id)
#     return response

# @app.post("/upload-post")
# async def upload_post(image:UploadFile = File(...),session_id: str = Form(...)
# ):
#     citilytic_data = await citilytic_request(image_data=image)
#     result = get_business_data(json_data=citilytic_data,session_id=session_id)
#     return {"data":result}
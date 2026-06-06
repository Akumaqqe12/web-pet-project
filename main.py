from fastapi import FastAPI, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db import Base, engine, get_user_requests, add_request_data
from gemini_client import get_answer_from_gemini
import traceback


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    print('LOG:\t  All tables created')
    yield

app = FastAPI(
    title="Mafaka",
    lifespan=lifespan
)

# CORS middleware ПЕРВЫМ
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "null",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/requests")
def get_my_requests(request: Request):
    try:
        user_ip_address = request.client.host
        print(f"GET /requests from IP: {user_ip_address}")
        user_requests = get_user_requests(ip_adress=user_ip_address)
        return user_requests
    except Exception as e:
        print(f"Error in GET /requests: {str(e)}")
        traceback.print_exc()
        return []

@app.post("/requests")
def send_prompt(request: Request, prompt: str = Body(embed=True)):
    try:
        user_ip_address = request.client.host
        print(f"POST /requests from IP: {user_ip_address}")
        print(f"Prompt: {prompt[:100]}...")
        
        answer = get_answer_from_gemini(prompt)
        
        add_request_data(
            ip_adress=user_ip_address,
            prompt=prompt,
            response=answer
        )
        
        return {"answer": answer}
        
    except Exception as e:
        print(f"Error in POST /requests: {str(e)}")
        traceback.print_exc()
        return {"answer": f"Ошибка: {str(e)}"}

@app.get("/test")
def test_endpoint():
    return {"message": "OK", "status": "running"}
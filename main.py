import os
import sqlite3
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

# db path and templates
DB_PATH = 'players.db'
templates = Jinja2Templates(directory='templates')

# db config. Lifespan: app startup/shutdown handling
@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        query = """CREATE TABLE IF NOT EXISTS players
                   (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_name TEXT NOT NULL,
                        position TEXT NOT NULL
                   )
                """
        cur.execute(query)
        conn.commit()
        conn.close()
    yield # App runs here

# create app with lifespan
app = FastAPI(lifespan=lifespan)


# Mount static directory (make sure this is after app = FastAPI())
app.mount('/static', StaticFiles(directory='static'), name='static')

# Helper functions: kinda acting like controllers
def get_players():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, player_name, position FROM players")
    rows = cur.fetchall()
    conn.close()
    return rows

def add_player(player_name: str, position: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO players (player_name, position) VALUES (?, ?)", (player_name, position))
    conn.commit()
    conn.close()

# Routes
@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    players = get_players()
    return templates.TemplateResponse("home.html", {"request":request, "players":players})

@app.post("/add-player")
def create(player_name: str = Form(...), position: str = Form(...)):
    add_player(player_name, position)
    return RedirectResponse("/", status_code=303)
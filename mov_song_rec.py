from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import random
import uvicorn
import os
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)


class input1(BaseModel):
    mental_health: int
    happiness: int
    mood: str

df_song = pd.read_csv(r"songs.csv")
df_movie = pd.read_csv(r"movies.csv")

def rec(df, mental_health, happiness, mood,l=[],cnt = 0,val=1):
    while True:
        try:
            new_df = df[(df["Mental_Health_Score"] == mental_health) & (df["Happiness_Level"] == happiness) & (df["Mood"].str.contains(mood))]

            if not new_df.empty:
                return new_df.sample(min(3, len(new_df)))[l].values.tolist()
            else:
                if cnt > 10:
                    val += 1
                happiness = max(0, min(5, happiness + random.randint(-val, val)))

                if cnt > 5:
                    mental_health = max(0, min(5, mental_health + random.randint(-1, 1)))
                    return rec(df, mental_health, happiness, mood, l, cnt + 1, val)
                else:
                    return rec(df, mental_health, happiness, mood, l, cnt + 1, val)

        except Exception as e:
            return f"An error occurred: {str(e)}"

@app.api_route("/ping", methods=["GET", "HEAD"])
async def ping():
    await asyncio.sleep(0.1)
    return {"message": "server is running"}

@app.post("/recommendations")
def get_recommendations(ui: input1):
    mood = ui.mood.title()
    res = {"songs": [], "movies": []}
    
    songs = rec(df_song, ui.mental_health, ui.happiness, mood, ["Song_Name", "Genre", "YouTube_Link"])
    uniq_song = set()
    for song in songs:
        sk = (song[0])
        if sk not in uniq_song:
            res["songs"].append({"song_name": song[0], "genre": song[1], "ytl": song[2]})
            uniq_song.add(sk)

    movies = rec(df_movie, ui.mental_health, ui.happiness, mood, ["Movie_Title", "Genre"])
    uniq_movies= set()
    for movie in movies:
        mk = (movie[0])
        if mk not in uniq_movies:
            res["movies"].append({"movie_name": movie[0], "genre": movie[1]})
            uniq_movies.add(mk)
    return res

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
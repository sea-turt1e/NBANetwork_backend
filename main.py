from typing import List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vueの開発サーバーのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データモデルの定義
Base = declarative_base()


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    team = Column(String)
    position = Column(String)
    points = Column(Float)
    assists = Column(Float)
    rebounds = Column(Float)


# Pydanticモデル
class PlayerBase(BaseModel):
    name: str
    team: str
    position: str
    points: float
    assists: float
    rebounds: float


class PlayerCreate(PlayerBase):
    pass


class PlayerResponse(PlayerBase):
    id: int

    class Config:
        orm_mode = True


class NetworkRequest(BaseModel):
    player_ids: List[int]


class NetworkRelation(BaseModel):
    player1_id: int
    player2_id: int
    weight: float


# データベース接続
SQLALCHEMY_DATABASE_URL = "sqlite:///./players.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# データベースの初期化
Base.metadata.create_all(bind=engine)


# 依存関係
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# APIエンドポイント
@app.get("/api/players", response_model=List[PlayerResponse])
def get_players():
    db = SessionLocal()
    players = db.query(Player).all()
    return players


@app.post("/api/players", response_model=PlayerResponse)
def create_player(player: PlayerCreate):
    db = SessionLocal()
    db_player = Player(**player.dict())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


@app.post("/api/network", response_model=List[NetworkRelation])
def get_network_relations(request: NetworkRequest):
    # ここではサンプルの関係性データを返します
    # 実際のアプリケーションではこの部分にグラフニューラルネットワークの計算ロジックが入ります
    relations = []
    player_ids = request.player_ids

    for i in range(len(player_ids)):
        for j in range(i + 1, len(player_ids)):
            # ダミーの重み付け計算（実際のアプリケーションではここを置き換えます）
            weight = np.random.uniform(0.7, 1.0)
            relations.append(NetworkRelation(player1_id=player_ids[i], player2_id=player_ids[j], weight=weight))

    return relations


# サンプルデータの追加用エンドポイント
@app.post("/api/sample-data")
def create_sample_data():
    db = SessionLocal()

    sample_players = [
        {"name": "Stephen Curry", "team": "GSW", "position": "PG", "points": 32.1, "assists": 7.1, "rebounds": 5.2},
        {"name": "LeBron James", "team": "LAL", "position": "SF", "points": 28.9, "assists": 8.3, "rebounds": 8.1},
        {
            "name": "Giannis Antetokounmpo",
            "team": "MIL",
            "position": "PF",
            "points": 29.7,
            "assists": 5.8,
            "rebounds": 11.5,
        },
        {"name": "Luka Doncic", "team": "DAL", "position": "PG", "points": 32.4, "assists": 8.0, "rebounds": 8.6},
        {"name": "Nikola Jokic", "team": "DEN", "position": "C", "points": 26.4, "assists": 9.1, "rebounds": 11.8},
    ]

    for player_data in sample_players:
        player = Player(**player_data)
        db.add(player)

    db.commit()
    return {"message": "Sample data created successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

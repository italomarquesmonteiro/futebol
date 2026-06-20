import requests
import pandas as pd
from pathlib import Path

# ============================================
# CONFIGURAÇÕES
# ============================================

API_KEY = "500569fa74c144669b3e75a724b515b6"

BASE_URL = "https://api.football-data.org/v4"

HEADERS = {
    "X-Auth-Token": API_KEY
}

COMPETITION = "WC"      # Copa do Mundo

OUTPUT = Path("dataset_worldcup")
OUTPUT.mkdir(exist_ok=True)


# ============================================
# FUNÇÃO PARA BUSCAR JOGOS
# ============================================

def get_matches():

    url = f"{BASE_URL}/competitions/{COMPETITION}/matches"

    response = requests.get(url, headers=HEADERS)

    response.raise_for_status()

    return response.json()["matches"]


# ============================================
# CONVERTE UM JOGO PARA UMA LINHA
# ============================================

def parse_match(match):

    row = {

        # Identificação
        "match_id": match["id"],
        "utcDate": match["utcDate"],
        "status": match["status"],
        "matchday": match["matchday"],
        "stage": match["stage"],
        "group": match.get("group"),

        # Times
        "home_id": match["homeTeam"]["id"],
        "home_team": match["homeTeam"]["name"],
        "home_short": match["homeTeam"].get("shortName"),
        "home_tla": match["homeTeam"].get("tla"),

        "away_id": match["awayTeam"]["id"],
        "away_team": match["awayTeam"]["name"],
        "away_short": match["awayTeam"].get("shortName"),
        "away_tla": match["awayTeam"].get("tla"),

        # Árbitro
        "referee": (
            match["referees"][0]["name"]
            if len(match["referees"]) > 0
            else None
        ),

        # Placar
        "home_ft":
            match["score"]["fullTime"]["home"],

        "away_ft":
            match["score"]["fullTime"]["away"],

        "home_ht":
            match["score"]["halfTime"]["home"],

        "away_ht":
            match["score"]["halfTime"]["away"],

        "winner":
            match["score"]["winner"],

        # Duração
        "duration":
            match["score"]["duration"]
    }

    return row


# ============================================
# MAIN
# ============================================

print("Baixando jogos...")

matches = get_matches()

print(f"{len(matches)} jogos encontrados.")

# Apenas primeira e segunda rodada

matches = [
    m
    for m in matches
    if m["matchday"] in [1, 2]
]

print(f"{len(matches)} jogos da 1ª e 2ª rodada.")

rows = [parse_match(m) for m in matches]

df = pd.DataFrame(rows)

# ============================================
# Ordenação
# ============================================

df = (
    df
    .sort_values(["matchday", "group", "utcDate"])
    .reset_index(drop=True)
)

# ============================================
# Datas
# ============================================

df["utcDate"] = pd.to_datetime(df["utcDate"])

# ============================================
# Salvar
# ============================================

csv_file = OUTPUT / "worldcup_rounds_1_2.csv"
parquet_file = OUTPUT / "worldcup_rounds_1_2.parquet"

df.to_csv(csv_file, index=False, encoding="utf-8-sig")

df.to_parquet(parquet_file, index=False)

print("\nDataset criado!")

print(df.head())

print(f"\nCSV: {csv_file}")
print(f"Parquet: {parquet_file}")
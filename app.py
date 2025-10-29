import sqlite3
from pathlib import Path
import streamlit as st
import pandas as pd
 
# ===== Nastavení databáze =====
DB_PATH = Path("pujcovna.db")
 
# Vytvoření a naplnění databáze při prvním spuštění
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
 
    # Tabulka strojů
    c.execute("""CREATE TABLE IF NOT EXISTS stroje (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nazev TEXT,
        popis TEXT,
        cena_za_den REAL,
        dostupnost INTEGER
    )""")
 
    # Tabulka klientů
    c.execute("""CREATE TABLE IF NOT EXISTS klienti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nazev TEXT,
        adresa TEXT,
        ico TEXT,
        sleva REAL,
        kontakt TEXT
    )""")
 
    # Naplnit ukázkovými daty (jen pokud prázdné)
    c.execute("SELECT COUNT(*) FROM stroje")
    if c.fetchone()[0] == 0:
        data_stroje = [
            ("Bagr CAT 320", "Hydraulický bagr střední třídy", 4500, 1),
            ("Minibagr Bobcat E10", "Malý bagr pro drobné práce", 2500, 0),
            ("Vibrační deska Wacker", "Kompaktní vibrační deska", 800, 1),
            ("Kladivo bourací 30 kg TE-H28 85 J", "Bourací kladivo", 1064, 1),
            ("Pila stolová průměr 700 mm", "Stolová pila", 859, 1),
            ("Nakladač čelní kloubový", "Nakladač 1 m3", 4840, 0),
            ("Dumper pásový 1,5 t", "Kompaktní pásový dumper", 4600, 1),
            ("Válec vibrační zemní 12.5 t", "Zemní válec", 7865, 0),
            ("Jeřáb samostavitelný 32 m", "Samostavitelný jeřáb", 2420, 0),
            ("Minirypadlo 2 t", "Kompaktní minirypadlo", 3450, 1)
        ]
        c.executemany("INSERT INTO stroje (nazev, popis, cena_za_den, dostupnost) VALUES (?, ?, ?, ?)", data_stroje)
 
    c.execute("SELECT COUNT(*) FROM klienti")
    if c.fetchone()[0] == 0:
        data_klienti = [
            ("Stavby s.r.o.", "Praha 1", "12345678", 10, "Jan Novák"),
            ("BuildPro a.s.", "Brno", "87654321", 5, "Petr Svoboda"),
            ("MegaConstruct s.r.o.", "Plzeň", "11223344", 15, "Eva Horáková"),
            ("Rekonstav s.r.o.", "Ostrava", "22334455", 8, "Tomáš Dvořák"),
            ("ProfiStav a.s.", "Olomouc", "33445566", 12, "Milan Kovář"),
            ("SolidBuild s.r.o.", "Hradec Králové", "44556677", 7, "Lucie Malá"),
            ("StrojRent s.r.o.", "Pardubice", "55667788", 10, "Radek Jelínek"),
            ("MaxiBuild s.r.o.", "Zlín", "66778899", 6, "Jaroslav Beneš"),
            ("RapidStav s.r.o.", "České Budějovice", "77889900", 5, "Monika Tichá"),
            ("Konstrukta s.r.o.", "Liberec", "88990011", 9, "Viktor Král")
        ]
        c.executemany("INSERT INTO klienti (nazev, adresa, ico, sleva, kontakt) VALUES (?, ?, ?, ?, ?)", data_klienti)
 
    conn.commit()
    conn.close()
 
init_db()
 
# ===== Streamlit aplikace =====
st.set_page_config(page_title="Půjčovna strojů", layout="wide", page_icon="🚜")
 
st.title("🚜 Půjčovna stavebních strojů")
 
# Načíst data
conn = sqlite3.connect(DB_PATH)
stroje = pd.read_sql("SELECT * FROM stroje", conn)
klienti = pd.read_sql("SELECT * FROM klienti", conn)
conn.close()
 
menu = st.sidebar.radio("Menu", ["Formulář", "Seznam strojů", "Seznam klientů"])
 
if menu == "Formulář":
    st.header("Výpočet půjčovného")
 
    klient = st.selectbox("Vyberte klienta", klienti["nazev"])
    stroj = st.selectbox("Vyberte stroj", stroje["nazev"])
    dny = st.number_input("Počet dní", min_value=1, value=1)
 
    sleva = klienti.loc[klienti["nazev"] == klient, "sleva"].values[0]
    cena_den = stroje.loc[stroje["nazev"] == stroj, "cena_za_den"].values[0]
    dostupnost = stroje.loc[stroje["nazev"] == stroj, "dostupnost"].values[0]
 
    if dostupnost == 1:
        st.success("Stroj je dostupný ✅")
        celkem = dny * cena_den * (1 - sleva / 100)
        st.metric("Celková cena (po slevě)", f"{celkem:,.0f} Kč")
    else:
        st.error("Tento stroj momentálně není dostupný ❌")
 
elif menu == "Seznam strojů":
    st.header("Seznam strojů")
    st.dataframe(stroje)
 
elif menu == "Seznam klientů":
    st.header("Seznam klientů")
    st.dataframe(klienti)

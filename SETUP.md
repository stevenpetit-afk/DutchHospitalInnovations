# UMC Innovaties — Installatie & Gebruik

## Wat je krijgt

Een statische website die elke ochtend om 07:30 automatisch nieuws ophaalt
over innovaties uit alle 8 Nederlandse UMC's en publiceert op GitHub Pages.

---

## Stap 1 — Zet het project op GitHub

### Optie A: via de GitHub-website (makkelijkst)

1. Ga naar [github.com/new](https://github.com/new)
2. Geef het project een naam, bijv. `umc-innovaties`
3. Zet het repo op **Public** (vereist voor gratis GitHub Pages)
4. Klik **Create repository**
5. Upload alle bestanden die je hebt ontvangen (sleep ze naar de upload-zone of gebruik Git)

### Optie B: via de terminal

```bash
cd umc-innovaties          # de map die je hebt ontvangen
git init
git add .
git commit -m "Eerste versie UMC Innovaties website"
git remote add origin https://github.com/JOUW-GEBRUIKERSNAAM/umc-innovaties.git
git push -u origin main
```

---

## Stap 2 — GitHub Pages activeren

1. Ga in jouw repository naar **Settings → Pages**
2. Onder **Source** kies je **GitHub Actions**
3. Sla op

De eerste keer moet je de workflow handmatig starten (zie Stap 4).

---

## Stap 3 — Workflow permissies instellen

1. Ga naar **Settings → Actions → General**
2. Scroll naar **Workflow permissions**
3. Kies **Read and write permissions**
4. Vink **Allow GitHub Actions to create and approve pull requests** aan
5. Klik **Save**

---

## Stap 4 — Eerste keer handmatig uitvoeren

1. Ga naar **Actions** in jouw repository
2. Klik op **Dagelijks nieuws ophalen**
3. Klik op **Run workflow → Run workflow**
4. Wacht ~2 minuten tot de workflow klaar is (groen vinkje)
5. Jouw site is nu live op:  
   `https://JOUW-GEBRUIKERSNAAM.github.io/umc-innovaties/`

---

## Daarna: volledig automatisch

Elke dag om **08:30 (zomertijd)** / 07:30 (wintertijd) voert GitHub Actions automatisch het script uit:

1. Nieuws wordt opgehaald via RSS-feeds en Google News
2. `data/articles.json` wordt bijgewerkt en gecommit
3. De website wordt herdeployd

Je hoeft hier zelf niets meer voor te doen.

---

## Handmatig nieuws vernieuwen

Wil je buiten de dagelijkse planning nieuws ophalen?

1. Ga naar **Actions → Dagelijks nieuws ophalen**
2. Klik **Run workflow**

---

## Lokaal testen

```bash
# Dependencies installeren
pip install -r requirements.txt

# Nieuws ophalen (vereist internet)
python scripts/fetch_news.py

# Website lokaal bekijken (in de project-map)
python -m http.server 8000
# Open: http://localhost:8000
```

---

## Bestandenstructuur

```
umc-innovaties/
├── index.html                    ← De website
├── data/
│   └── articles.json             ← Artikeldata (automatisch bijgewerkt)
├── scripts/
│   ├── fetch_news.py             ← Nieuwsscript (draait dagelijks)
│   └── gen_sample_data.py        ← Voorbeelddata generator
├── requirements.txt              ← Python-afhankelijkheden
├── .github/
│   └── workflows/
│       └── daily_news.yml        ← Dagelijkse automatisering
└── SETUP.md                      ← Dit bestand
```

---

## UMC's en bronnen

| UMC | Directe RSS | Google News |
|-----|-------------|-------------|
| Amsterdam UMC | ✓ | ✓ |
| Erasmus MC | ✓ | ✓ |
| LUMC | ✓ | ✓ |
| Maastricht UMC+ | ✓ | ✓ |
| Radboudumc | ✓ | ✓ |
| UMCG | ✓ | ✓ |
| UMC Utrecht | ✓ | ✓ |

---

## Veelgestelde vragen

**Wat als een UMC zijn RSS-feed wijzigt?**  
Pas de URL aan in `scripts/fetch_news.py` onder de sectie `UMCS`.

**Hoe voeg ik extra zoektermen toe?**  
Voeg trefwoorden toe aan `INNOVATION_KEYWORDS` of `TOPIC_KEYWORDS` in `fetch_news.py`.

**Kan ik meer UMC's of ziekenhuizen toevoegen?**  
Ja — voeg een nieuw blok toe aan het `UMCS`-woordenboek in `fetch_news.py`.

**Hoe filter ik irrelevante artikelen weg?**  
Verwijder trefwoorden uit `INNOVATION_KEYWORDS` of maak de `is_innovation_relevant()`-functie strenger.

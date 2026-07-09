#!/usr/bin/env python3
"""Genereert realistische voorbeelddata voor articles.json."""
import json, random
from datetime import datetime, timezone, timedelta
from pathlib import Path

random.seed(42)

UMCS = [
    "Amsterdam UMC", "Erasmus MC", "LUMC",
    "Maastricht UMC+", "Radboudumc", "UMCG", "UMC Utrecht",
]

ARTICLES = [
    # Amsterdam UMC
    {
        "umc": "Amsterdam UMC",
        "title": "AI-algoritme van Amsterdam UMC detecteert borstkanker beter dan radioloog",
        "summary": "Onderzoekers van Amsterdam UMC hebben een kunstmatige-intelligentiemodel ontwikkeld dat microscopisch kleine borstkankerlaesies opspoodt met een nauwkeurigheid van 96%, significant beter dan de gemiddelde radioloog. Het model is getraind op meer dan 100.000 mammografieën en zal binnenkort worden getest in een multicenter klinische studie.",
        "url": "https://www.amsterdamumc.org/nieuws/ai-borstkanker-detectie",
        "source": "Amsterdam UMC",
        "tags": ["AI & machine learning", "Kanker & oncologie", "Diagnostiek & beeldvorming"],
        "days_ago": 0,
    },
    {
        "umc": "Amsterdam UMC",
        "title": "Nieuw bloedtest ontdekt vroeg stadium Alzheimer met hoge betrouwbaarheid",
        "summary": "Een team van neurologen en biochemici bij Amsterdam UMC heeft een bloedtest ontwikkeld die de ziekte van Alzheimer jaren voor de eerste symptomen kan opsporen. De test meet de concentratie van het eiwit p-tau217 in het bloed en heeft een sensitiviteit van 91% in een studie met 850 deelnemers.",
        "url": "https://www.amsterdamumc.org/nieuws/bloedtest-alzheimer",
        "source": "Amsterdam UMC",
        "tags": ["Neurologie", "Diagnostiek & beeldvorming", "Genomica & genetica"],
        "days_ago": 2,
    },
    {
        "umc": "Amsterdam UMC",
        "title": "€4,2 miljoen EU-subsidie voor onderzoek naar orgaanoïden als vervanging dierproeven",
        "summary": "Amsterdam UMC ontvangt een Europese subsidie van 4,2 miljoen euro voor het Horizon-project ORGANO-REPLACE, dat orgaanoïden (miniatuurorganen in een petrischaal) wil inzetten als ethischer alternatief voor dierproeven bij geneesmiddelenonderzoek.",
        "url": "https://www.amsterdamumc.org/nieuws/eu-subsidie-organoïden",
        "source": "Amsterdam UMC",
        "tags": ["Regeneratieve geneeskunde", "Farmacologie", "Subsidie & samenwerking"],
        "days_ago": 5,
    },
    # Erasmus MC
    {
        "umc": "Erasmus MC",
        "title": "Erasmus MC implanteert eerste draadloze pacemaker ter wereld bij kind van 3 jaar",
        "summary": "Chirurgen van het Erasmus MC Sophia Kinderziekenhuis hebben succesvol de kleinste draadloze pacemaker ter wereld geïmplanteerd bij een driejarig meisje met een aangeboren hartafwijking. Het apparaat, kleiner dan een vitamine-pil, werkt zonder draden en kan van buitenaf worden geprogrammeerd.",
        "url": "https://www.erasmusmc.nl/nieuws/draadloze-pacemaker-kind",
        "source": "Erasmus MC",
        "tags": ["Cardiologie", "Chirurgie & robotica"],
        "days_ago": 1,
    },
    {
        "umc": "Erasmus MC",
        "title": "Groot doorbraak: Erasmus MC ontdekt genetische oorzaak zeldzame leverziekte",
        "summary": "Onderzoekers van Erasmus MC hebben de genetische oorzaak ontdekt van een zeldzame, erfelijke leverziekte die wereldwijd zo'n 10.000 mensen treft. De ontdekking opent de weg voor gerichte gentherapie. Resultaten zijn gepubliceerd in Nature Medicine.",
        "url": "https://www.erasmusmc.nl/nieuws/genetische-oorzaak-leverziekte",
        "source": "Erasmus MC",
        "tags": ["Genomica & genetica", "Zeldzame ziekten", "Farmacologie"],
        "days_ago": 3,
    },
    {
        "umc": "Erasmus MC",
        "title": "Robotarm helpt neurochirurgen bij precisie-operaties aan de hersenstam",
        "summary": "Het Erasmus MC introduceert een geavanceerde robotarm die neurochirurgen ondersteunt bij extreem delicate operaties aan de hersenstam. Het systeem filtert ongewenste trillingen van de hand van de chirurg en vergroot de precisie met een factor tien, waarmee operaties die voorheen te riskant waren nu veilig kunnen worden uitgevoerd.",
        "url": "https://www.erasmusmc.nl/nieuws/robotarm-neurochirurgie",
        "source": "Erasmus MC",
        "tags": ["Chirurgie & robotica", "Neurologie", "AI & machine learning"],
        "days_ago": 7,
    },
    # LUMC
    {
        "umc": "LUMC",
        "title": "LUMC-onderzoekers kweken functioneel hartweefsel uit stamcellen",
        "summary": "In een primeur voor Nederland zijn onderzoekers van het LUMC erin geslaagd volledig functioneel hartweefsel te kweken uit geïnduceerde pluripotente stamcellen (iPSC). Het weefsel klopt autonoom en kan worden gebruikt voor het testen van nieuwe hartziektemedicijnen zonder dierproeven.",
        "url": "https://www.lumc.nl/nieuws/hartweefsel-stamcellen",
        "source": "LUMC",
        "tags": ["Regeneratieve geneeskunde", "Cardiologie", "Farmacologie"],
        "days_ago": 2,
    },
    {
        "umc": "LUMC",
        "title": "CRISPR-behandeling van LUMC elimineert HIV-virus uit menselijke cellen in laboratorium",
        "summary": "Wetenschappers van het LUMC hebben met CRISPR-Cas9 gen-editingtechnologie het HIV-virus volledig verwijderd uit geïnfecteerde menselijke cellen in laboratoriumomstandigheden. Dit is een belangrijke stap richting een definitieve genezing van aids, al zijn klinische studies nog jaren verwijderd.",
        "url": "https://www.lumc.nl/nieuws/crispr-hiv-behandeling",
        "source": "LUMC",
        "tags": ["Genomica & genetica", "Infectieziekten", "Farmacologie"],
        "days_ago": 4,
    },
    {
        "umc": "LUMC",
        "title": "Nieuwe MRI-techniek van LUMC maakt onzichtbare hersentumoren detecteerbaar",
        "summary": "Een team van radiologen en fysici bij het LUMC heeft een nieuwe MRI-techniek ontwikkeld die gebruik maakt van hyperpolariseerde koolstof-13 als contrastmiddel. Met deze techniek worden gliomen die voor conventionele MRI onzichtbaar zijn voor het eerst detecteerbaar in een vroeg en nog behandelbaar stadium.",
        "url": "https://www.lumc.nl/nieuws/mri-techniek-hersentumoren",
        "source": "LUMC",
        "tags": ["Diagnostiek & beeldvorming", "Kanker & oncologie", "Neurologie"],
        "days_ago": 8,
    },
    # Maastricht UMC+
    {
        "umc": "Maastricht UMC+",
        "title": "Maastricht UMC+ start eerste Nederlandse studie met draagbare kunstnier",
        "summary": "Het Maastricht UMC+ is gestart met een klinische studie voor de 'wearable kidney', een draagbare kunstnier die dialysepatiënten bevrijdt van hun afhankelijkheid van de dialysemachine. Acht patiënten nemen deel aan de eerste fase; het apparaat werkt continu en weegt slechts 5 kilogram.",
        "url": "https://www.mumc.nl/nieuws/draagbare-kunstnier-studie",
        "source": "Maastricht UMC+",
        "tags": ["Chirurgie & robotica", "Farmacologie"],
        "days_ago": 1,
    },
    {
        "umc": "Maastricht UMC+",
        "title": "Onderzoekers Maastricht ontdekken hoe darmflora bijdraagt aan depressie",
        "summary": "Psychiaters en microbiologen van het Maastricht UMC+ publiceren baanbrekend onderzoek in Cell dat aantoont hoe specifieke darmbacteriën de productie van serotonine in de hersenen direct beïnvloeden. De bevindingen openen nieuwe therapeutische wegen voor de behandeling van therapieresistente depressie.",
        "url": "https://www.mumc.nl/nieuws/darmflora-depressie",
        "source": "Maastricht UMC+",
        "tags": ["Neurologie", "Genomica & genetica"],
        "days_ago": 6,
    },
    # Radboudumc
    {
        "umc": "Radboudumc",
        "title": "Radboudumc ontwikkelt vaccinplatform dat binnen 48 uur tegen nieuw virus beschermt",
        "summary": "Virologen van Radboudumc hebben een mRNA-vaccinplatform ontwikkeld dat in slechts 48 uur na identificatie van een nieuw virus een effectief vaccin kan produceren. In dierproeven bood het vaccin bij vier van vijf dieren volledige bescherming. ZonMw financiert de volgende onderzoeksfase met 3,8 miljoen euro.",
        "url": "https://www.radboudumc.nl/nieuws/mRNA-vaccinplatform",
        "source": "Radboudumc",
        "tags": ["Infectieziekten", "Farmacologie", "Subsidie & samenwerking"],
        "days_ago": 0,
    },
    {
        "umc": "Radboudumc",
        "title": "Radboudumc en Philips lanceren AI-platform voor vroege sepsis-detectie op de IC",
        "summary": "In samenwerking met Philips heeft Radboudumc een AI-systeem ontwikkeld dat sepsis (bloedvergiftiging) gemiddeld zes uur eerder detecteert dan artsen dat klinisch kunnen doen. Het systeem analyseert continu meer dan 200 vitale parameters en waarschuwt verplegend personeel via een app op hun smartphone.",
        "url": "https://www.radboudumc.nl/nieuws/ai-sepsis-detectie",
        "source": "Radboudumc",
        "tags": ["AI & machine learning", "Diagnostiek & beeldvorming", "Infectieziekten"],
        "days_ago": 3,
    },
    {
        "umc": "Radboudumc",
        "title": "Eerste succesvolle gentherapie voor erfelijke doofheid bij baby's in Nederland",
        "summary": "Radboudumc heeft als eerste ziekenhuis in Nederland gentherapie toegepast bij twee baby's met aangeboren doofheid door een mutatie in het OTOF-gen. Na de behandeling met een virale vector die het correcte gen inbrengt, reageerden beide kinderen binnen acht weken aantoonbaar op geluid.",
        "url": "https://www.radboudumc.nl/nieuws/gentherapie-doofheid",
        "source": "Radboudumc",
        "tags": ["Genomica & genetica", "Farmacologie", "Zeldzame ziekten"],
        "days_ago": 10,
    },
    # UMCG
    {
        "umc": "UMCG",
        "title": "UMCG-wetenschappers ontdekken nieuw type immuuncel dat tumoren vernietigt",
        "summary": "Immunologen van het UMCG hebben een voorheen onbekend type T-cel geïdentificeerd dat in staat is om solide tumoren van binnenuit te vernietigen zonder omliggende gezond weefsel te beschadigen. De ontdekking, gepubliceerd in Science Immunology, kan leiden tot een nieuwe generatie kankertherapieën.",
        "url": "https://www.umcg.nl/nieuws/nieuwe-immuuncel-tumoren",
        "source": "UMCG",
        "tags": ["Kanker & oncologie", "Genomica & genetica", "Farmacologie"],
        "days_ago": 2,
    },
    {
        "umc": "UMCG",
        "title": "UMCG opent nieuw centrum voor precisiegeneeskunde met supercomputer",
        "summary": "Het UMCG opent het Groningen Institute for Precision Medicine (GIPM), uitgerust met een supercomputer die 10 petabyte aan genetische data kan verwerken. Het centrum richt zich op het koppelen van genomische profielen aan klinische uitkomsten voor gepersonaliseerde behandeling van kanker, diabetes en hart- en vaatziekten.",
        "url": "https://www.umcg.nl/nieuws/precisiegeneeskunde-centrum",
        "source": "UMCG",
        "tags": ["Genomica & genetica", "AI & machine learning", "Subsidie & samenwerking"],
        "days_ago": 5,
    },
    # UMC Utrecht
    {
        "umc": "UMC Utrecht",
        "title": "UMC Utrecht implanteert als eerste ter wereld spraakcomputer in hersenen patiënt met ALS",
        "summary": "Neurochirurgen van UMC Utrecht hebben een Brain-Computer Interface geïmplanteerd bij een 58-jarige ALS-patiënt die volledig verlamd is. Via elektroden in de motorische schors kan de patiënt nu tekst typen met een snelheid van 62 woorden per minuut, uitsluitend door na te denken over het bewegen van zijn handen.",
        "url": "https://www.umcutrecht.nl/nieuws/bci-als-patiënt",
        "source": "UMC Utrecht",
        "tags": ["Neurologie", "AI & machine learning", "Chirurgie & robotica"],
        "days_ago": 1,
    },
    {
        "umc": "UMC Utrecht",
        "title": "Nieuw type immunotherapie van UMC Utrecht geneest 43% van therapieresistente lymfomen",
        "summary": "Een fase II-studie van UMC Utrecht met BiSpecifieke Antilichamen (BsAbs) toont aan dat 43% van de patiënten met therapieresistent non-Hodgkin lymfoom volledig in remissie gaat. De therapie koppelt T-cellen van de patiënt direct aan de tumorcellen, waarna het immuunsysteem de kanker vernietigt.",
        "url": "https://www.umcutrecht.nl/nieuws/immunotherapie-lymfoom",
        "source": "UMC Utrecht",
        "tags": ["Kanker & oncologie", "Farmacologie"],
        "days_ago": 4,
    },
    {
        "umc": "UMC Utrecht",
        "title": "UMC Utrecht en RIVM lanceren nationaal biobank-netwerk voor pandemie-paraatheid",
        "summary": "UMC Utrecht en het RIVM hebben samen het Nationaal Pandemie-Paraatheidsnetwerk opgericht, een samenwerkingsverband van 12 ziekenhuizen dat in geval van een nieuwe pandemie binnen 72 uur kan beginnen met het verzamelen, analyseren en delen van biomaterialen en klinische data.",
        "url": "https://www.umcutrecht.nl/nieuws/biobank-netwerk-pandemie",
        "source": "UMC Utrecht",
        "tags": ["Infectieziekten", "Subsidie & samenwerking", "Diagnostiek & beeldvorming"],
        "days_ago": 12,
    },
]

# Artikelen omzetten naar juist formaat
import hashlib

now = datetime.now(timezone.utc)
articles = []
for i, a in enumerate(ARTICLES):
    pub = now - timedelta(days=a["days_ago"], hours=random.randint(0, 8))
    art_id = hashlib.md5(f"{a['url']}|{a['title']}".encode()).hexdigest()
    articles.append({
        "id":        art_id,
        "umc":       a["umc"],
        "title":     a["title"],
        "summary":   a["summary"],
        "url":       a["url"],
        "source":    a["source"],
        "published": pub.isoformat(),
        "tags":      a["tags"],
    })

# Sorteren op datum
articles.sort(key=lambda x: x["published"], reverse=True)

output = {
    "last_updated": now.isoformat(),
    "total": len(articles),
    "articles": articles,
}

out_path = Path(__file__).parent.parent / "data" / "articles.json"
out_path.parent.mkdir(exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✓ {len(articles)} voorbeeldartikelen geschreven naar {out_path}")

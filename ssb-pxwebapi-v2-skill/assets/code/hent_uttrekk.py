"""Mal: hent et uttrekk fra SSBs PxWebApi v2 til en pandas DataFrame.

Fyll inn TABELL, UTVALG, KODELISTER og LANG. Variabel- og verdikodene skal være
bekreftet mot GET /tables/{id}/metadata først, ikke gjettet.

Før du summerer eller tar gjennomsnitt: sjekk kan_summeres(ds). Er den False,
har SSB merket tallene som ikke summerbare. Si det til brukeren.

Krever: requests, pandas.
"""
from __future__ import annotations

import itertools
import time
from collections import deque

import pandas as pd
import requests

BASE = "https://data.ssb.no/api/pxwebapi/v2"
LANG = "no"  # "no" eller "en"

TABELL = "07459"

# Variabelkode -> verdikoder. Variabler med elimination: false må være med
# (Tid og ContentsCode alltid). For tid: top(n) eller from(x) følger nye perioder.
UTVALG: dict[str, list[str]] = {
    "Region": ["0301", "4601"],
    "ContentsCode": ["Personer1"],
    "Tid": ["top(5)"],
}

# Variabelkode -> kodeliste. Kodene i UTVALG må da komme fra kodelisten:
# {"Region": "agg_KommSummer"} krever "K-0301", ikke "0301".
KODELISTER: dict[str, str] = {}

# Halve rate limit (40 kall per 60 s). En plass holdes i 61 s.
BUDSJETT = 20
VINDU_S = 61.0
_kall: deque[float] = deque(maxlen=BUDSJETT)


def _ta_plass() -> None:
    """Vent til det er plass i kallvinduet, og ta plassen."""
    if len(_kall) == _kall.maxlen:
        vent = _kall[0] + VINDU_S - time.monotonic()
        if vent > 0:
            time.sleep(vent)
    _kall.append(time.monotonic())


def hent(tabell: str, utvalg: dict[str, list[str]],
         kodelister: dict[str, str] | None = None, lang: str = LANG) -> dict:
    """Hent et uttrekk som json-stat2. Feil gir RuntimeError med API-ets `title`."""
    kodelister = kodelister or {}
    body = {"selection": [
        {"variableCode": var, "valueCodes": koder,
         **({"codelist": kodelister[var]} if var in kodelister else {})}
        for var, koder in utvalg.items()
    ]}
    url = f"{BASE}/tables/{tabell}/data"
    params = {"lang": lang, "outputFormat": "json-stat2"}
    for forsok in (1, 2):
        _ta_plass()
        svar = requests.post(url, params=params, json=body, timeout=60)
        if svar.status_code != 429 or forsok == 2:
            break
        time.sleep(VINDU_S)  # 429: vent ett vindu, prøv én gang til
    if svar.status_code != 200:
        try:
            aarsak = svar.json().get("title", "")
        except ValueError:
            aarsak = svar.text[:200]  # 500 kan ha tom body
        raise RuntimeError(f"HTTP {svar.status_code} fra tabell {tabell}: {aarsak}")
    return svar.json()


def til_dataframe(ds: dict) -> pd.DataFrame:
    """json-stat2 -> én rad per celle, med kode og tekst per variabel, value og status.

    `value` er row-major: siste variabel i `id` varierer raskest. Manglende tall
    er NaN, og `status` sier hvorfor. Et tall med status (f.eks. *) er foreløpig.
    """
    variabler = ds["id"]
    kategorier = []
    for var in variabler:
        kat = ds["dimension"][var]["category"]
        indeks = kat["index"]
        koder = sorted(indeks, key=indeks.get) if isinstance(indeks, dict) else list(indeks)
        tekster = kat.get("label", {})
        kategorier.append([(kode, tekster.get(kode, kode)) for kode in koder])

    status = ds.get("status") or {}
    if isinstance(status, list):
        status = {str(i): s for i, s in enumerate(status)}

    rader = []
    for pos, kombinasjon in enumerate(itertools.product(*kategorier)):
        rad = {}
        for var, (kode, tekst) in zip(variabler, kombinasjon):
            rad[var] = kode
            rad[f"{var}_tekst"] = tekst
        rad["value"] = ds["value"][pos]
        rad["status"] = status.get(str(pos))
        rader.append(rad)
    return pd.DataFrame(rader)


def enheter(ds: dict) -> dict[str, dict]:
    """Enhet og desimaler per statistikkvariabel: {kode: {"base": …, "decimals": …}}."""
    metric = ds.get("role", {}).get("metric", ["ContentsCode"])[0]
    return ds["dimension"][metric]["category"].get("unit", {})


def noter(ds: dict) -> list[tuple[bool, str]]:
    """Tabellnotene som (obligatorisk, tekst). Obligatoriske noter skal følge tallene."""
    obligatorisk = ds.get("extension", {}).get("noteMandatory") or {}
    return [(bool(obligatorisk.get(str(i))), tekst)
            for i, tekst in enumerate(ds.get("note") or [])]


def kan_summeres(ds: dict) -> bool:
    """False når SSB har merket tallene som ikke summerbare (aggregallowed).

    Merket gjelder hele tabellen: indekser og gjennomsnitt, men også antall i en
    tabell som har prosent. Summerer du eller tar gjennomsnitt likevel, si det
    til brukeren og merk det som egen beregning.
    """
    return bool(ds.get("extension", {}).get("px", {}).get("aggregallowed", True))


def kilde(ds: dict, lang: str = LANG) -> str:
    tabell = ds["extension"]["px"]["tableid"]
    dato = ds["updated"][:10]
    if lang == "en":
        return f"Source: Statistics Norway, table {tabell}. Last updated: {dato}."
    return f"Kilde: SSB, tabell {tabell}. Sist oppdatert: {dato}."


def main() -> None:
    ds = hent(TABELL, UTVALG, KODELISTER, LANG)
    df = til_dataframe(ds)

    print(ds["label"])
    for kode, enhet in enheter(ds).items():
        print(f"  {kode}: {enhet.get('base')}, {enhet.get('decimals')} desimaler")
    print()
    # Ikke fillna(0), og ikke dropna() uten å si fra: status forklarer hullene.
    print(df.to_string(index=False))
    print()
    for obligatorisk, tekst in noter(ds):
        print(("Obligatorisk note: " if obligatorisk else "Note: ") + tekst)
    if not kan_summeres(ds):
        print("Advarsel: SSB har merket tallene som ikke summerbare "
              "(aggregallowed: false). Sjekk at en sum eller et gjennomsnitt "
              "gir mening, og si fra om du regner det ut.")

    # Responsen sier ikke hvilke variabler som er utelatt (summert bort) eller
    # hvilken kodeliste som er brukt, så skriv ut utvalget sammen med tallene.
    print(f"Utvalg: {UTVALG}")
    if KODELISTER:
        print(f"Kodelister: {KODELISTER}")
    print(kilde(ds, LANG))


if __name__ == "__main__":
    main()

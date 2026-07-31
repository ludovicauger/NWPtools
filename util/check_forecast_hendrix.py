#!/usr/bin/env python3
"""
Verifie sur hendrix.meteo.fr, pour une XP donnee, que chaque repertoire
de prevision contient le bon nombre de fichiers pour chacun des motifs
suivants : *eurat01* (103), *eurat1s20* (67), *glob025* (67), *glob01* (103).

Arborescence explorée :
    /home/auger/vortex/arpege/4dvarfr/<XP>/<YYYYMMDD>T0000P/forecast

Les dates sont decouvertes automatiquement en listant le repertoire
/home/auger/vortex/arpege/4dvarfr/<XP>.

Usage:
    python3 check_forecast_hendrix.py XP [--user USER] [--host HOST] [--base BASE]

Les identifiants de connexion sont cherches dans ~/.netrc (machine
hendrix.meteo.fr) si --user n'est pas fourni ; sinon le mot de passe est
demande de facon interactive (jamais affiche, jamais stocke).
"""

import argparse
import fnmatch
import getpass
import netrc
import re
import sys
from ftplib import FTP, error_perm

HOST = "hendrix.meteo.fr"
BASE = "/home/auger/vortex/arpege/4dvarfr"
DATE_DIR_RE = re.compile(r"^(\d{8})T0000P$")
EXPECTED_COUNTS = {
    "*eurat01*": 103,
    "*eurat1s20*": 67,
    "*glob025*": 67,
    "*glob01*": 103,
}


def get_credentials(host, user):
    if not user:
        try:
            auths = netrc.netrc()
            entry = auths.authenticators(host)
        except (FileNotFoundError, netrc.NetrcParseError):
            entry = None
        if entry:
            login, _, password = entry
            return login, password
        user = input(f"Utilisateur pour {host}: ")
    password = getpass.getpass(f"Mot de passe pour {user}@{host}: ")
    return user, password


def list_names(ftp, path):
    """Liste les entrees d'un repertoire FTP (noms simples, sans chemin)."""
    names = []
    ftp.retrlines(f"NLST {path}", names.append)
    return [n.rsplit("/", 1)[-1] for n in names if n.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("xp", help="Nom de l'experience (XP)")
    parser.add_argument("--host", default=HOST, help=f"Serveur FTP (defaut: {HOST})")
    parser.add_argument("--base", default=BASE,
                         help=f"Repertoire de base (defaut: {BASE})")
    parser.add_argument("--user", help="Utilisateur FTP (sinon lu dans ~/.netrc)")
    args = parser.parse_args()

    xp_path = f"{args.base}/{args.xp}"

    user, password = get_credentials(args.host, args.user)

    ftp = FTP(args.host)
    ftp.login(user, password)

    try:
        entries = list_names(ftp, xp_path)
    except error_perm as exc:
        ftp.quit()
        sys.exit(f"Impossible de lister {xp_path}: {exc}")

    dates = sorted({
        match.group(1)
        for name in entries
        for match in [DATE_DIR_RE.match(name)]
        if match
    })

    if not dates:
        ftp.quit()
        sys.exit(f"Aucun repertoire de date (format YYYYMMDDT0000P) trouve dans {xp_path}")

    print(f"{len(dates)} date(s) trouvee(s) pour XP={args.xp} : {', '.join(dates)}\n")

    problems = []

    for date in dates:
        forecast_path = f"{xp_path}/{date}T0000P/forecast"
        try:
            files = list_names(ftp, forecast_path)
        except error_perm as exc:
            print(f"{date}: PROBLEME - repertoire forecast inaccessible ({exc})")
            problems.append(date)
            continue

        if not files:
            print(f"{date}: PROBLEME - repertoire forecast vide ou introuvable ({forecast_path})")
            problems.append(date)
            continue

        counts = {
            pattern: sum(1 for f in files if fnmatch.fnmatch(f, pattern))
            for pattern in EXPECTED_COUNTS
        }

        bad = {p: c for p, c in counts.items() if c != EXPECTED_COUNTS[p]}
        detail = "  ".join(f"{p}={c}" for p, c in counts.items())

        if bad:
            print(f"{date}: PROBLEME  {detail}")
            problems.append(date)
        else:
            print(f"{date}: OK  {detail}")

    ftp.quit()

    print()
    if problems:
        print(f"Dates problematiques ({len(problems)}): {', '.join(problems)}")
        sys.exit(1)

    print("Toutes les dates sont conformes.")


if __name__ == "__main__":
    main()

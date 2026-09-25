#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scorearpege.py
===============

Dérivé de diagarpege.py : au lieu de comparer directement 2 expériences
entre elles, ce script calcule un SCORE de chacune des 2 expériences
(xp1, xp2) par rapport à une 3ème expérience de référence (xp3), pour
une date (DAT) et une échéance (ECH) données :

    - pour xp1 et pour xp2, on récupère le fichier prévu à l'échéance
      ECH depuis la date DAT (comme dans diagarpege.py),
    - pour xp3 (la référence), on récupère le fichier à l'ÉCHÉANCE 0,
      mais valide à la même date/heure que xp1/xp2 à l'échéance ECH.
      Exemple : DAT=20260101, ECH=48 (2 jours) -> la référence est le
      réseau du 20260103 à 00, échéance 0 (c'est l'instant "vérité
      terrain" ou analyse la plus proche disponible pour ce réseau) ;
    - pour chaque champ/niveau demandé, on calcule :
        diff1 = xp1 - reference   et   diff2 = xp2 - reference
      (et leurs carrés), pour chaque date de la plage --dat/--dat2 ;
    - on en déduit, en moyennant sur toutes les dates (et pour chaque
      point de grille) :
        biais1 = moyenne(diff1), RMSE1 = sqrt(moyenne(diff1**2))
        biais2 = moyenne(diff2), RMSE2 = sqrt(moyenne(diff2**2))
    - on trace enfin 2 cartes par champ : la différence des RMSE
      (RMSE1 - RMSE2) et la différence des biais (biais1 - biais2)
      entre les 2 expériences xp1 et xp2, ainsi que les valeurs
      globales correspondantes dans le titre,
    - dépôt des png + d'un index.html sur sxalgo1.cnrm.meteo.fr,
      comme dans diagarpege.py.

ATTENTION sur le réseau de référence : la formule ci-dessus suppose
qu'un réseau de xp3 existe à l'instant DAT+RESEAU+ECH (par exemple
seulement 00/06/12/18 UTC pour OPER/DBLE). Si ce n'est pas le cas pour
votre --ech, le téléchargement du fichier de référence échouera.

Usage minimal :
    ./scorearpege.py --dat 20260101 --ech 48 --xp1 HCWO --xp2 OPER --xp3 OPER

(reprend les mêmes options que diagarpege.py --help, avec en plus
--xp3 pour l'expérience de référence et --local-file-ref pour lui
substituer un fichier local).
"""

import argparse
import copy
import html
import math
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta

import numpy as np


# ---------------------------------------------------------------------------
# Valeurs par défaut (reprises de diagarpege.py)
# ---------------------------------------------------------------------------

DEFAULT_HOST_HENDRIX = "hendrix.meteo.fr"
DEFAULT_HOST_IMAGES = "sxalgo1.cnrm.meteo.fr"
DEFAULT_USER = "auger"
DEFAULT_IMAGES_BASE = "/d0/images/auger"
# Authentification vers hendrix via lftp : par defaut simple "ftp" en
# s'appuyant sur ~/.netrc (entree "machine hendrix.meteo.fr login ... "
# password ..."), comme le fait l'utilisateur habituellement. Ne JAMAIS
# passer de mot de passe en argument/ligne de commande.
DEFAULT_PROTOCOL = "ftp"
DEFAULT_LISTING_FILENAME = "listing.arpege-forecast.a0001-b0001"

# Gabarits de nom de fichier. {ech2d} = échéance sur 2 chiffres (ex: "03"),
# ce qui donne "+0003:00" une fois inséré dans le gabarit, conformément aux
# deux exemples des instructions (historic...+00<ECH>:00.fa et
# grid...+0099:00.grib pour ECH=99).
#DEFAULT_FA_FILENAME_TEMPLATE = "historic.arpege.tc1798-c10+00{ech2d}:00.fa"
DEFAULT_FA_FILENAME_TEMPLATE = "historic.arome.franmg-01km30+00{ech2d}:00.fa"
DEFAULT_GRIB_FILENAME_TEMPLATE = "grid.arpege-forecast.glob01+00{ech2d}:00.grib"
#xptype = "arpege/4dvarfr"
xptype = "arome/3dvarfr"

# Champs par défaut pour les fichiers FA "historic"
#DEFAULT_FA_PARAMS = ["TEMPERATURE", "HUMI.SPECIFI", "WIND"]
DEFAULT_FA_PARAMS = ["TEMPERATURE"]
DEFAULT_FA_LEVELS = [80]
DEFAULT_WIND_SOURCE = "psikhi"

# Champs par défaut pour les fichiers GRIB "grid"
DEFAULT_GRIB_PARAMS = ["WIND", "TEMPERATURE"]
DEFAULT_GRIB_WIND_LEVEL = "10m"      # A VERIFIER : vent 10 m par défaut
DEFAULT_GRIB_TEMP_LEVEL_HPA = 850


# ---------------------------------------------------------------------------
# Arguments en ligne de commande
# ---------------------------------------------------------------------------

def build_argparser():
    p = argparse.ArgumentParser(
        description="Calcule le score (RMSE, biais) de 2 previsions ARPEGE "
                    "(xp1, xp2) par rapport a une 3eme experience de "
                    "reference (xp3), et publie la difference des scores "
                    "sur sxalgo1.")

    g_req = p.add_argument_group("Echéance / date / expériences")
    g_req.add_argument("--dat", default="20260101",
                        help="Date de la prévision (date de début si --dat2 "
                            "fourni), format YYYYMMDD (defaut: %(default)s)")
    g_req.add_argument("--dat2", default=None,
                        help="Date de fin optionnelle (si fourni, calcule les "
                            "stats sur tous les jours entre --dat et --dat2 "
                            "inclus), format YYYYMMDD (defaut: None = pas de "
                            "plage)")
    g_req.add_argument("--reseau", default="0000",
                        help="Heure de réseau HHMM, ex 0000 (defaut: %(default)s)")
    g_req.add_argument("--ech", type=int, default=0,
                        help="Echéance en heures (defaut: %(default)s)")
    g_req.add_argument("--xp1", default="HCWO",
                        help="Identifiant de la 1ere experience (numero "
                            "Olive/Vortex a 4 caracteres, ou OPER/DBLE). "
                            "HCWO n'est qu'un exemple, a adapter (defaut: %(default)s)")
    g_req.add_argument("--xp2", default="OPER",
                        help="Identifiant de la 2eme experience, ou OPER/DBLE "
                            "(defaut: %(default)s)")
    g_req.add_argument("--xp3", default="OPER",
                        help="Identifiant de l'experience de REFERENCE pour "
                            "le score (ou OPER/DBLE). Le fichier de "
                            "reference est pris a l'echeance 0, a la date/"
                            "reseau correspondant au meme instant que xp1/"
                            "xp2 a l'echeance --ech (ex: dat=20260101 "
                            "ech=48 -> reference = reseau du 20260103 a 00, "
                            "echeance 0) (defaut: %(default)s)")

    g_file = p.add_argument_group("Fichiers")
    g_file.add_argument("--filetype", choices=["fa", "grib"], default="fa",
                        help="Type de fichier a comparer (defaut: %(default)s)")
    g_file.add_argument("--filename-template", default=None,
                        help="Gabarit de nom de fichier, avec {ech2d} pour "
                            "l'echeance sur 2 chiffres. Defaut selon "
                            "--filetype (fa: %r, grib: %r)"
                            % (DEFAULT_FA_FILENAME_TEMPLATE,
                                DEFAULT_GRIB_FILENAME_TEMPLATE))
    g_file.add_argument("--local-file1", default=None,
                        help="Si fourni, saute le telechargement lftp pour "
                            "l'experience 1 et utilise ce fichier local")
    g_file.add_argument("--local-file2", default=None,
                        help="Idem pour l'experience 2")
    g_file.add_argument("--local-file-ref", default=None,
                        help="Idem pour l'experience de reference (xp3). "
                            "Ne fonctionne que pour une plage d'une seule "
                            "date (--dat sans --dat2), sinon la reference "
                            "differe a chaque date")
    g_file.add_argument("--workdir", default="./scorearpege_work",
                        help="Repertoire local de travail (telechargements, "
                            "png) (defaut: %(default)s)")

    g_fields = p.add_argument_group("Champs a tracer")
    g_fields.add_argument("--params", nargs="+", default=None,
                        help="Liste de parametres a tracer. Pour un fichier "
                            "FA : parmi TEMPERATURE, HUMI.SPECIFI, WIND, ou "
                            "tout suffixe de champ SxxxNOM. Pour un fichier "
                            "GRIB : parmi WIND, TEMPERATURE. Defaut selon "
                            "--filetype.")
    g_fields.add_argument("--levels", type=int, nargs="+", default=None,
                        help="Niveaux (uniquement pour --filetype fa ; "
                            "numeros de niveau vertical, ex 080) "
                            "(defaut: %s)" % DEFAULT_FA_LEVELS)
    g_fields.add_argument("--wind-source", choices=["psikhi", "uv"],
                        default=DEFAULT_WIND_SOURCE,
                        help="Pour --filetype fa, comment obtenir le champ "
                            "WIND : 'psikhi' (defaut) calcule le vent a "
                            "partir de S{niveau}FONC.COURANT (fonction de "
                            "courant, psi) et S{niveau}POT.VITESSE "
                            "(potentiel de vitesse, khi) via "
                            "epygram.fields.psikhi2uv -- ce sont les seuls "
                            "champs de vent presents dans certains historic "
                            "; 'uv' relit directement S{niveau}WIND.U.PHYS "
                            "/ S{niveau}WIND.V.PHYS quand ils existent")
    g_fields.add_argument("--grib-temp-level-hpa", type=int,
                        default=DEFAULT_GRIB_TEMP_LEVEL_HPA,
                        help="Niveau (hPa) pour le champ TEMPERATURE en "
                            "GRIB (defaut: %(default)s)")
    g_fields.add_argument("--grib-wind-level", default=DEFAULT_GRIB_WIND_LEVEL,
                        help="Niveau pour le champ WIND en GRIB, '10m' ou "
                            "une pression en hPa (defaut: %(default)s)")

    g_net = p.add_argument_group("Reseau / deploiement")
    g_net.add_argument("--user", default=DEFAULT_USER,
                        help="Login Meteo-France : utilise a la fois pour la "
                            "connexion lftp a hendrix (mis dans l'URL, ex "
                            "ftp://user@hendrix.meteo.fr) et pour le ssh/scp "
                            "de deploiement vers host-images (defaut: "
                            "%(default)s)")
    g_net.add_argument("--protocol", choices=["ftp", "sftp"],
                        default=DEFAULT_PROTOCOL,
                        help="Protocole lftp pour se connecter a hendrix "
                            "(defaut: %(default)s). Le mot de passe n'est "
                            "jamais passe en argument par ce script : il est "
                            "cherche par lftp dans ~/.netrc")
    g_net.add_argument("--host-hendrix", default=DEFAULT_HOST_HENDRIX,
                        help="Serveur d'archivage (defaut: %(default)s)")
    g_net.add_argument("--host-images", default=DEFAULT_HOST_IMAGES,
                        help="Serveur de publication des images (defaut: %(default)s)")
    g_net.add_argument("--images-base", default=DEFAULT_IMAGES_BASE,
                        help="Repertoire de base sur host-images (defaut: %(default)s)")
    g_net.add_argument("--remote-dir", default=None,
                        help="Sous-repertoire de publication (defaut : "
                            "construit a partir de dat/ech/xp1/xp2/xp3)")
    g_net.add_argument("--no-deploy", action="store_true",
                        help="Ne pas faire ssh/scp vers host-images (les png "
                            "+ index.html restent seulement dans --workdir)")
    g_net.add_argument("--list-fields", action="store_true",
                        help="Se contente de lister les champs disponibles "
                            "dans les fichiers xp1/xp2/reference puis "
                            "s'arrete (utile pour verifier les noms de "
                            "champs GRIB)")

    g_listing = p.add_argument_group("Diff du fichier listing")
    g_listing.add_argument("--listing-filename", default=DEFAULT_LISTING_FILENAME,
                        help="Nom du fichier listing recupere en plus dans le "
                            "meme repertoire forecast de xp1 et xp2 (pas de "
                            "la reference), et compare avec git diff "
                            "--word-diff (defaut: %(default)s)")
    g_listing.add_argument("--no-listing-diff", action="store_true",
                        help="Ne pas recuperer/comparer le fichier listing "
                            "(ignore aussi si --local-file1/--local-file2 "
                            "sont utilises, car le repertoire distant n'est "
                            "alors pas connu)")

    return p


# ---------------------------------------------------------------------------
# Construction des chemins distants / noms de fichiers
# ---------------------------------------------------------------------------

def remote_dir_for_xp(args, xp):
    """Construit le repertoire distant "forecast" pour une experience xp
    (commun aux fichiers historic/grid et au fichier listing). Utilise
    args.dat/args.reseau (qui, pour la reference, sont temporairement
    positionnes sur la date/reseau de reference -- voir reference_args())."""
    if xp.upper() in ("OPER", "DBLE"):
        # ~mxpt001/vortex/arpege/4dvarfr/OPER|DBLE/YYYY/MM/DD/T{reseau}P/forecast/
        yyyy, mm, dd = args.dat[0:4], args.dat[4:6], args.dat[6:8]
        return ("~mxpt001/vortex/%s/%s/%s/%s/%s/T%sP/forecast"
                % (xptype, xp.upper(), yyyy, mm, dd, args.reseau))
    else:
        # ~/vortex/arpege/4dvarfr/{XPID}/{DAT}T{reseau}P/forecast/
        return ("~/vortex/%s/%s/%sT%sP/forecast"
                % (xptype, xp, args.dat, args.reseau))


def remote_path_and_filename(args, xp):
    """Construit (repertoire_distant, nom_de_fichier) pour une experience xp,
    a l'echeance args.ech."""
    ech2d = "%02d" % args.ech
    if args.filename_template:
        template = args.filename_template
    elif args.filetype == "fa":
        template = DEFAULT_FA_FILENAME_TEMPLATE
    else:
        template = DEFAULT_GRIB_FILENAME_TEMPLATE
    filename = template.format(ech2d=ech2d)
    return remote_dir_for_xp(args, xp), filename


def date_range(dat1_str, dat2_str=None):
    """Genere une plage de dates au format YYYYMMDD.
    Si dat2_str est None, retourne [dat1_str].
    Sinon retourne une liste de toutes les dates entre dat1_str et dat2_str inclus.
    """
    if not dat2_str:
        return [dat1_str]

    d1 = datetime.strptime(dat1_str, "%Y%m%d")
    d2 = datetime.strptime(dat2_str, "%Y%m%d")

    if d1 > d2:
        d1, d2 = d2, d1

    dates = []
    current = d1
    while current <= d2:
        dates.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)

    return dates


def reference_datetime(dat, reseau, ech):
    """Calcule (dat_ref, reseau_ref) : la date/reseau (a echeance 0) qui
    correspond au meme instant que (dat, reseau) a l'echeance ech.

    Exemple : dat=20260101, reseau=0000, ech=48 -> ("20260103", "0000")
    (2 jours plus tard, a 00h)."""
    dt = datetime.strptime(dat + reseau, "%Y%m%d%H%M") + timedelta(hours=ech)
    return dt.strftime("%Y%m%d"), dt.strftime("%H%M")


def reference_args(args, dat_ref, reseau_ref):
    """Copie superficielle de args avec dat/reseau/ech positionnes sur la
    reference (echeance 0), pour reutiliser telle quelle
    remote_path_and_filename() / remote_dir_for_xp()."""
    ref = copy.copy(args)
    ref.dat = dat_ref
    ref.reseau = reseau_ref
    ref.ech = 0
    return ref


def fetch_via_lftp(protocol, user, host, remote_dir, filename, local_path):
    """Recupere un fichier distant par lftp vers local_path.

    Authentification : le login (user) est mis dans l'URL, exactement
    comme dans l'enonce d'origine ("lftp auger@hendrix.meteo.fr:...") --
    sans quoi lftp se connecte en anonyme, ce qui echoue sur hendrix.
    Le mot de passe n'est en revanche JAMAIS passe en argument : lftp va
    le chercher automatiquement dans ~/.netrc (entree "machine <host>
    login <user>"), a charge pour l'utilisateur d'avoir cette entree.
    """
    if os.path.exists(local_path):
        print("  -> deja present localement : %s" % local_path)
        return
    remote_full = remote_dir.rstrip("/") + "/" + filename
    print("  -> telechargement lftp (%s) de %s@%s ..." % (protocol, user, remote_full))
    local_dir = os.path.dirname(local_path) or "."
    os.makedirs(local_dir, exist_ok=True)
    # "-o <lfile>" (minuscule) fixe le nom LOCAL exact du fichier telecharge.
    # A ne pas confondre avec "-O <dir>" (majuscule) qui place le fichier
    # dans un repertoire mais sous le nom REMOTE (bug precedent : le fichier
    # se retrouvait sous son nom distant, sans le prefixe xp1_/xp2_ attendu).
    cmd = [
        "lftp", "%s://%s@%s" % (protocol, user, host),
        "-e", "get %s -o %s; bye" % (remote_full, local_path),
    ]
    print("     commande: %s" % " ".join(cmd))
    subprocess.run(cmd, check=True)
    if not os.path.exists(local_path):
        raise RuntimeError("Echec du telechargement de %s (fichier local "
                            "attendu introuvable : %s)" % (remote_full, local_path))


# ---------------------------------------------------------------------------
# Lecture des champs avec epygram
# ---------------------------------------------------------------------------

def open_resource(path):
    import epygram
    epygram.init_env()
    return epygram.formats.resource(path, openmode="r")


def read_fa_scalar(resource, param, level):
    """Lit un champ scalaire FA de la forme S{level:03d}{param}."""
    fieldname = "S%03d%s" % (level, param)
    fld = resource.readfield(fieldname)
    if fld.spectral:
        fld.sp2gp()
    return fld


def _speed_and_direction(u_data, v_data, template_field):
    """Construit 2 champs epygram (force, direction meteo -- d'ou vient le
    vent) a partir de tableaux numpy u,v et d'un champ modele pour la
    geometrie (deepcopy)."""
    speed = np.sqrt(u_data ** 2 + v_data ** 2)
    direction = (270.0 - np.degrees(np.arctan2(v_data, u_data))) % 360.0
    f_speed = template_field.deepcopy()
    f_speed.setdata(speed)
    f_dir = template_field.deepcopy()
    f_dir.setdata(direction)
    return f_speed, f_dir


def read_fa_wind_uv(resource, level):
    """Lit U/V PHYS a un niveau FA donne (quand ils existent dans le
    fichier) et renvoie (force, direction)."""
    fu = resource.readfield("S%03dWIND.U.PHYS" % level)
    fv = resource.readfield("S%03dWIND.V.PHYS" % level)
    if fu.spectral:
        fu.sp2gp()
    if fv.spectral:
        fv.sp2gp()
    return _speed_and_direction(fu.getdata(), fv.getdata(), fu)


def read_fa_wind_psikhi(resource, level):
    """Calcule le vent (force, direction) a partir de la fonction de
    courant et du potentiel de vitesse spectraux S{level}FONC.COURANT
    (psi) / S{level}POT.VITESSE (khi) -- seuls champs de vent presents
    dans certains fichiers historic (le vent n'y est pas ecrit directement
    en U/V ni en vorticite/divergence).

    Utilise directement epygram.fields.psikhi2uv (utilitaire officiel
    d'epygram pour cette conversion psi/khi -> vent) : aucun calcul
    spectral "maison" n'est refait ici, ce qui evite tout risque d'erreur
    de convention de signe sur l'inversion du laplacien.
    """
    from epygram.fields import psikhi2uv

    psi = resource.readfield("S%03dFONC.COURANT" % level)
    khi = resource.readfield("S%03dPOT.VITESSE" % level)
    if not (psi.spectral and khi.spectral):
        raise RuntimeError("S%03dFONC.COURANT/POT.VITESSE attendus en "
                            "spectral pour le calcul vent<-psi/khi" % level)

    uv = psikhi2uv(psi, khi)  # renvoie u,v deja au point de grille
    u, v = uv.components
    return _speed_and_direction(u.getdata(), v.getdata(), u)


def read_fa_wind(resource, level, source="psikhi"):
    if source == "uv":
        return read_fa_wind_uv(resource, level)
    return read_fa_wind_psikhi(resource, level)


def read_grib_scalar(resource, fid):
    """Lit un champ GRIB via un dictionnaire fid (cles GRIB : shortName,
    typeOfLevel, level, ...). A VERIFIER selon la version d'epygram et le
    contenu reel des fichiers grid.arpege-forecast."""
    fld = resource.readfield(fid)
    if getattr(fld, "spectral", False):
        fld.sp2gp()
    return fld


def read_grib_wind(resource, level_kwargs):
    fid_u = dict(shortName="u", **level_kwargs)
    fid_v = dict(shortName="v", **level_kwargs)
    fu = resource.readfield(fid_u)
    fv = resource.readfield(fid_v)
    return _speed_and_direction(fu.getdata(), fv.getdata(), fu)


def grib_level_kwargs(level):
    """level: '10m' ou un entier (hPa)."""
    if isinstance(level, str) and level.lower().endswith("m"):
        height = int(level.lower().rstrip("m"))
        return dict(typeOfLevel="heightAboveGround", level=height)
    else:
        return dict(typeOfLevel="isobaricInhPa", level=int(level))


def collect_fields(resource, args):
    """Renvoie une liste de (label, field) pour la resource donnee, selon
    --filetype/--params/--levels. Utilise aussi pour la reference (xp3),
    qui partage les memes champs/niveaux que xp1/xp2."""
    out = []
    if args.filetype == "fa":
        levels = args.levels or DEFAULT_FA_LEVELS
        params = args.params or DEFAULT_FA_PARAMS
        for level in levels:
            for param in params:
                if param.upper() == "WIND":
                    speed, direction = read_fa_wind(resource, level, args.wind_source)
                    out.append(("WIND_SPEED_%03d" % level, speed))
                    out.append(("WIND_DIR_%03d" % level, direction))
                else:
                    fld = read_fa_scalar(resource, param, level)
                    out.append(("%s_%03d" % (param.replace(".", ""), level), fld))
    else:
        params = args.params or DEFAULT_GRIB_PARAMS
        for param in params:
            if param.upper() == "WIND":
                lvl_kwargs = grib_level_kwargs(args.grib_wind_level)
                speed, direction = read_grib_wind(resource, lvl_kwargs)
                out.append(("WIND_SPEED_%s" % args.grib_wind_level, speed))
                out.append(("WIND_DIR_%s" % args.grib_wind_level, direction))
            elif param.upper() == "TEMPERATURE":
                lvl_kwargs = grib_level_kwargs(args.grib_temp_level_hpa)
                fid = dict(shortName="t", **lvl_kwargs)
                fld = read_grib_scalar(resource, fid)
                out.append(("TEMPERATURE_%dhPa" % args.grib_temp_level_hpa, fld))
            else:
                raise ValueError("Parametre GRIB non reconnu : %s "
                                "(attendu WIND ou TEMPERATURE ; ajouter un "
                                "cas dans collect_fields() pour en ajouter "
                                "d'autres)" % param)
    return out


# ---------------------------------------------------------------------------
# Tracé + statistiques de score (RMSE, biais vs reference)
# ---------------------------------------------------------------------------

def plot_field(fld, title, out_png):
    """Trace un champ epygram avec cartoplot et sauvegarde en png."""
    fig, ax = fld.cartoplot(title=title,colormap='hot_r')
    fig.savefig(out_png, dpi=120, bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(fig)


def plot_diff_field(fld_diff_template, diff_data, title, out_png):
    """fld_diff_template : champ epygram (deepcopy) dont on remplace les
    donnees par diff_data (colormap divergente centree sur 0 -- adaptee a
    une difference de scores qui peut etre positive ou negative) pour
    beneficier de sa geometrie/cartoplot."""
    f = fld_diff_template.deepcopy()
    f.setdata(diff_data)
    maxval = max(np.abs(np.nanmin(f.data)), np.abs(np.nanmax(f.data)))
    if not np.isfinite(maxval) or maxval == 0:
        maxval = 1.0
    fig, ax = f.cartoplot(title=title, colormap='seismic', minmax=[-maxval, maxval])
    fig.savefig(out_png, dpi=120, bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(fig)


# ---------------------------------------------------------------------------
# Fichier listing : recuperation + diff colore (git word-diff -> HTML)
# (inchange par rapport a diagarpege.py -- compare xp1 vs xp2, pas la
# reference)
# ---------------------------------------------------------------------------

def fetch_listing(args, xp, workdir):
    """Recupere le fichier listing pour l'experience xp dans le meme
    repertoire forecast, et renvoie son chemin local (ou None si
    --no-listing-diff)."""
    if args.no_listing_diff:
        return None
    remote_dir = remote_dir_for_xp(args, xp)
    local_path = os.path.join(workdir, "%s_%s" % (xp, args.listing_filename))
    print("Listing (%s) : %s/%s" % (xp, remote_dir, args.listing_filename))
    fetch_via_lftp(args.protocol, args.user, args.host_hendrix, remote_dir,
                    args.listing_filename, local_path)
    return local_path


# Couleurs approximatives (theme sombre) pour les codes SGR "couleur de
# premier plan" 30-37 / 90-97 emis par `git diff --color=always`.
_ANSI_RE = re.compile(r"\x1b\[([0-9;]*)m")
_SGR_FG = {
    30: "#3b3b3b", 31: "#e06c75", 32: "#98c379", 33: "#d19a66",
    34: "#61afef", 35: "#c678dd", 36: "#56b6c2", 37: "#dcdfe4",
    90: "#5c6370", 91: "#e06c75", 92: "#98c379", 93: "#d19a66",
    94: "#61afef", 95: "#c678dd", 96: "#56b6c2", 97: "#ffffff",
}


def ansi_to_html(text):
    """Convertit une sortie coloree (codes SGR "gras"/"couleur de premier
    plan"/"reset", tels qu'emis par `git diff --color=always`) en HTML
    (des <span style=...> a inserer dans un <pre>). Ne gere pas tous les
    codes SGR possibles, seulement ceux utilises par git diff."""
    out = []
    pos = 0
    span_open = False
    bold = False
    fg = None
    for m in _ANSI_RE.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        pos = m.end()
        codes = [int(c) for c in m.group(1).split(";") if c] or [0]
        for code in codes:
            if code == 0:
                bold, fg = False, None
            elif code == 1:
                bold = True
            elif code == 22:
                bold = False
            elif code in _SGR_FG:
                fg = _SGR_FG[code]
            elif code == 39:
                fg = None
        if span_open:
            out.append("</span>")
            span_open = False
        style = []
        if bold:
            style.append("font-weight:bold")
        if fg:
            style.append("color:%s" % fg)
        if style:
            out.append("<span style='%s'>" % ";".join(style))
            span_open = True
    out.append(html.escape(text[pos:]))
    if span_open:
        out.append("</span>")
    return "".join(out)


def git_word_diff_html(path1, path2):
    """Lance `git diff --no-index --word-diff=color` entre 2 fichiers et
    renvoie le HTML colore correspondant (None si l'un des chemins est
    manquant)."""
    if not (path1 and path2 and os.path.exists(path1) and os.path.exists(path2)):
        return None
    result = subprocess.run(
        ["git", "diff", "--no-index", "--word-diff=color", "--color=always",
        "--no-prefix", path1, path2],
        capture_output=True, text=True)
    if result.returncode not in (0, 1):
        raise RuntimeError("git diff a echoue (code %d) : %s"
                            % (result.returncode, result.stderr))
    if not result.stdout.strip():
        return "<em>(fichiers listing identiques)</em>"
    return "<pre style='background:#1e1e1e;color:#ddd;padding:10px;" \
        "overflow:auto;white-space:pre-wrap'>%s</pre>" % ansi_to_html(result.stdout)


# ---------------------------------------------------------------------------
# index.html + déploiement
# ---------------------------------------------------------------------------

def write_index_html(workdir, entries, title, xp1, xp2, xp3,
                     listing_diff_html=None):
    """entries: liste de dicts {label, png_diff_biais, png_diff_rmse,
    biais1, rmse1, biais2, rmse2, diff_biais, diff_rmse}

    png_diff_biais/png_diff_rmse : cartes de (score(xp1) - score(xp2)),
    biais/rmse etant calcules par rapport a la reference xp3.
    """
    out = ["<html><head><meta charset='utf-8'>",
            "<title>%s</title>" % title,
            "<style>body{font-family:sans-serif} "
            "div.row{margin-bottom:30px} img{max-width:45%%;margin-right:2%%} "
            "h2{margin-bottom:4px}</style></head><body>",
            "<h1>%s</h1>" % title,
            "<p>Reference des scores : <b>%s</b> (echeance 0, a l'instant "
            "correspondant). Cartes = difference entre les scores de "
            "<b>%s</b> et de <b>%s</b> par rapport a cette reference "
            "(rouge/bleu = %s plus proche/eloigne de la reference).</p>"
            % (xp3, xp1, xp2, xp1)]
    for e in entries:
        out.append("<div class='row'>")
        out.append("<h2>%s</h2>" % e["label"])
        out.append("<img src='%s' alt='difference des biais'>" % e["png_diff_biais"])
        out.append("<img src='%s' alt='difference des RMSE'>" % e["png_diff_rmse"])
        out.append("<p>%s vs %s : biais = %.4g, RMSE = %.4g<br>"
                    "%s vs %s : biais = %.4g, RMSE = %.4g<br>"
                    "<b>Difference (%s - %s) : &Delta;biais = %.4g, "
                    "&Delta;RMSE = %.4g</b></p>"
                    % (xp1, xp3, e["biais1"], e["rmse1"],
                        xp2, xp3, e["biais2"], e["rmse2"],
                        xp1, xp2, e["diff_biais"], e["diff_rmse"]))
        out.append("</div>")
    if listing_diff_html:
        out.append("<h2>Diff du fichier listing (%s vs %s)</h2>" % (xp1, xp2))
        out.append(listing_diff_html)
    out.append("</body></html>")
    path = os.path.join(workdir, "index.html")
    with open(path, "w") as f:
        f.write("\n".join(out))
    return path


def deploy(workdir, user, host_images, remote_full_dir):
    print("Deploiement vers %s:%s ..." % (host_images, remote_full_dir))
    subprocess.run(
        ["ssh", "%s@%s" % (user, host_images), "mkdir -p %s" % remote_full_dir],
        check=True)
    png_files = [f for f in os.listdir(workdir) if f.endswith(".png")]
    if png_files:
        subprocess.run(
            ["scp"] + [os.path.join(workdir, f) for f in png_files] +
            ["%s@%s:%s" % (user, host_images, remote_full_dir)],
            check=True)
    subprocess.run(
        ["scp", os.path.join(workdir, "index.html"),
        "%s@%s:%s" % (user, host_images, remote_full_dir)],
        check=True)
    print("OK. A consulter sur http://intra.cnrm.meteo.fr/algo/%s/ (URL exacte selon la "
        "configuration du serveur web sur %s)" % (remote_full_dir[4:],
                                                    host_images))


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    args = build_argparser().parse_args()
    os.makedirs(args.workdir, exist_ok=True)

    if args.local_file_ref and args.dat2:
        raise ValueError("--local-file-ref n'est utilisable qu'avec une "
                        "seule date (--dat sans --dat2) : la reference "
                        "change a chaque date de la plage")

    # Generer la liste des dates a traiter
    dates = date_range(args.dat, args.dat2)
    multi_day = len(dates) > 1

    if multi_day:
        print("Traitement sur %d jours : %s a %s" % (len(dates), dates[0], dates[-1]))

    # 1bis) fichier listing de xp1/xp2 + diff colore (inchange, ne concerne
    # pas la reference)
    listing_diff_html = None
    listing1_kept = None
    listing2_kept = None

    # Pour accumuler les diff (xp1-ref) et (xp2-ref) sur tous les jours
    accumulated_diffs1 = {}  # label -> liste des arrays (xp1 - ref) par jour
    accumulated_diffs2 = {}  # label -> liste des arrays (xp2 - ref) par jour
    accumulated_field_templates = {}  # label -> template de champ pour cartoplot

    for day_idx, dat in enumerate(dates):
        print("\n=== Traitement date %s (echeance %02dh) ===" % (dat, args.ech))

        # Modifier args.dat temporairement pour cette iteration
        old_dat = args.dat
        args.dat = dat

        # 1) obtenir les fichiers locaux de xp1 et xp2 (a l'echeance --ech)
        if args.local_file1:
            local1 = args.local_file1
        else:
            remote_dir1, filename1 = remote_path_and_filename(args, args.xp1)
            local1 = os.path.join(args.workdir, "%s_%s_%s" % (args.xp1, dat, filename1))
            print("Experience 1 (%s) : %s/%s" % (args.xp1, remote_dir1, filename1))
            fetch_via_lftp(args.protocol, args.user, args.host_hendrix, remote_dir1, filename1, local1)

        if args.local_file2:
            local2 = args.local_file2
        else:
            remote_dir2, filename2 = remote_path_and_filename(args, args.xp2)
            local2 = os.path.join(args.workdir, "%s_%s_%s" % (args.xp2, dat, filename2))
            print("Experience 2 (%s) : %s/%s" % (args.xp2, remote_dir2, filename2))
            fetch_via_lftp(args.protocol, args.user, args.host_hendrix, remote_dir2, filename2, local2)

        # 1ter) obtenir le fichier de reference (xp3, echeance 0, a
        # l'instant DAT+RESEAU+ECH)
        dat_ref, reseau_ref = reference_datetime(dat, args.reseau, args.ech)
        if args.local_file_ref:
            local_ref = args.local_file_ref
        else:
            ref_args = reference_args(args, dat_ref, reseau_ref)
            remote_dir_ref, filename_ref = remote_path_and_filename(ref_args, args.xp3)
            local_ref = os.path.join(
                args.workdir, "%s_%s_%s_%s" % (args.xp3, dat_ref, reseau_ref, filename_ref))
            print("Reference (%s), echeance 0, valide %s %sUTC (= %s + %02dh) : %s/%s"
                % (args.xp3, dat_ref, reseau_ref, dat, args.ech, remote_dir_ref, filename_ref))
            fetch_via_lftp(args.protocol, args.user, args.host_hendrix, remote_dir_ref, filename_ref, local_ref)

        # Recuperer le listing xp1/xp2 une seule fois (sur la premiere date)
        if day_idx == 0 and not args.no_listing_diff and not (args.local_file1 or args.local_file2):
            try:
                listing1_kept = fetch_listing(args, args.xp1, args.workdir)
                listing2_kept = fetch_listing(args, args.xp2, args.workdir)
                listing_diff_html = git_word_diff_html(listing1_kept, listing2_kept)
            except Exception as exc:
                print("!! diff du listing impossible (%s), on continue sans" % exc)

        # 2) ouverture epygram
        print("Ouverture de %s, %s et %s (reference) avec epygram ..." % (local1, local2, local_ref))
        r1 = open_resource(local1)
        r2 = open_resource(local2)
        r_ref = open_resource(local_ref)

        if args.list_fields:
            print("--- Champs disponibles dans %s (xp1) ---" % local1)
            for f in r1.listfields():
                print(" ", f)
            print("--- Champs disponibles dans %s (reference) ---" % local_ref)
            for f in r_ref.listfields():
                print(" ", f)
            args.dat = old_dat
            return

        # 3) champs
        fields1 = collect_fields(r1, args)
        fields2 = dict(collect_fields(r2, args))
        fields_ref = dict(collect_fields(r_ref, args))

        # Accumuler les differences (xp1-ref) et (xp2-ref) pour chaque champ
        for label, fld1 in fields1:
            if label not in fields2 or label not in fields_ref:
                if day_idx == 0:
                    print("!! champ %s absent de xp2 ou de la reference, ignore" % label)
                continue

            fld2 = fields2[label]
            fld_ref = fields_ref[label]
            data1 = fld1.getdata()
            data2 = fld2.getdata()
            data_ref = fld_ref.getdata()

            diff1 = np.asarray(data1) - np.asarray(data_ref)
            diff2 = np.asarray(data2) - np.asarray(data_ref)

            if label not in accumulated_diffs1:
                accumulated_diffs1[label] = []
                accumulated_diffs2[label] = []
                accumulated_field_templates[label] = fld1

            accumulated_diffs1[label].append(diff1)
            accumulated_diffs2[label].append(diff2)

        # Restaurer args.dat
        args.dat = old_dat

    # 4) Calculer les scores (biais, RMSE) et leur difference, et tracer
    print("\n=== Calcul des scores (biais, RMSE vs %s) ===" % args.xp3)

    entries = []
    for label in accumulated_diffs1:
        # Stacker toutes les diff (shape: (n_days, *field_shape))
        all_diffs1 = np.array(accumulated_diffs1[label])
        all_diffs2 = np.array(accumulated_diffs2[label])

        # Scores globaux (moyenne sur tous les jours ET tous les points)
        biais1 = float(np.nanmean(all_diffs1))
        rmse1 = float(np.sqrt(np.nanmean(all_diffs1 ** 2)))
        biais2 = float(np.nanmean(all_diffs2))
        rmse2 = float(np.sqrt(np.nanmean(all_diffs2 ** 2)))
        diff_biais_global = biais1 - biais2
        diff_rmse_global = rmse1 - rmse2

        # Cartes de score (par point de grille : moyenne/RMS sur les jours)
        biais1_field = np.nanmean(all_diffs1, axis=0)
        rmse1_field = np.sqrt(np.nanmean(all_diffs1 ** 2, axis=0))
        biais2_field = np.nanmean(all_diffs2, axis=0)
        rmse2_field = np.sqrt(np.nanmean(all_diffs2 ** 2, axis=0))

        # Difference des scores entre xp1 et xp2 (cartes)
        diff_biais_field = biais1_field - biais2_field
        diff_rmse_field = rmse1_field - rmse2_field

        template_fld = accumulated_field_templates[label]

        png_diff_biais = os.path.join(
            args.workdir, "%s_diffbiais_%s-%s_ref%s.png" % (label, args.xp1, args.xp2, args.xp3))
        png_diff_rmse = os.path.join(
            args.workdir, "%s_diffrmse_%s-%s_ref%s.png" % (label, args.xp1, args.xp2, args.xp3))

        date_range_str = ("%s to %s" % (dates[0], dates[-1]) if multi_day else dates[0])
        title_biais = ("%s - %sbiais(%s)-biais(%s)%s vs ref %s (%s ech %02dh) | %sbiais=%.4g"
                    % (label, "\u0394", args.xp1, args.xp2, "", args.xp3,
                        date_range_str, args.ech, "\u0394", diff_biais_global))
        title_rmse = ("%s - %sRMSE(%s)-RMSE(%s) vs ref %s (%s ech %02dh) | %sRMSE=%.4g"
                    % (label, "\u0394", args.xp1, args.xp2, args.xp3,
                        date_range_str, args.ech, "\u0394", diff_rmse_global))

        print("Trace %s (difference biais et RMSE, %s vs %s, ref %s) ..."
            % (label, args.xp1, args.xp2, args.xp3))
        plot_diff_field(template_fld, diff_biais_field, title_biais, png_diff_biais)
        plot_diff_field(template_fld, diff_rmse_field, title_rmse, png_diff_rmse)

        entries.append(dict(label=label,
                           png_diff_biais=os.path.basename(png_diff_biais),
                           png_diff_rmse=os.path.basename(png_diff_rmse),
                           biais1=biais1, rmse1=rmse1,
                           biais2=biais2, rmse2=rmse2,
                           diff_biais=diff_biais_global, diff_rmse=diff_rmse_global))

    # 5) index.html
    if multi_day:
        page_title = ("ARPEGE score %s vs %s (ref %s) - %s to %s echeance %02dh"
                    % (args.xp1, args.xp2, args.xp3, dates[0], dates[-1], args.ech))
    else:
        page_title = ("ARPEGE score %s vs %s (ref %s) - %s echeance %02dh"
                    % (args.xp1, args.xp2, args.xp3, args.dat, args.ech))

    write_index_html(args.workdir, entries, page_title, args.xp1, args.xp2, args.xp3,
                     listing_diff_html)
    print("index.html + %d png ecrits dans %s" % (2 * len(entries), args.workdir))

    # 6) déploiement
    if not args.no_deploy:
        if multi_day:
            remote_dir = args.remote_dir or ("%s_%s_ech%02d_score_%s-%s_ref%s"
                                            % (dates[0], args.reseau, args.ech,
                                                args.xp1, args.xp2, args.xp3))
        else:
            remote_dir = args.remote_dir or ("%s_%s_ech%02d_score_%s-%s_ref%s"
                                            % (args.dat, args.reseau, args.ech,
                                                args.xp1, args.xp2, args.xp3))
        remote_full_dir = args.images_base.rstrip("/") + "/" + remote_dir
        deploy(args.workdir, args.user, args.host_images, remote_full_dir)
    else:
        print("(--no-deploy) : pas de publication sur %s" % args.host_images)


if __name__ == "__main__":
    main()

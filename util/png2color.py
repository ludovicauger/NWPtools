#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import math
import webcolors
import numpy as np
import argparse
# work on belenos with python/3.10... module
#create virutal environment and install
# numpy pillow webcolors


# Create the parser
parser = argparse.ArgumentParser(description="A simple script to demonstrate argument parsing.")

# Add arguments
parser.add_argument("experience", type=str, help="image file of the experiment")
parser.add_argument("--base", "-b", type=str, help="image file of the base experiment")
parser.add_argument("--reference", "-r", type=str, help="image file of the reference/observation data")

# Parse the arguments
args = parser.parse_args()


def couleur_la_plus_proche(rgb):
    """Retourne le nom de la couleur CSS la plus proche."""
    try:
        return webcolors.rgb_to_name(rgb)
    except ValueError:
        pass

    min_distance = float("inf")
    couleur_proche = None

    for hex_code, nom in webcolors._definitions._CSS3_HEX_TO_NAMES.items():
        r, g, b = webcolors.hex_to_rgb(hex_code)

        distance = (
            (rgb[0] - r) ** 2
            + (rgb[1] - g) ** 2
            + (rgb[2] - b) ** 2
        )

        if distance < min_distance:
            min_distance = distance
            couleur_proche = nom

    return couleur_proche


def set_couleurs_vers_png(
    set_couleurs,
    fichier_sortie="nuancier.png",
    colonnes=5,
    largeur_case=180,
    hauteur_case=90,
    taille_police=18,
):
    """
    Crée un PNG à partir d'un set de noms de couleurs.

    Exemple :
    set_couleurs_vers_png({'snow','gray','red'})
    """

    couleurs = sorted(list(set_couleurs))

    nb = len(couleurs)
    lignes = math.ceil(nb / colonnes)

    largeur = colonnes * largeur_case
    hauteur = lignes * hauteur_case

    img = Image.new("RGB", (largeur, hauteur), "white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", taille_police)
    except:
        font = ImageFont.load_default()

    for i, nom in enumerate(couleurs):

        ligne = i // colonnes
        colonne = i % colonnes

        x0 = colonne * largeur_case
        y0 = ligne * hauteur_case

        x1 = x0 + largeur_case
        y1 = y0 + hauteur_case

        # Dessin du rectangle coloré
        draw.rectangle((x0, y0, x1, y1),
                       fill=nom,
                       outline="black",
                       width=1)

        # Choix automatique de la couleur du texte
        r, g, b = Image.new("RGB", (1, 1), nom).getpixel((0, 0))

        luminance = 0.299*r + 0.587*g + 0.114*b

        couleur_texte = "black" if luminance > 140 else "white"

        # Centrage du texte
        bbox = draw.textbbox((0, 0), nom, font=font)

        largeur_texte = bbox[2] - bbox[0]
        hauteur_texte = bbox[3] - bbox[1]

        xt = x0 + (largeur_case - largeur_texte) / 2
        yt = y0 + (hauteur_case - hauteur_texte) / 2

        draw.text(
            (xt, yt),
            nom,
            fill=couleur_texte,
            font=font
        )

    img.save(fichier_sortie)

    print(f"Image créée : {fichier_sortie}")


def png_vers_matrice_couleurs(fichier_png):
    image = Image.open(fichier_png).convert("RGB")
    largeur, hauteur = image.size
    matrice = []
    for y in range(hauteur):
        ligne = []
        print(y,range(hauteur))
        for x in range(largeur):
            rgb = image.getpixel((x, y))
            ligne.append(couleur_la_plus_proche(rgb))
        matrice.append(ligne)
    return matrice


def equitable_threat_score(prevu, observe, seuil=1.0):
    """
    Calcule l'Equitable Threat Score (ETS).
    Parameters
    ----------
    prevu : array-like 2D
        Pluie prévue.
    observe : array-like 2D
        Pluie observée.
    seuil : float
        Seuil de l'événement.
    Returns
    -------
    ets : float
    stats : dict
        Contient H, M, F, CN.
    """
    prevu = np.asarray(prevu)
    observe = np.asarray(observe)
    if prevu.shape != observe.shape:
        raise ValueError("Les tableaux doivent avoir la même taille.")
    prev_event = prevu >= seuil
    obs_event = observe >= seuil
    H = np.sum(prev_event & obs_event)
    M = np.sum(~prev_event & obs_event)
    F = np.sum(prev_event & ~obs_event)
    CN = np.sum(~prev_event & ~obs_event)
    N = H + M + F + CN
    Hr = (H + F) * (H + M) / N
    denominateur = H + M + F - Hr
    if denominateur == 0:
        ets = np.nan
    else:
        ets = (H - Hr) / denominateur
    stats = {
        "hits": H,
        "misses": M,
        "false_alarms": F,
        "correct_negatives": CN,
    }
    return ets, stats
def reech(matrice, N=50):
    matrice = np.array(matrice)
    h, w = matrice.shape
    resultat = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            # bornes de la boîte
            r0 = int(i * h / N)
            r1 = int((i + 1) * h / N)
            c0 = int(j * w / N)
            c1 = int((j + 1) * w / N)
            boite = matrice[r0:r1, c0:c1]
            resultat[i, j] = np.mean(boite)
    return resultat

def matrice_couleurs_vers_real(matrice_couleur):
    colortab={'cyan': 0.6, 'silver':0.0, 'darkred': 400.0, 'purple':18.0, 'darkblue':7.0, 'royalblue':3.0, 'darkmagenta':18.0, 'ghostwhite':0.0, 'maroon':400.0, 'saddlebrown':125.0, 'darkcyan':0.6, 'darkviolet':18.0, 'darkslategray':0.0, 'magenta':38.0, 'lightseagreen':0.6, 'firebrick':250.0, 'indigo':18.0, 'lightgray':0.0, 'lavender':0.0, 'blue':7.0, 'snow':0.0, 'white':0.0, 'darkgray':0.0, 'darkorange':75.0, 'whitesmoke':0.0, 'teal':0.6, 'mediumblue':7.0, 'midnightblue':7.0, 'dimgray':0.0, 'gray':0.0, 'orangered':125.0, 'chocolate':125.0, 'dodgerblue':1.5, 'darkgoldenrod':75.0, 'navy':7.0, 'black':0.0, 'gainsboro':0.0, 'lightslategray':0.0, 'darkturquoise':0.6}
    matrice_real = []
    for ligne in matrice_couleur:
        ligne_real=[]
        for elem in ligne:
             ligne_real.append(colortab.get(elem,0.0))       
        matrice_real.append(ligne_real)
    return matrice_real

# Exemple
#matrice = png_vers_matrice_couleurs("20260118pluie.png")
#unique_vals = {elem for row in matrice for elem in row}
#print(unique_vals)
#set_couleurs_vers_png(unique_vals,"nuancier.png")
#exit()
print(args.base,args.experience,args.reference)
obs=reech(matrice_couleurs_vers_real(png_vers_matrice_couleurs(args.reference)))
arome=reech(matrice_couleurs_vers_real(png_vers_matrice_couleurs(args.base)))
deode=reech(matrice_couleurs_vers_real(png_vers_matrice_couleurs(args.experience)))
ets_deode=[]
ets_arome=[]
for seuil in (0.1,1.0,5,10,20,50,100,300):
  ets,stats=equitable_threat_score(deode, obs, seuil)
  ets_deode.append(ets)
  ets,stats=equitable_threat_score(arome, obs, seuil)
  ets_arome.append(ets)
print("deode ets",ets_deode)
print("arome ets",ets_arome)


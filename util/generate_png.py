#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont
import os

def create_image_grid(input_dir, output_path, images_per_row=3):
    # Récupérer tous les fichiers .png dans le répertoire
    png_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith('.png')])

    if not png_files:
        raise ValueError("Aucun fichier .png trouvé dans le répertoire.")

    # Charger toutes les images
    images = []
    for file in png_files:
        img_path = os.path.join(input_dir, file)
        img = Image.open(img_path)
        images.append((img, file))

    # Déterminer la taille de chaque image (on suppose qu'elles ont la même taille)
    img_width, img_height = images[0][0].size

    # Calculer la taille de la grille
    num_rows = (len(images) + images_per_row - 1) // images_per_row
    grid_width = images_per_row * img_width
    grid_height = num_rows * (img_height + 40)  # 40 pixels pour la légende

    # Créer une nouvelle image pour la grille
    grid = Image.new('RGB', (grid_width, grid_height), (255, 255, 255))
    draw = ImageDraw.Draw(grid)

    # Charger une police pour la légende
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # Placer les images et les légendes
    for i, (img, filename) in enumerate(images):
        row = i // images_per_row
        col = i % images_per_row
        x = col * img_width
        y = row * (img_height + 40)

        # Coller l'image
        grid.paste(img, (x, y))

        # Ajouter la légende (nom du fichier)
        legend = filename
        text_width = draw.textlength(legend, font=font)
        text_x = x + (img_width - text_width) // 2
        text_y = y + img_height + 10
        draw.text((text_x, text_y), legend, fill=(0, 0, 0), font=font)

    # Sauvegarder la grille
    grid.save(output_path)
    print(f"Grille sauvegardée sous : {output_path}")

# Exemple d'utilisation
input_directory = "."  # Remplace par ton répertoire
output_file = "grille_images.png"  # Nom du fichier de sortie
create_image_grid(input_directory, output_file)


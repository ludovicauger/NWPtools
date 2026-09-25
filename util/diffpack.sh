#!/bin/bash

# Chemin de base pour les répertoires à comparer
local_dir="./src/local"
main_dir="./src/main"

# Boucle sur tous les fichiers .F90 dans ./src/local
find "$local_dir" -type f -name "*.F90" | while read -r local_file; do
    # Calcul du chemin relatif par rapport à ./src/local
    relative_path="${local_file#$local_dir/}"

    # Construction du chemin du fichier correspondant dans ./src/main
    main_file="$main_dir/$relative_path"

    # Vérification que le fichier existe dans ./src/main
    if [ -f "$main_file" ]; then
        echo "Comparaison de $local_file et $main_file"
        git diff --no-index --word-diff "$local_file" "$main_file"
    else
        echo "Avertissement : Le fichier $main_file n'existe pas. Impossible de comparer."
    fi
done

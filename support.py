import csv
import os
from typing import List

import pygame

def import_csv_layout(filename: str) -> List[List[str]]:
    """
    Imports a CSV file and returns a 2D list of strings.
    """
    terrain_map = []
    with open(filename, 'r') as level_map:
        layout = csv.reader(level_map, delimiter=',')

        for row in layout:
            terrain_map.append(list(row))
        
        return terrain_map

def import_folder(folder: str) -> List[str]:
    """
    Imports a files under folder and returns a 2D list of strings.
    """
    surface_list = []
    for _root, _, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(_root, file)
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list
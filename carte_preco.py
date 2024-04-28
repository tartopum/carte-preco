import sys
import argparse
from collections import defaultdict
import pathlib

from haversine import haversine
import networkx as nx
import shapefile


def compute_distances(shapes):
    points = []
    # Les points contigus géographiquement le sont dans le shp donc on ne
    # calcule que la distance avec i+1
    for i in range(len(shapes) - 1):
        lng1, lat1 = shapes[i].points[0]
        lng2, lat2 = shapes[i+1].points[0]
        yield i, i+1, round(haversine((lat1, lng1), (lat2, lng2)) * 100000)  # cm


def group_points(shapes, distance_thresh):
    # Pour regrouper les points, on crée un graphe en connectant entre eux les
    # points appartenant à la même zone. Si un point A est "proche" d'un point B
    # et que ce point B est "proche" d'un point C, alors A, B et C appartiennent
    # à la même zone.
    graph = nx.Graph()
    for i, j, dist in compute_distances(shapes):
        if dist <= distance_thresh:
            graph.add_edge(i, j)
    return nx.connected_components(graph)


def main(path, distance_thresh, dose):
    """Le shapefile est exporté de MyJohnDeere au format zip. Il comporte trois
    fichiers :

    * .shp : la liste des relevés GPS où il y a des fleurs
    * .shx : l'index du .shp
    * .dbf : les données associées à chaque point, notamment la vitesse du
             véhicule et la largeur de la bande

    Pour générer le shp, l'agriculteur parcourt le rang avec son tracteur et
    enregistre un tracé avec la console GPS. Quand il voit des fleurs au niveau
    où il passe, il active l'enregistrement, le désactive sinon. Nous obtenons
    donc des points GPS correspondant aux relevés GPS quand l'agriculteur
    a indiqué qu'il y avait des fleurs.

    L'objectif est de générer un shp avec des rectangles sur le rang représentant
    les zones fleuries. Le pulvé s'active automatiquement quand il détecte
    qu'il est dans une telle zone. Cela se fait en plusieurs étapes :

    1. Passer d'un ensemble de points à des zones : il faut regrouper les relevés
       GPS qu'on considère appartenir à la même zone.
    2. Identifier l'axe du rang à partir des points
    3. Pour chaque zone (groupe de points), dessiner un rectangle aligné sur
       l'axe du rang de la longueur du groupe de points et de la largeur spécifiée
       dans le dbf.

    On génère le dbf correspondant avec une seule colonne "Dose" dont la valeur
    représente le débit de pulvérisation. On permet pour le moment de spécifier
    une seule dose pour toutes les zones (il n'y a pas de notion de niveau de
    fleuraison).

    On ne dessine les rectangles que sur les zones fleuries car la console, si
    le pulvé n'est pas dans un rectangle, considère qu'il ne faut pas traiter.
    Si ce n'était pas le cas, il faudrait dessiner des rectangles sur toute la
    longueur du rang et, pour ceux ne correspond pas à une zone fleurie, définir
    une dose de traitement à 0 dans le dbf.
    """
    sf = shapefile.Reader(path)
    groups = list(group_points(sf.shapes(), distance_thresh))
    print(len(groups))
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("--distance_thresh", type=int, default=240)
    parser.add_argument("--dose", type=int, default=700)
    args = parser.parse_args(sys.argv[1:])
    main(args.path, args.distance_thresh, args.dose)

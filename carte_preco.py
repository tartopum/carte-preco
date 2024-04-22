import sys
import argparse
from collections import defaultdict
import pathlib

from haversine import haversine
import networkx as nx
import shapefile


def compute_distances(shapes):
    points = []
    for i, first_shape in enumerate(shapes):
        for j, second_shape in enumerate(shapes):
            if i >= j:
                # Inutile de calculer la distance (b, a) si on connait déjà (a, b)
                continue
            lng1, lat1 = shapes[i].points[0]
            lng2, lat2 = shapes[j].points[0]
            yield i, j, round(haversine((lat1, lng1), (lat2, lng2)) * 100000)  # cm


def main(path, distance_thresh):
    sf = shapefile.Reader(path)
    distances = compute_distances(sf.shapes())
    graph = nx.Graph()
    for i, j, dist in compute_distances(sf.shapes()):
        if dist <= distance_thresh:
            graph.add_edge(i, j)
    print(len(list(nx.connected_components(graph))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("--distance_thresh", type=int, default=240)
    args = parser.parse_args(sys.argv[1:])
    main(args.path, args.distance_thresh)

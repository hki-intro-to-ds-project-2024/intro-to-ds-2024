import geopy.distance

class Node:
    def __init__(self, longitude: int, latitude: int):
        self.coords = (longitude, latitude)
        self.rides = []
        self.distance = []

    def __repr__(self):
        return f"(lat:{self.coords[0]}, long:{self.coords[1]})"


def node_distance_from_node(first_node: Node, second_node: Node) -> float:
    """
    Calculate the distance between two nodes

    Args:
        first_node (Node): the first node
        second_node (Node): the second node

    Returns:
        float: the distance between the two nodes
    """
    coords_1 = (first_node.latitude, first_node.longitude)
    coords_2 = (second_node.latitude, second_node.longitude)
    return geopy.distance.geodesic(coords_1, coords_2).km

import geopy.distance

class Node:
    def __init__(self, lat: int, lng: int):
        self.coords = (lat, lng)
        self.rides = []
        self.distance = []

    def get_node_json(self):
        return {
            "lat": self.coords[0],
            "lng": self.coords[1]
        }

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
    coords_1 = (first_node.lat, first_node.lng)
    coords_2 = (second_node.lat, second_node.lng)
    return geopy.distance.geodesic(coords_1, coords_2).km

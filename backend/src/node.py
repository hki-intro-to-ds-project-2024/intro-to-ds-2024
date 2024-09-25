import geopy.distance

class Node:
    def __init__(self, longitude: int, latitude: int):
        self.longitude = longitude
        self.latitude  = latitude

    def __repr__(self):
        return f"(lat:{self.latitude}, long:{self.longitude})"


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

if __name__ == "__main__":
    coords_1 = Node(2,0)
    coords_2 = Node(0, 0)
    print(node_distance_from_node(coords_1, coords_2))
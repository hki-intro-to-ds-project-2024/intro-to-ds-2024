
from node import Node

class Analytics:
    def __init__(self):
        self.nodes: List[Node] = []

    def add_node(self, node: Node):
        self.nodes.append(node)

if __name__ == "__main__":
    analytics = Analytics()

    # read csv
    """
    for row in data: 
        longitude = ???
        latitude  =  ???
        node = Node(longitude, latitude)
        analytics.nodes.append(node)
    """

    latlongs = [(60.192059, 24.945831), (60.191, 25), (60.192059, 24.945831)]

    for latlong in latlongs: 
        longitude = latlong[0]
        latitude  = latlong[1]
        node = Node(longitude, latitude)
        analytics.nodes.append(node)

    print(analytics.nodes)
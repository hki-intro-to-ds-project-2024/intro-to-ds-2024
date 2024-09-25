
from node import Node
import pandas as pd
from config import DATA_DIR

class Analytics:
    def __init__(self):
        self.nodes: List[Node] = []

    def add_node(self, node: Node):
        self.nodes.append(node)

if __name__ == "__main__":
    analytics = Analytics()

    
    data = pd.read_csv(DATA_DIR / "2021/2021-04.csv")
    print(data)
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
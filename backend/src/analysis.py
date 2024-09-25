
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

    
    data_rides = pd.read_csv(DATA_DIR / "rides_2021/2021-04.csv")
    #print(data_rides)

    data_stops = pd.read_csv(DATA_DIR / "stops/Helsingin_ja_Espoon_kaupunkipyöräasemat_avoin.csv")
    print(data_stops)    

    nodes = [Node(x, y) for x, y in zip(data_stops['x'], data_stops['y'])]
    analytics.nodes = nodes

    print(analytics.nodes)

    print(len(analytics.nodes))
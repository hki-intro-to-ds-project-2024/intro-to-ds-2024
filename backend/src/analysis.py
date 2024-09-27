
from src.node import Node
import pandas as pd
from src.config import DATA_DIR

class Analytics:
    def __init__(self):
        self.node = self._get_node_locs()

    def add_node(self, node: Node) -> None:
        self.nodes.append(node)

    def _get_node_locs(self) :
        data_stops = pd.read_csv(DATA_DIR / "stops/Helsingin_ja_Espoon_kaupunkipyöräasemat_avoin.csv")
        return [Node(x, y) for x, y in zip(data_stops['x'], data_stops['y'])]



if __name__ == "__main__":    
    data_rides = pd.read_csv(DATA_DIR / "rides_2021/2021-04.csv")
    print(analytics.nodes)
    print(len(analytics.nodes))
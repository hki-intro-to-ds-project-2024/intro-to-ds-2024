DATA_DIR = Path(__file__).parent / "data"

class Analytics:
    def __init__(self):
        self.nodes: List[Node] = []

    def add_node(self, node: Node):
        self.nodes.append(node)


analytics = Analytics()

# read csv

"""
for row in data: 
    longitude = ???
    latitude  =  ???
    node = Node(longitude, latitude)
    analytics.nodes.append(node)
"""
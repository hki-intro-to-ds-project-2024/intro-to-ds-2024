DATA_DIR = Path(__file__).parent / "data"

class Node:
    def __init__(self, longitude, latitude):
        self.longitude = longitude
        self.latitude  = latitude

class Analytics:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)


analytics = Analytics()

# import csv

"""
for row in data: 
    longitude = ???
    latitude  =  ???
    node = Node(longitude, latitude)
    analytics.nodes.append(node)
"""
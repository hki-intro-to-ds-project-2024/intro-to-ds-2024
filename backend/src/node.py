
class Node:
    def __init__(self, longitude: int, latitude: int):
        self.longitude = longitude
        self.latitude  = latitude

    def __str__(self):
        return f"({self.latitude}, {self.longitude})"

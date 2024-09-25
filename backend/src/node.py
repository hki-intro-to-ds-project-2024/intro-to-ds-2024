
class Node:
    def __init__(self, longitude: int, latitude: int):
        self.longitude = longitude
        self.latitude  = latitude

    def __repr__(self):
        return f"(lat:{self.latitude}, long:{self.longitude})"


class Position:
    def __init__(self, latitude: float, longitude: float):
        """
        represents a position on earth

        :param latitude: a latitude from -90 (south pole) to +90 (north pole)
        :param longitude: a longitude from -180 (west) to 0 (Greenwich) to +180 (east)
        """
        self.latitude = latitude
        self.longitude = longitude

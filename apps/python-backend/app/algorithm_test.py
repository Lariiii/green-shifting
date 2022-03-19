import math
import geopy.distance

class Datacenter:
    def __init__(self,name, ist, soll1, soll2, soll3, long, lat):
        self.name = name
        self.ist = ist
        self.soll1 = soll1
        self.soll2 = soll2
        self.soll3 = soll3
        self.long = long
        self.lat = lat

    def __repr__(self):
        return self.name


def main():
    dc1 = Datacenter("dc1", 14, 20, 20, 15, 52.2296756, 21.0122287)
    dc2 = Datacenter("dc2", 14, 8, 7, 0, 52.2296756, 21.0122287)
    dc3 = Datacenter("dc3", 5, 9, 15, 20, 52.406374, 16.9251681)

    shift([dc1, dc2, dc3])


def shift(datacenters):
    capacities = {}
    full = {}
    shifts = {}

    for dc in datacenters:
        average = math.floor((dc.soll1+dc.soll2+dc.soll3)/3)
        if dc.ist < average <= dc.soll1:
            capacities[dc] = (average-dc.ist)
        if dc.ist < dc.soll1 <= average:
            capacities[dc] = (dc.soll1 - dc.ist)
        if average <= dc.soll1 < dc.ist:
            full[dc] = (dc.soll1-dc.ist)
        if dc.soll1 <= average < dc.ist:
            full[dc] = (average-dc.ist)

    print(capacities)
    print(full)

    for c in list(capacities.keys()):
        nearest = get_nearest_dc(c, full.keys())
        while capacities[c] > 0 and full:
            diff = capacities[c]+full[nearest]
            if diff == 0:
                shifts[(nearest, c)] = capacities[c]
                capacities[c] = 0
                del full[nearest]
            elif diff > 0:
                shifts[(nearest, c)] = full[nearest]*-1
                capacities[c] = diff
                del full[nearest]
            else:
                shifts[(nearest, c)] = capacities[c]
                capacities[c] = 0
                full[nearest] = diff
        del capacities[c]

    print(capacities)
    print(full)
    print(shifts)


def get_nearest_dc(dc, neighbors):
    coords_1 = (dc.long, dc.lat)

    nearest_dc = dc
    distance = -1
    for neighbor in neighbors:
        coords_2 = (neighbor.long, neighbor.lat)
        if geopy.distance.distance(coords_1, coords_2).km < distance or distance == -1:
            distance = geopy.distance.distance(coords_1, coords_2).km
            nearest_dc = neighbor

    if nearest_dc == dc:
        raise ValueError('Nearest Datacenter cannot be the datacenter itself')
    return nearest_dc


if __name__ == "__main__":
    main()
import math
import geopy.distance
from random import randint


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
    dc1 = Datacenter("dc1", randint(0,30), randint(0,30), randint(0,30), randint(0,30), 52.2296756, 21.0122287)
    dc2 = Datacenter("dc2", randint(0,30), randint(0,30), randint(0,30), randint(0,30), 52.2296756, 21.0122287)
    dc3 = Datacenter("dc3", randint(0,30), randint(0,30), randint(0,30), randint(0,30), 52.406374, 16.9251681)

    #dc1 = Datacenter("dc1", 25, 17, 18, 2, 52.2296756, 21.0122287)
    #dc2 = Datacenter("dc2", 3, 19, 26, 15, 52.2296756, 21.0122287)
    #dc3 = Datacenter("dc3", 29, 18, 25, 28, 52.406374, 16.9251681)

    #print(dc1)
    #print(dc1.ist, dc1.soll1, dc1.soll2, dc1.soll3)
    #print(dc2)
    #print(dc2.ist, dc2.soll1, dc2.soll2, dc2.soll3)
    #print(dc3)
    #print(dc3.ist, dc3.soll1, dc3.soll2, dc3.soll3)

    shift([dc1, dc2, dc3])


def shift(datacenters):
    capacities = {}
    full = {}
    shifts = {}

    for dc in datacenters:
        average = math.floor((dc.soll1+dc.soll2+dc.soll3)/3)
        if dc.ist < average <= dc.soll1:
            capacities[dc] = (average-dc.ist)
        elif dc.ist < dc.soll1 <= average:
            capacities[dc] = (dc.soll1 - dc.ist)
        elif average <= dc.soll1 < dc.ist:
            full[dc] = (dc.soll1-dc.ist)
        elif dc.soll1 <= average < dc.ist:
            full[dc] = (average-dc.ist)
        dc.soll1 = -1
        dc.soll2 = -1
        dc.soll3 = -1

    #TODO remove
    #print(capacities)
    #print(full)

    for c in list(capacities.keys()):
        while capacities[c] > 0 and full:
            nearest = get_nearest_dc(c, full.keys())
            diff = capacities[c]+full[nearest]
            if diff == 0:
                shifts[(nearest, c)] = capacities[c]
                nearest.ist = nearest.ist - capacities[c]
                c.ist = c.ist + capacities[c]
                capacities[c] = 0
                del full[nearest]
            elif diff > 0:
                shifts[(nearest, c)] = full[nearest]*-1
                nearest.ist = nearest.ist - (full[nearest]*-1)
                c.ist = c.ist + (full[nearest]*-1)
                capacities[c] = diff
                del full[nearest]
            else:
                shifts[(nearest, c)] = capacities[c]
                nearest.ist = nearest.ist - capacities[c]
                c.ist = c.ist + capacities[c]
                capacities[c] = 0
                full[nearest] = diff
        del capacities[c]

    #TODO remove
    #print(capacities)
    #print(full)

    # return liste von fake datacenters und shifts-dict
    #TODO change this to return
    print(shifts, datacenters)




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
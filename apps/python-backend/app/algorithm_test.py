import math
import geopy.distance


def shift(datacenters):
    capacities = {}
    full = {}
    shifts = {}

    for dc in datacenters:
        average = math.floor((dc.datacenter_vm_count_1 + dc.datacenter_vm_count_2 + dc.datacenter_vm_count_3) / 3)
        if dc.datacenter_vm_count_0 < average <= dc.datacenter_vm_count_1:
            capacities[dc] = (average - dc.datacenter_vm_count_0)
        elif dc.datacenter_vm_count_0 < dc.datacenter_vm_count_1 <= average:
            capacities[dc] = (dc.datacenter_vm_count_1 - dc.datacenter_vm_count_0)
        elif average <= dc.datacenter_vm_count_1 < dc.datacenter_vm_count_0:
            full[dc] = (dc.datacenter_vm_count_1 - dc.datacenter_vm_count_0)
        elif dc.datacenter_vm_count_1 <= average < dc.datacenter_vm_count_0:
            full[dc] = (average - dc.datacenter_vm_count_0)
        #dc.datacenter_vm_count_1 = -1
        dc.datacenter_vm_count_2 = -1
        dc.datacenter_vm_count_3 = -1

    # TODO remove
    # print(capacities)
    # print(full)

    for c in list(capacities.keys()):
        while capacities[c] > 0 and full:
            nearest = get_nearest_dc(c, full.keys())
            diff = capacities[c] + full[nearest]
            if diff == 0:
                shifts[(nearest, c)] = capacities[c]
                nearest.datacenter_vm_count_0 = nearest.datacenter_vm_count_0 - capacities[c]
                c.datacenter_vm_count_0 = c.datacenter_vm_count_0 + capacities[c]
                capacities[c] = 0
                del full[nearest]
            elif diff > 0:
                shifts[(nearest, c)] = full[nearest] * -1
                nearest.datacenter_vm_count_0 = nearest.datacenter_vm_count_0 - (full[nearest] * -1)
                c.datacenter_vm_count_0 = c.datacenter_vm_count_0 + (full[nearest] * -1)
                capacities[c] = diff
                del full[nearest]
            else:
                shifts[(nearest, c)] = capacities[c]
                nearest.datacenter_vm_count_0 = nearest.datacenter_vm_count_0 - capacities[c]
                c.datacenter_vm_count_0 = c.datacenter_vm_count_0 + capacities[c]
                capacities[c] = 0
                full[nearest] = diff
        del capacities[c]

    # TODO remove
    # print(capacities)
    # print(full)

    green_energy = percentage_green_energy(datacenters)

    print(green_energy)

    return (shifts, datacenters)


def get_nearest_dc(dc, neighbors):
    coords_1 = (dc.position.latitude, dc.position.longitude)

    nearest_dc = dc
    distance = -1
    for neighbor in neighbors:
        coords_2 = (neighbor.position.latitude, neighbor.position.longitude)
        if geopy.distance.distance(coords_1, coords_2).km < distance or distance == -1:
            distance = geopy.distance.distance(coords_1, coords_2).km
            nearest_dc = neighbor

    if nearest_dc == dc:
        raise ValueError('Nearest Datacenter cannot be the datacenter itself')
    return nearest_dc


def percentage_green_energy(datacenters):
    total = 0
    green = 0
    for dc in datacenters:
        total = total+dc.datacenter_vm_count_0
        if dc.datacenter_vm_count_0 <= dc.datacenter_vm_count_1:
            green = green+dc.datacenter_vm_count_0
        else:
            green = dc.datacenter_vm_count_1

    return (green/total)


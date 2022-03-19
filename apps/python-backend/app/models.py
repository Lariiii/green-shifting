class Position:
    def __init__(self, latitude: float, longitude: float):
        """
        represents a position on earth

        :param latitude: a latitude from -90 (south pole) to +90 (north pole)
        :param longitude: a longitude from -180 (west) to 0 (Greenwich) to +180 (east)
        """
        self.latitude = latitude
        self.longitude = longitude


class Datacenter:
    def __init__(self,
                 name: str,
                 company: str,
                 position: Position,
                 windpower_kwh: int,
                 solarpower_kwh: int,
                 datacenter_vm_count_0: int):

        self.name = name
        self.company = company
        self.position = position
        self.windpower_kwh = windpower_kwh
        self.solarpower_kwh = solarpower_kwh
        self.datacenter_vm_count_0 = datacenter_vm_count_0

        # Soll Werte in der Zukunft
        self.datacenter_vm_count_1 = 0
        self.datacenter_vm_count_2 = 0
        self.datacenter_vm_count_3 = 0

        # Wetter Daten 24h
        self.environment = None

    def __str__(self) -> str:
        return (f'DC: {self.name}:' if self.name is not None else '') + \
               (f' datacenter_vm_count_0={self.datacenter_vm_count_0} VMs' if self.datacenter_vm_count_0 is not None else '') + \
               (f' datacenter_vm_count_1={self.datacenter_vm_count_1} VMs' if self.datacenter_vm_count_0 is not None else '') + \
               (f' datacenter_vm_count_2={self.datacenter_vm_count_2} VMs' if self.datacenter_vm_count_0 is not None else '') + \
               (f' datacenter_vm_count_3={self.datacenter_vm_count_3} VMs' if self.datacenter_vm_count_0 is not None else '')


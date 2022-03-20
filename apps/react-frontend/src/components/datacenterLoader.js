import React from 'react';
import { io } from "socket.io-client";

export const DatacenterLoader = ({}) => {

    const socket = io("ws://127.0.0.1:5000", {
        transports: ["websocket"],
        withCredentials: true,
        path: "/socket.io"
    });

    console.log("Rendering Custom Socket IO 7!")

    socket.on("connect", () => {
        console.log("connect")
        var example_datacenter_1 = {"name": "DC 1",
                        "company": "vmware",
                        "longitude": 55.2321664,
                        "latitude": 9.5155424,
                        "windpower_kwh": 2000,
                        "solarpower_kwh": 2000,
                        "datacenter_vm_count_0": 2000}
        socket.emit("create_datacenters", example_datacenter_1);
    });

    return <div>
        YEP
    </div>

}
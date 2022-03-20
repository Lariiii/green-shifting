import React, {useState} from 'react';
import {io} from "socket.io-client";
import {useSelector, useDispatch,} from "react-redux";

export function DatacenterLoader() {
    let [hasConnected, setHasConnected] = useState(false)
    const dcs = useSelector(state => state.data.dataCenters)

    if (!hasConnected) {
        const dispatch = useDispatch()
        const socket = io("ws://127.0.0.1:5000", {
            transports: ["websocket"],
            withCredentials: true,
            path: "/socket.io"
        });

        console.log("Rendering Custom Socket IO 8!")
        setHasConnected(true)
        socket.on("connect", () => {
            console.log("connected")
            console.log(dcs)
            for (var i = 0; i < dcs.length; i++) {
                socket.emit("create_datacenters", dcs[i]);
            }

            // Start Data Stream
            socket.emit("begin_datastream")

            // Add Pew Pew
            socket.on("step_data", async (step_data) => {
                const shifts = step_data["shifts"]
                console.log(shifts)
                if (shifts.length > 0) {
                    dispatch({type: "DATACENTER_STEP", payload: {shifts}})
                }

            })
        });
    }

    return <div/>
}
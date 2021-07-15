#!/bin/bash

# Kill all subprocesses
function _exit() {
    JOBS=$(jobs -p)
    [[ -z "${JOBS}" ]] || kill ${JOBS}
    wait ${JOBS}
} 
trap _exit EXIT

PHC_NIC_MAP=()
for NIC in /sys/class/net/*; do
    NIC=$(basename ${NIC})
    PHC=$(ethtool -T ${NIC} | sed -n 's/PTP Hardware Clock: \(.*\)/\1/p')
    echo ${NIC} ${PHC}
    if [ "${PHC}" != "none" ]; then
        PHC_NIC_MAP[${PHC}]=${NIC}
    fi
done

for NIC in ${PHC_NIC_MAP[@]}; do
    ptp4l -m -i ${NIC} &
done

wait

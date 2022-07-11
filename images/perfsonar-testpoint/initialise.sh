#!/bin/bash

mkdir -p /var/run/pscheduler-server/{scheduler,ticker,archiver,runner}
chown pscheduler:pscheduler /var/run/pscheduler-server/{scheduler,ticker,archiver,runner}
sleep 10000

#!/bin/bash

export DIM_DNS_NODE="DNS address"
export DIM_HOST_NODE="Serwer address"


sudo chmod 777 /dev/ttyGS0

./build/server/server

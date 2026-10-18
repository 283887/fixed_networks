#!/bin/bash

cat $1 | grep -v -E "spawn ssh|password:|Welcome to ISAM|last login|Connection to" > $2
sed -i 's/\r//g;/./,$!d' $2

echo "Output saved to '$2'"

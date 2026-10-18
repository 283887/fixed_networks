#!/bin/bash

mapfile -d '' -t blocks < <(
awk '
/^typ:isadmin># / {
    if (block)
        printf "%s\0", block
    block = $0 "\n"
    next
}
{
    block = block $0 "\n"
}
END {
    if (block)
        printf "%s\0", block
}
' "$1"
)

#echo "Number of blocks: ${#blocks[@]}"

#1. info configure service
echo ""
echo "1. info configure service"
adr=$(awk '/address/ {print $2; exit}' <<< "${blocks[0]}")
adr="${adr%%/*}"

if [ "$adr" = "$2" ]; then
	echo "IPv4 address: OK ($adr)"
else
	echo "IPv4 address: Not OK ($adr)"
fi

# 2. info configure router
echo ""
echo "2. info configure router"
router_conf=$(awk -F' *' '/static-route/ {print $5}' <<< "${blocks[1]}")
#echo "static route $router_conf"

if [ "$router_conf" = "10.128.160.61" ]; then
	echo "Static route: OK ($router_conf)"
else
	echo "Static route: Not OK"
fi

# 3. show service id 4093 all
echo ""
echo "3. show service id 4093 all"
admin_state=$(awk -F' *' '/Admin State/ {print $4; exit}' <<< "${blocks[2]}")
service_type=$(awk -F' *' '/Service Type/ {print $4; exit}' <<< "${blocks[2]}")
vlan_id=$(awk -F': *' '/VlanId/ {print $2}' <<< "${blocks[2]}")

if [ "$admin_state" = "Up" ]; then
	echo "Admin State: OK ($admin_state)"
else
	echo "Admin State: Not OK ($admin_state)"
fi

if [ "$service_type" = "v-VPLS" ]; then
	echo "Service Type: OK ($service_type)"
else
	echo "Service Type: Not OK ($service_type)"
fi

if [ "$vlan_id" = "4093" ]; then
	echo "VLAN Id: OK ($vlan_id)"
else
	echo "VLAN Id: Not OK ($vlan_id)"
fi

# 4. show service sap-using
echo ""
echo "4. show service sap-using"
svc_id=$(awk -F' *' '/nt:vp:1:4093/ {print $2}' <<< "${blocks[3]}")
adm=$(awk -F' *' '/nt:vp:1:4093/ {print $5}' <<< "${blocks[3]}")
opr=$(awk -F' *' '/nt:vp:1:4093/ {print $6}' <<< "${blocks[3]}")

if [ "$svc_id" = "10000" ]; then
	echo "SvcId: OK ($svc_id)"
else
	echo "SvcId: Not OK ($svc_id)"
fi

if [ "$adm" = "Up" ]; then
	echo "Admin State: OK ($adm)"
else
	echo "Admin State: Not OK ($adm)"
fi

if [ "$opr" = "Up" ]; then
	echo "Operational Status: OK ($opr)"
else
	echo "Operational Status: Not OK ($opr)"
fi

# 5. show port nt-a:xfp:1
echo ""
echo "5. show port nt-a:xfp:1"
port_ad=$(awk -F' *' '/Admin State/ {print $4}' <<< "${blocks[4]}")
port_neg=$(awk -F' *' '/Auto-negotiate/ {print $3}' <<< "${blocks[4]}")

if [ "$port_ad" = "up" ]; then
	echo "Admin State: OK ($port_ad)"
else
	echo "Admin State: Not OK ($port_ad)"
fi

if [ "$port_neg" = "up" ]; then
	echo "Auto-negotiation: OK ($port_neg)"
else
	echo "Auto-negotiation: Not OK ($port_neg)"
fi

#!/bin/bash


run() {
    echo "Connecting to ISAM $1"
    ./turn_up.exp "$1" "$2" >/dev/null
    rc=$?

    if [ $rc -eq 88 ]; then
	echo "[ ERROR ] couldn't connect to $1"
	rm -f "$2" "$3"
	return 88
    fi
    
    echo "Formating output for $1"
    ./execute.sh "$2" "$3" >/dev/null

    echo "Analyzing data for $1"

    echo "Saving output"
    ./check.sh $3 $1 > "$4"

    echo "Cleaning up..."
    rm "$2" "$3"
}


input=""
i=0
ip_addresses=()
 
while true; do
	echo "ISAM config checker, press to:
	[1] ADD addresses to scan
	[2] START scan
	[3] EXIT"

	read -p "" input	
	if [ "$input" = "1" ]; then
		echo "Enter IPv4 address, type 'exit' to go back"
		while true; do
			read -p "" ip
			if [ "$ip" = "exit" ]; then
				break
			else
				if  [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
					ip_addresses+=("$ip")
				else
					echo "[ERROR] Invalid address format, try again or type 'exit' to go back"
				fi
			fi
		done

	elif [ "$input" = "2" ]; then
		if [ ${#ip_addresses[@]} -eq 0 ]; then
			echo "No targets to scan, exiting ..."
			break
		else
			for adr in "${ip_addresses[@]}"; do
				echo "Running scan for $adr"
				run "$adr"  "output_${adr}.txt"  "final_${adr}.txt" "data_${adr}.txt" &
			done
		wait
		fi

	elif [ "$input" = "3" ]; then
		break
	else
		continue
	fi
	
done


import re
import csv

with open("ONTs-before-dummy.txt", "r", encoding="utf-8") as plik:
    before = plik.read()

with open("ONTs-after-dummy.txt", "r", encoding="utf-8") as plik:
    after = plik.read()


alarms = {}
with open("alarms_after.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        if row["Source Name"].startswith("ONT:") :
            key = row["Source Name"] 

            ont_match = re.search(r"ONT(\d+)", key)
            pon_match = re.search(r"PON(\d+)", key)
            r = re.search(r"R(\d+)", key)
            s = re.search(r"S(\d+)", key)
            lt = re.search(r"LT(\d+)", key)
            ont_id = ont_match.group(1)
            pon_id = pon_match.group(1)
            r_id = r.group(1)
            s_id = s.group(1)
            lt_id = lt.group(1)

            key = r_id + "/" + s_id + "/" + lt_id + "/" + pon_id + "/" + ont_id

            if key not in alarms:
                alarms[key] = []
            alarms[key].append(row["TL1 Alarm Condition"])

#print(before)
#print(after)

before_elementy = re.split(r'(?=>#)', before)
after_elementy = re.split(r'(?=>#)', after)

#1. nowe ont
before_ont = []
for line in before_elementy[1].splitlines():
    line = line.strip()

    if line and line[0].isdigit():
        cols = line.split()
        ont = cols[1] 
        before_ont.append(ont)

#print(before_ont)

after_ont = []
for line in after_elementy[1].splitlines():
    line = line.strip()

    if line and line[0].isdigit():
        cols = line.split()
        ont = cols[1]
        after_ont.append(ont)

#print(len(after_ont))

new_ont = list(set(after_ont) - set(before_ont))

#2. ilość ont + status ranged-ind
before_stats = {}
for line in before_elementy[2].splitlines():
    line = line.strip()

    if line.startswith("1/") or line.startswith("x-pon"):
        cols = line.split()

        pon_idx = cols[0]
        ont_num = cols[1]
        ranged_ind = cols[4]

        klucz = pon_idx + "/" + ont_num
        key = (klucz)
        before_stats[key] = ranged_ind

#print(before_stats)

after_stats = {}
for line in after_elementy[2].splitlines():
    line = line.strip()

    if line.startswith("1/") or line.startswith("x-pon"):
        cols = line.split()

        pon_idx = cols[0]
        ont_num = cols[1]
        ranged_ind = cols[4]

        klucz = pon_idx + "/" + ont_num

        key = (klucz)
        after_stats[key] = ranged_ind

#3. ilośc ont + admin status + oper status [zmiana] + wartości olt-rx-sig-level nie zmieniły się o 2.0 +-
before_sum = {}
for line in before_elementy[3].splitlines():
    line = line.strip()

    if line.startswith("1/"):  # dane zaczynają się od pon-idx
        cols = line.split()

        ont = cols[1]
        admin_stat = cols[3]
        oper_stat = cols[4]
        level = cols[5]

        key = (ont)
        before_sum[key] = (admin_stat, oper_stat, level)

#print(before_sum)

after_sum = {}
for line in after_elementy[3].splitlines():
    line = line.strip()

    if line.startswith("1/"):  # dane zaczynają się od pon-idx
        cols = line.split()

        ont = cols[1]
        admin_stat = cols[3]
        oper_stat = cols[4]
        level = cols[5]

        key = (ont)
        after_sum[key] = (admin_stat, oper_stat, level)

#print(after_sum)

# nowe ont po etapach 
#1
if(len(new_ont)) == 0:
    print("Brak nowych ONT po SWAP")
else:
    print("Nowe ont po SWAP: ", new_ont)
#2
print("\nProvisioned\nIlość ONT przed:", len(before_stats), "\nIlość ONT po:", len(after_stats))
#3
print("\nActive\nIlość ONT przed:", len(before_sum), "\nIlość ONT po:", len(after_sum))


# zmienne do plików
out1 = ""
out2 = ""
out3 = ""

2. 
ranged = {} 
for key in after_stats:
    if key in before_stats:
        if before_stats[key] != after_stats[key]: 
            print(
                f"\n{key}: "
                f"{before_stats[key]} -> {after_stats[key]}", end=""
            )
            out1 += f"\n{key}: " f"{before_stats[key]} -> {after_stats[key]}"
            if before_sum[key][0] == after_sum[key][0] and before_sum[key][1] == after_sum[key][1]:
                print(", operational state has not changed", end = "")
                out1 += ", operational state has not changed"
            ranged[key] = (before_stats[key], after_stats[key])
            if key in alarms.keys():
                print(f", ALARM: {alarms[key]}", end="")
                out1 += f", ALARM: {alarms[key]}"
print("\n")


# 3. 
for key in after_sum:
    if key not in before_sum:
        continue

    # admin state
    if before_sum[key][0] != after_sum[key][0]:
        if before_sum[key][0] == "before":
            continue
        else:
            print(
                f"{key} admin status changed: "
                f"{before_sum[key][0]} -> {after_sum[key][0]}"
            )
            out2 += f"{key} admin status changed: " f"{before_sum[key][0]} -> {after_sum[key][0]}"

    # oper state
    if before_sum[key][1] != after_sum[key][1]:
            if before_sum[key][1] == "down":
                continue
            else:
                print(
                f"\n{key} oper status changed: "
                f"{before_sum[key][1]} -> {after_sum[key][1]}", end=""
            )
                out2 += f"\n{key} oper status changed: " f"{before_sum[key][1]} -> {after_sum[key][1]}"
                if key in ranged.keys():
                    print( f", {ranged[key][0]} -> {ranged[key][1]}", end="")
                    out2 += f", {ranged[key][0]} -> {ranged[key][1]}"
                if key in alarms.keys():
                    print(f", ALARM: {alarms[key]}", end="")
                    out2 += f", ALARM: {alarms[key]}"
            

print("\n")
for key in after_sum:
    if key not in before_sum:
        continue
# rx power
    if (
        before_sum[key][2] != "invalid"
        and after_sum[key][2] != "invalid"
    ):
        diff = round(abs(
            abs(float(before_sum[key][2]))
            - abs(float(after_sum[key][2]))
        ), 2)
        if diff > 2.0:
            if before_sum[key][2] > after_sum[key][2]:
                continue
            else:
                print(
                    f"{key} olt-rx-sig changed significantly: "
                    f"{before_sum[key][2]} -> {after_sum[key][2]} "
                    f"(diff={diff:.1f} dB)"
                )
                out3 += f"{key} olt-rx-sig changed significantly: " f"{before_sum[key][2]} -> {after_sum[key][2]} " f"(diff={diff:.1f} dB)"
                out3 += "\n"


with open("ONTs_Sig_Deg.txt", "w") as f:
    f.write(out3)
with open("ONTs_not_ranged_OK.txt", "w") as f:
    f.write(out1)
with open("ONTs_NOK.txt", "w") as f:
    f.write(out2)
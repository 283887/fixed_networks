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

before_elementy = re.split(r'(?=>#)', before)
after_elementy = re.split(r'(?=>#)', after)

def pierwsze (before_elementy, after_elementy):
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
    if(len(new_ont)) == 0:
        print("Brak nowych ONT po SWAP")
    else:
        print("Nowe ont po SWAP: ", new_ont)

def drugie(before_elementy, after_elementy):
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

    print("\nProvisioned\nPrzed:", len(before_stats), "\nPo:", len(after_stats))

def trzecie(before_elementy, after_elementy):
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

    print("\nActive ONT\nPrzed:", len(before_sum), "\nPo:", len(after_sum))


pierwsze(before_elementy=before_elementy, after_elementy=after_elementy)
drugie(before_elementy=before_elementy, after_elementy=after_elementy)
trzecie(before_elementy=before_elementy, after_elementy=after_elementy)
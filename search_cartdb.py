import os
import re
import json
import csv

# -----------------------------------------
# Dat Parser
# -----------------------------------------
def parse_dat(path):
    games = []
    current_game = None
    current_rom = None
    stack = []

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            # Start game
            if line.startswith("game"):
                current_game = {"name": "", "region": "", "roms": []}
                games.append(current_game)
                stack.append("game")
                continue

            # End of a block
            if line == ")":
                if stack:
                    stack.pop()
                continue

            if current_game:

                # name "XXX"
                if line.startswith("name "):
                    m = re.match(r'name\s+"(.*)"', line)
                    if m:
                        current_game["name"] = m.group(1)
                    continue

                # region "XXX"
                if line.startswith("region "):
                    m = re.match(r'region\s+"(.*)"', line)
                    if m:
                        current_game["region"] = m.group(1)
                    continue

                # rom (...)
                if line.startswith("rom"):
                    rom = {"name": "", "size": 0, "crc": "", "md5": "", "sha1": ""}
                    # rom ( name "..." size xxxx crc XXXXX md5 XXXXX sha1 XXXXX )
                    items = re.findall(r'(\w+)\s+"?([^"\s)]+)"?', line)
                    for key, val in items:
                        if key == "name":
                            rom["name"] = val
                        elif key == "size":
                            rom["size"] = int(val)
                        elif key == "crc":
                            rom["crc"] = val
                        elif key == "md5":
                            rom["md5"] = val
                        elif key == "sha1":
                            rom["sha1"] = val
                    current_game["roms"].append(rom)
                    continue

    return games


# -----------------------------------------
# Search Filtering
# -----------------------------------------
def match_alignment(size):
    return (size % 1024) == 0


def apply_search_filter(games, field, value):
    filtered = []

    for g in games:
        rom_hits = []

        for r in g["roms"]:
            if field == "name" and value.lower() in g["name"].lower():
                rom_hits.append(r)

            elif field == "region" and value.lower() in g["region"].lower():
                rom_hits.append(r)

            elif field == "md5" and r["md5"].lower() == value.lower():
                rom_hits.append(r)

            elif field == "sha1" and r["sha1"].lower() == value.lower():
                rom_hits.append(r)

            elif field == "crc" and r["crc"].lower() == value.lower():
                rom_hits.append(r)

            elif field == "align1024" and match_alignment(r["size"]):
                rom_hits.append(r)

        if rom_hits:
            new_g = {
                "name": g["name"],
                "region": g["region"],
                "roms": rom_hits
            }
            filtered.append(new_g)

    return filtered


# -----------------------------------------
# Display
# -----------------------------------------
def display_games(games):
    if not games:
        print("No entries.")
        return

    for g in games:
        print(f"[{g['name']}]  region={g['region']}")
        for r in g["roms"]:
            print(f"  ROM: {r['name']}")
            print(f"    size = {r['size']}  (align1024={match_alignment(r['size'])})")
            print(f"    crc  = {r['crc']}")
            print(f"    md5  = {r['md5']}")
            print(f"    sha1 = {r['sha1']}")
        print("-" * 40)


# -----------------------------------------
# Export
# -----------------------------------------
def export_json(path, games):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(games, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON: {path}")


def export_csv(path, games):
    rows = []
    for g in games:
        for r in g["roms"]:
            rows.append({
                "name": g["name"],
                "region": g["region"],
                "rom_name": r["name"],
                "size": r["size"],
                "crc": r["crc"],
                "md5": r["md5"],
                "sha1": r["sha1"],
                "align1024": match_alignment(r["size"])
            })

    if not rows:
        print("No data.")
        return

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved CSV: {path}")


# -----------------------------------------
# Main Loop
# -----------------------------------------
def main():
    # list DAT files in current dir
    dat_files = [f for f in os.listdir(".") if f.lower().endswith(".dat")]
    if not dat_files:
        print("No DAT files found.")
        return

    print("Select DAT file:")
    for i, f in enumerate(dat_files):
        print(f"[{i}] {f}")

    sel = input("番号を入力: ").strip()
    if not sel.isdigit() or int(sel) not in range(len(dat_files)):
        print("Invalid selection.")
        return

    dat_path = dat_files[int(sel)]
    print("Loading:", dat_path)
    all_games = parse_dat(dat_path)
    current_games = all_games[:]  # filtered view

    print(f"Loaded {len(all_games)} game entries")

    conditions = []  # keep filter history

    help_text = """
Commands:
  search - add filter
  display - show current list
  clear - reset filters
  export - export current list (json/csv)
  cond - show conditions
  help
  quit
"""

    print(help_text)

    while True:
        cmd = input("> ").strip().lower()

        if cmd == "quit":
            break

        elif cmd == "help":
            print(help_text)

        elif cmd == "display":
            display_games(current_games)

        elif cmd == "clear":
            current_games = all_games[:]
            conditions.clear()
            print("Filters cleared. Total:", len(current_games))

        elif cmd == "cond":
            if not conditions:
                print("No conditions.")
            else:
                for c in conditions:
                    print(f"- {c}")
            print("Current count:", len(current_games))

        elif cmd == "search":
            print("Select field:")
            print(" 1: name")
            print(" 2: region")
            print(" 3: md5")
            print(" 4: sha1")
            print(" 5: crc")
            print(" 6: align1024 (size%1024==0)")

            fsel = input("番号: ").strip()
            field_map = {
                "1": "name",
                "2": "region",
                "3": "md5",
                "4": "sha1",
                "5": "crc",
                "6": "align1024"
            }

            if fsel not in field_map:
                print("Invalid field.")
                continue

            field = field_map[fsel]

            if field == "align1024":
                value = "true"
                cond_text = f"align1024"
            else:
                value = input("search value: ").strip()
                cond_text = f"{field} contains {value}"

            current_games = apply_search_filter(current_games, field, value)
            conditions.append(cond_text)

            print(f"Filtered: {len(current_games)} matched")
            print("Conditions:")
            for c in conditions:
                print(" -", c)

        elif cmd == "export":
            fmt = input("json or csv?: ").strip().lower()
            if fmt == "json":
                export_json("export.json", current_games)
            elif fmt == "csv":
                export_csv("export.csv", current_games)
            else:
                print("Invalid format.")

        else:
            print("Unknown command")



if __name__ == "__main__":
    main()

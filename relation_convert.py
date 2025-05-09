import json


def raw_to_middle():
    with open("rel-data/relation.json", "r", encoding="utf-8") as f:
        raw = json.load(f)
    with open("rel-data/syscall_name.json", "r", encoding="utf-8") as f:
        syscall_name = json.load(f)
    name_map = {}
    for syscall in syscall_name:
        name_map[int(syscall["ID"])] = syscall["name"]
    middle_relation = []
    for i in range(len(raw)):
        for j in range(len(raw[i])):
            if raw[i][j] == 1:
                middle_relation.append([
                    name_map[i],
                    name_map[j],
                ])
    with open("rel-data/middle_relation.json", "w", encoding="utf-8") as f:
        json.dump(middle_relation, f, indent=4, ensure_ascii=False)


def middle_to_raw():
    with open("rel-data/middle_relation.json", "r", encoding="utf-8") as f:
        middle_relation = json.load(f)
    with open("rel-data/syscall_name.json", "r", encoding="utf-8") as f:
        syscall_name = json.load(f)
    name_map = {}
    for syscall in syscall_name:
        name_map[syscall["name"]] = int(syscall["ID"])
    raw_relation = [[0] * len(syscall_name) for _ in range(len(syscall_name))]
    for i in range(len(middle_relation)):
        raw_relation[name_map[middle_relation[i][0]]][name_map[middle_relation[i][1]]] = 1
    with open("rel-data/relation2.json", "w", encoding="utf-8") as f:
        json.dump(raw_relation, f, ensure_ascii=False)


def main():
    middle_to_raw()


if __name__ == '__main__':
    main()

from pathlib import Path
import re


# 获取一个目录下二级目录下所有的 txt，并按照二级目录分类
def get_files(path):
    path = Path(path)
    files = {}
    for p in path.iterdir():
        if p.is_dir():
            for f in p.iterdir():
                if f.suffix == '.txt':
                    if p.name not in files:
                        files[p.name] = []
                    files[p.name].append(f)
    return files


def parse_syzlang(files):
    lines = []
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            lines += file.readlines()
    resource_lines = []
    for line in lines:
        if line.startswith("resource"):
            resource_lines.append(line)

    r_map = {}

    ban_list = ["int32", "intptr","int64", "int16", "int8", "uint32", "uint64", "uint16", "uint8"]

    for r_line in resource_lines:
        r = re.compile(r"resource\s+(\w+)\s*\[(\w+)].*")
        match = r.match(r_line)
        if match:
            name = match.group(1)
            parent = match.group(2)
            if name in ban_list:
                continue
            if name not in r_map:
                r_map[name] = {
                    "name": name,
                    "parent": None,
                    "gen_by": [],
                    "used_by": [],
                    "all_parent": [],
                }
            if parent in ban_list:
                continue
            if parent not in r_map:
                r_map[parent] = {
                    "name": parent,
                    "parent": None,
                    "gen_by": [],
                    "used_by": [],
                    "all_parent": [],
                }
            r_map[name]["parent"]= parent
        else:
            print("No match found")



    for k, v in r_map.items():
        cur_parent = v["parent"]
        while cur_parent is not None:
            v["all_parent"].append(cur_parent)
            if cur_parent in r_map:
                cur_parent = r_map[cur_parent]["parent"]
            else:
                break


    syscall_lines = []
    for line in lines:
        if line.startswith("#"):
            continue
        if "(" in line:
            syscall_lines.append(line)
    for line in syscall_lines:
        s1 = line.split(")")[0]
        s2 = line.split(")")[1]
        s_name = s1.split("(")[0]
        for r_name in r_map.keys():
            if r_name in s2:
                r_map[r_name]["gen_by"].append(s_name)
            if "out, "+ r_name in s1:
                r_map[r_name]["gen_by"].append(s_name)
            if "in, "+ r_name in s1:
                r_map[r_name]["used_by"].append(s_name)

    depend_map = {}

    for k, v in r_map.items():
        for call in v["gen_by"]:
            if call not in depend_map:
                depend_map[call] = {
                    "name": call,
                    "follow": set(),
                    "indirect_follow": set(),
                }
        for call in v["used_by"]:
            if call not in depend_map:
                depend_map[call] = {
                    "name": call,
                    "follow": set(),
                    "indirect_follow": set(),
                }
        for c1 in v["gen_by"]:
            for c2 in v["used_by"]:
                depend_map[c1]["follow"].add(c2)
                depend_map[c1]["indirect_follow"].add(c2)
        for c1 in v["gen_by"]:
            for p in v["all_parent"]:
                for c2 in r_map[p]["gen_by"]:
                    depend_map[c1]["indirect_follow"].add(c2)

    follow_count = 0
    indirect_follow = 0
    extend_call_list = []
    call_list = []

    for k, v in depend_map.items():
        follow_count += len(v["follow"])
        indirect_follow += len(v["indirect_follow"])
        if len(v["indirect_follow"]) > 0:
            extend_call_list.append(k)
            extend_call_list.extend(v["indirect_follow"])
        if len(v["follow"]) > 0:
            call_list.append(k)
            call_list.extend(v["follow"])
    print(f"follow_count: {follow_count}")
    print(f"indirect_follow: {indirect_follow}")
    print(f"total call num: {len(syscall_lines)}")
    print(f"extend depend call num: {len(set(extend_call_list))}")
    print(f"depend call num: {len(set(call_list))}")


def main():
    ps = get_files("sys")
    for k, v in ps.items():
        print(k)
        parse_syzlang(v)


if __name__ == '__main__':
    main()

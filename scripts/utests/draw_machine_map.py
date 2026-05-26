import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

MAP_FILE = r"C:\Users\technician\.gemini\antigravity\brain\221ed255-22b9-4c08-88a2-5f870ade149f\artifacts\plc_true_map.json"
OUTPUT_FILE = r"C:\Users\technician\.gemini\antigravity\brain\221ed255-22b9-4c08-88a2-5f870ade149f\artifacts\System_Architecture_Map.md"


def build_tree(flat_map, current_node):
    if current_node not in flat_map:
        return {"name": current_node, "type": "Unknown", "children": []}

    node_data = flat_map[current_node]
    if isinstance(node_data, str):
        return {"name": current_node, "type": "Primitive", "status": node_data}

    tree = {
        "name": current_node,
        "type": node_data.get("type", ""),
        "subsystem": node_data.get("subsystem", ""),
        "children": [],
    }

    for child in node_data.get("children", []):
        child_id = child.get("identity")
        child_status = child.get("status", "")
        child_type = child.get("type", "")
        child_sub = child.get("subsystem", "")

        if child_status == "[LEAF]":
            tree["children"].append(
                {
                    "name": child_id,
                    "type": child_type,
                    "subsystem": child_sub,
                    "status": "[LEAF]",
                }
            )
        else:
            # Expand recursively
            tree["children"].append(build_tree(flat_map, child_id))

    return tree


def count_nodes(tree):
    total = 1
    leaves = 0
    expandable = 0

    if "children" in tree:
        for c in tree["children"]:
            if c.get("status") == "[LEAF]":
                leaves += 1
                total += 1
            else:
                sub_t, sub_l, sub_e = count_nodes(c)
                total += sub_t
                leaves += sub_l
                expandable += sub_e + 1
    else:
        leaves = 1

    return total, leaves, expandable


def get_node_short_name(full_name):
    return full_name.split(".")[-1].split("/")[-1]


def generate_markdown_hierarchy(tree, depth=0):
    lines = []
    indent = "  " * depth
    short_name = get_node_short_name(tree["name"])

    if tree.get("status") == "[LEAF]":
        lines.append(f"{indent}- **{short_name}** (`{tree.get('type', '')}`) 🍃")
    else:
        subsys_info = (
            f" [Subsystem: {tree['subsystem']}]" if tree.get("subsystem") else ""
        )
        lines.append(
            f"{indent}- 📂 **{short_name}** (`{tree.get('type', '')}`){subsys_info}"
        )
        for c in tree.get("children", []):
            lines.extend(generate_markdown_hierarchy(c, depth + 1))

    return lines


def generate_mermaid_highlevel(tree):
    lines = [
        "graph TD",
        "    %% Style Definitions",
        "    classDef subsystem fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#f8fafc;",
        "    classDef leaf fill:#0f172a,stroke:#10b981,stroke-width:1px,color:#34d399;",
    ]

    # Let's extract top level subsystems under System
    if "children" in tree:
        for c in tree["children"]:
            c_short = get_node_short_name(c["name"])
            lines.append(f"    System --> {c_short}[📂 {c_short}]")
            lines.append(f"    class {c_short} subsystem;")

            # Show one level down if they have children
            if "children" in c:
                for gc in c["children"]:
                    gc_short = get_node_short_name(gc["name"])
                    if gc.get("status") != "[LEAF]" and len(gc.get("children", [])) > 0:
                        lines.append(
                            f"    {c_short} --> {c_short}_{gc_short}[📂 {gc_short}]"
                        )
                        lines.append(f"    class {c_short}_{gc_short} subsystem;")

    return "\n".join(lines)


def generate_mermaid_subsystem(tree, subsystem_name):
    # Find the subsystem node
    sub_node = None
    if "children" in tree:
        for c in tree["children"]:
            if get_node_short_name(c["name"]) == subsystem_name:
                sub_node = c
                break

    if not sub_node:
        return "%% Subsystem not found"

    lines = [
        f"graph TD",
        f"    %% Subsystem: {subsystem_name}",
        "    classDef folder fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#f8fafc;",
        "    classDef variable fill:#0f172a,stroke:#10b981,stroke-width:1px,color:#e2e8f0;",
    ]

    def traverse_sub(node, parent_id):
        node_short = get_node_short_name(node["name"])
        curr_id = parent_id + "_" + node_short

        if node.get("status") == "[LEAF]":
            lines.append(
                f"    {parent_id} --> {curr_id}[\"🍃 {node_short} ({node.get('type')})\"]"
            )
            lines.append(f"    class {curr_id} variable;")
        else:
            lines.append(
                f"    {parent_id} --> {curr_id}[\"📂 {node_short} ({node.get('type')})\"]"
            )
            lines.append(f"    class {curr_id} folder;")
            for c in node.get("children", []):
                traverse_sub(c, curr_id)

    traverse_sub(sub_node, subsystem_name)
    return "\n".join(lines)


def main():
    if not os.path.exists(MAP_FILE):
        print(f"[-] Không tìm thấy file bản đồ phẳng: {MAP_FILE}")
        sys.exit(1)

    with open(MAP_FILE, "r", encoding="utf-8") as f:
        flat_map = json.load(f)

    print(f"[+] Đang xây dựng cây phân cấp từ {len(flat_map)} node...")

    # We start traversal from the top node in our BFS, which is 'System' (or 'PrimaryPLC.System')
    # Let's find the root key
    root_key = "System"
    for k in flat_map.keys():
        if k.endswith(".System") or k == "System":
            root_key = k
            break

    tree = build_tree(flat_map, root_key)

    total, leaves, expandable = count_nodes(tree)
    print(
        f"[+] Thống kê: Tổng số node = {total}, Lá (Leaf) = {leaves}, Nhánh (Expandable) = {expandable}"
    )

    markdown_lines = generate_markdown_hierarchy(tree)

    # Generate sub-system Mermaid blocks
    subsystems_found = []
    if "children" in tree:
        for c in tree["children"]:
            subsystems_found.append(get_node_short_name(c["name"]))

    mermaid_blocks = {}
    for s in subsystems_found:
        mermaid_blocks[s] = generate_mermaid_subsystem(tree, s)

    # Write the premium markdown file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"""# Bản Đồ Kiến Trúc Hệ Thống PLC (System Architecture Map)

Bản tài liệu này mô tả chi tiết toàn bộ kiến trúc phân cấp vật lý và logic của các biến điều khiển trên PLC (`PrimaryPLC.System`), được tự động giải mã thông qua tiến trình quét BFS sâu và phân tích kiểu dữ liệu thời gian thực.

> [!NOTE]
> Bản đồ hệ thống được xây dựng bằng cách đi qua tất cả các subsystem từ cổng Read-Only (`49880`), nhận diện kiểu lá nguyên thủy (`ValRef`, `ValObj`) để ngăn chặn việc quét lặp thừa vô ích.

## 📊 Thống kê Hệ thống PLC

- **Tổng số biến điều khiển:** `{total}`
- **Số lượng biến lá thực thi (Active Leaves):** `{leaves}`
- **Số lượng nhóm/subsystem phân cấp (Expandable Folders):** `{expandable}`

---

## 🗺️ Sơ đồ Kiến trúc Tổng thể (High-Level Architecture)

Dưới đây là sơ đồ tổng quan về các subsystem chính kết nối trực tiếp với nhân điều khiển hệ thống (`System`):

```mermaid
{generate_mermaid_highlevel(tree)}
```

---

## 🧩 Sơ đồ Chi tiết của các Subsystem Chính

""")

        # Write BMS, TMS, Spreader, Travel, Steer detail mermaid diagrams
        major_subsystems = ["BMSAB", "TMS", "Spreader", "Travel", "Steer", "ChargerABC"]
        for s in major_subsystems:
            if s in mermaid_blocks:
                f.write(f"""### Subsystem `{s}`

```mermaid
{mermaid_blocks[s]}
```

""")

        f.write(f"""---

## 🌳 Cấu trúc Phân cấp Chi tiết (Hierarchical Tree View)

🍃 đại diện cho biến lá nguyên thủy (có giá trị đọc/ghi trực tiếp).  
📂 đại diện cho thư mục logic (chứa các biến con).

```markdown
{"\n".join(markdown_lines)}
```
""")

    print(f"[+] ĐÃ TẠO THÀNH CÔNG BẢN ĐỒ KIẾN TRÚC MÁY TẠI: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

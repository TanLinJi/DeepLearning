import os
import json
import re

base_dir = "/root/autodl-tmp/DeepLearning/d2l-zh/pytorch"

for d in sorted(os.listdir(base_dir)):
    dir_path = os.path.join(base_dir, d)
    if os.path.isdir(dir_path) and d.startswith("chapter_"):
        # 寻找对应的 index 文件
        index_file = None
        for p in ["00_index.ipynb", "index.ipynb"]:
            if os.path.exists(os.path.join(dir_path, p)):
                index_file = p
                break
        
        if not index_file:
            continue
            
        index_path = os.path.join(dir_path, index_file)
        
        with open(index_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except:
                continue
        
        # 解析按顺序排序的文件列表
        links = []
        for cell in data.get('cells', []):
            if cell.get('cell_type') == 'markdown':
                lines = cell.get('source', [])
                for line in lines:
                    # 匹配 markdown 里面的 (xxx.ipynb)
                    m = re.search(r'\((.*?)\.ipynb\)', line)
                    if m:
                        link = m.group(1).split('/')[-1] # 防御性提取文件名
                        # 排除不属于当前正文的文件
                        if link not in ("index", "00_index", "zreferences"):
                            links.append(link)
        
        # 重命名过程
        if index_file == "index.ipynb":
            new_index_path = os.path.join(dir_path, "00_index.ipynb")
            os.rename(index_path, new_index_path)
            print(f"Renamed: index.ipynb -> 00_index.ipynb in {d}")
            index_path = new_index_path
            
        current_files = os.listdir(dir_path)
        
        # 为了保证不重复重命名，去除当前可能存在的前缀来匹配
        for i, link in enumerate(links, start=1):
            target_prefix = f"{i:02d}_"
            target_base = f"{link}.ipynb"
            target_name = f"{target_prefix}{target_base}"
            
            if target_name in current_files:
                continue
                
            # 找找当前目录下哪个文件名字末尾是这个 target_base
            found = False
            for cf in current_files:
                # 把原有的前缀（如果有的话）去掉进行比对
                if cf == target_base or (re.match(r'^\d{2}_', cf) and cf[3:] == target_base):
                    old_path = os.path.join(dir_path, cf)
                    new_path = os.path.join(dir_path, target_name)
                    if old_path != new_path:
                        os.rename(old_path, new_path)
                        print(f"Renamed: {cf} -> {target_name} in {d}")
                    found = True
                    break
            
            if not found:
                print(f"Warning: Not found file ending in {target_base} in {d}")
                
print("Done!")

import re
msg = "['col_missing'] not in index"
match = re.search(r"['\"]([^'\"]+)['\"]", msg)
if match:
    print(f"Match: {match.group(1)}")
else:
    print("No match")

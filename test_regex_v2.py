import re
msg = "could not convert string to float: 'N/A': Error while type casting for column 'col_numeric'"
pattern = r"column ['\"]([^'\"]+)['\"]"
match = re.search(pattern, msg, re.IGNORECASE)
if match:
    print(f"Match: {match.group(1)}")
else:
    print("No match")

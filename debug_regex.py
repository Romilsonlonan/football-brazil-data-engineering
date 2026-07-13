import re

def _handle_type_error(error_msg, df_columns):
    column_match = re.search(r"column\s+['\"]([^'\"]+)['\"]", error_msg, re.IGNORECASE)
    print(f"Column Match: {column_match}")
    if column_match:
        print(f"Group 1: {column_match.group(1)}")
    
    value_match = re.search(r"['\"]([^'\"]+)['\"]", error_msg)
    print(f"Value Match: {value_match}")
    if value_match:
        print(f"Group 1: {value_match.group(1)}")

error_msg = "could not convert string to float: 'N/A': Error while type casting for column 'col_numeric'"
df_cols = ["col_numeric"]

_handle_type_error(error_msg, df_cols)

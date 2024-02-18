import re
def extract_session_id(output_contexts):
    session_str = output_contexts[0]["name"]
    pattern = r'(?<=sessions\/)[\w-]+'
    match = re.search(pattern, session_str)
    if match:
        extracted_value = match.group(0)
        return extracted_value
    else:
        return "No match found."

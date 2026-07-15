import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

content_path = Path("C:/Users/WJLEE/.gemini/antigravity-cli/brain/00a2dabb-fabc-4b25-b7eb-bc3381c8f490/.system_generated/steps/148/content.md")
lines = content_path.read_text(encoding="utf-8").splitlines()

# Print line 3 in chunks
line = lines[2] # 0-indexed
print("Length of line 3:", len(line))

# Print first 2000 chars and search for some keywords
import re
print("First 2000 chars:")
print(line[:2000])

# Split by tables or formatting markers if any, or just print formatted
# It looks like the HTML text is concatenated. Let's see if we can find the tables
# Replace multiple spaces/newlines
text = re.sub(r'\s+', ' ', line)
# Let's print out text around some markers
print("\n--- Formatted ---")
pos = 0
while pos < len(text):
    print(text[pos:pos+120])
    pos += 120

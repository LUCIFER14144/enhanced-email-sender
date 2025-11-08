"""
Raw distributable Python script version of the Enhanced Email Sender.
This file is a direct copy of the original `pefectedwithinline image.py` for download.

Usage (Windows PowerShell):
  python Enhanced-Email-Sender.py

Note: For full functionality, install dependencies from requirements.txt.
"""

import os
import sys

def _copy_original_into_stdout():
	# Locate the original script at repo root
	project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
	original_path = os.path.join(project_root, "pefectedwithinline image.py")
	try:
		with open(original_path, 'r', encoding='utf-8') as f:
			return f.read()
	except Exception as e:
		return None

def main():
	# If executed directly, chain-exec the original script content
	src = _copy_original_into_stdout()
	if src is None:
		print("Error: Could not load original script.")
		sys.exit(1)
	code = compile(src, "Enhanced-Email-Sender.py", "exec")
	globals_dict = {"__name__": "__main__"}
	exec(code, globals_dict, globals_dict)

if __name__ == "__main__":
	main()


import subprocess

def get_diff():
    # Run git diff for all modified files
    result = subprocess.run(["git", "diff"], capture_output=True, text=True, encoding="utf-8")
    with open("e:\\The_Council_v2\\full_diff.txt", "w", encoding="utf-8") as f:
        f.write(result.stdout)
    
    # Run git status
    result_status = subprocess.run(["git", "status"], capture_output=True, text=True, encoding="utf-8")
    with open("e:\\The_Council_v2\\full_status.txt", "w", encoding="utf-8") as f:
        f.write(result_status.stdout)

if __name__ == "__main__":
    get_diff()

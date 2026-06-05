import subprocess
result = subprocess.run(["uv", "run", "pytest", "backend/tests/test_api_e2e_true.py"], capture_output=True, text=True)
with open("real_output.txt", "w", encoding="utf-8") as f:
    f.write(result.stdout)
    f.write("\n\n--- STDERR ---\n\n")
    f.write(result.stderr)

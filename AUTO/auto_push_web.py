import subprocess

def push_web():
    try:
        subprocess.run(["python", "TOOLS/export_web_data.py"], check=True)
        subprocess.run(["git", "-C", "web", "add", "."], check=True)
        subprocess.run(["git", "-C", "web", "commit", "-m", "🔄 Auto push web"], check=True)
        subprocess.run(["git", "-C", "web", "push", "origin", "main"], check=True)
    except Exception as e:
        print(f"Erreur push web : {e}")

if __name__ == "__main__":
    push_web()

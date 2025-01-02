import os
import subprocess

def install_requirements():
    requirements_file = "../requirements.txt"

    if not os.path.exists(requirements_file):
        print(f"Súbor {requirements_file} neexistuje. Vygenerujte ho príkazom: pip freeze > requirements.txt")
        return

    print(f"Inštalujem balíky zo súboru {requirements_file}...")
    subprocess.check_call(["pip", "install", "-r", requirements_file])

if __name__ == "__main__":
    install_requirements()
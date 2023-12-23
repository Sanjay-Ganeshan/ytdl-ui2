import subprocess
import sys

def upgrade_downloader() -> None:
    """
    Upgrades the downloader we use automatically by calling pip.
    """

    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])

def upgrade_self() -> None:
    """
    Upgrades self, by git pulling
    """
    subprocess.run(["git", "pull"])

def main() -> None:
    upgrade_downloader()
    upgrade_self()
    

if __name__ == "__main__":
    main()
import subprocess
import sys


def main():
    print("Running tests with pytest...", flush=True)
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pytest", "-q"]
        )  # exit code assertion
        print("All tests passed.")
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with exit code {e.returncode}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()

import singleton
from utilities.api import API
import sys

app = API().app
# Usage
if __name__ == "__main__":
    s = singleton.Singleton()
    if len(sys.argv) < 2:
        print("Usage: python main.py <route>")
    else:
        route = sys.argv[1]
        if route == 'update_caches':
            s.Crons.update_caches()
            print("Cache Update executed")
        else:
            print(f"Unknown route: {route}")

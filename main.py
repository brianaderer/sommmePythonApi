import singleton
from utilities.api import API

app = API().app
# Usage
if __name__ == "__main__":
    s = singleton.Singleton()
    api = s.api.API()
    s.Parser.load("./wineAndLiquor.pdf")

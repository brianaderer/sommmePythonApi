import singleton

# Usage
if __name__ == "__main__":
    s = singleton.Singleton()
    s.Parser.load("./roseCloseouts.pdf")

import singleton

# Usage
if __name__ == "__main__":
    s = singleton.Singleton()
    s.Parser.load("./echelon.pdf")
    # s.Parser2.load("./roseCloseouts.pdf")
    # print(s.Foo.do_something())  # Accessing Foo through the singleton instance
    # print(s.Bar.do_something_else())  # Accessing Bar through the singleton instance

    # Ensuring that the instances are indeed singleton
    # t = Singleton()
    # print(s == t)  # True, s and t are the same instance
    # print(s.Foo == t.Foo)  # True, s.Foo and t.Foo are the same instance
    # print(s.Bar == t.Bar)  # True, s.Bar and t.Bar are the same instance

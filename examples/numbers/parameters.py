parameters = [
    ["-add 1 2".split(), "3"],
    ["-sub 1 2".split(), "-1"],
    ["-add 1 -sub 10 2".split(), "9"],
    ["-add -add 1 -sub 10 2 100".split(), "109"],
    ["-sum 1 2 3 4 5".split(), "15"],
    ["-sub 100 -sum 1 2 3 4 5".split(), "85"],
]

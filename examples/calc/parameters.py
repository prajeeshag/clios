# type: ignore
parameters = [
    [["-print", "-add", "1", "2"], 3.0],
    [["-print", "-sub", "1", "2"], -1.0],
    [["-print", "-add", "1", "-sub", "10", "2"], 9.0],
    [["-print", "-add", "-add", "1", "-sub", "10", "2", "100"], 109.0],
]

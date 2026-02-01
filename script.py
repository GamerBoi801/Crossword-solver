import pandas as pd


'''data = dict()
with open('global.txt', 'r') as file:
    for line in file:
        length = len(line.strip())
        data[line.strip()] = length

with open('lengths.csv', 'w') as file:
    for key, value in data.items():
        file.write(f"{key},{value}\n")
'''


data = pd.read_csv('lengths.csv')
data
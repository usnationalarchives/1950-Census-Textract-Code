import csv 

with open('debug/descriptions/Illinois/Illinois-0111/Illinois-0111_0039.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(row['Locale'])
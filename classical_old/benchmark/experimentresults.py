import json

# Load the data from the JSON file
with open('classical/benchmark/experiments/firstRunningLogs95notypes.json') as f:
    data = json.load(f)

# Filter out failing examples
data = [entry for entry in data if entry['Error'] == 0]

# Calculate the sum of all branch coverage percentages
total_coverage = sum(entry['BranchCoveragePercentage'] for entry in data)

# Calculate the average branch coverage
average_coverage = total_coverage / len(data)

# Calculate the sum of all time taken
total_time = sum(entry['TimeConsumed'] for entry in data)

# Calculate the average time taken
average_time = total_time / len(data)

print(f'Average Time Taken: {average_time}')
print(f'Average Branch Coverage: {average_coverage}%')
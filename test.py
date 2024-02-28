import json
import random

with open("database/slot.json", 'r', encoding='utf-8') as file:
    slot_json = json.load(file)

result_count = {}

for _ in range(1000):
    result = random.choices(
        population=slot_json["population"],
        weights=slot_json["weights"],
        k=1
    )[0]

    if result in result_count:
        result_count[result] += 1
    else:
        result_count[result] = 1

print(result_count)

import json
with open('manual-transcript.json', 'r') as file:
    json_data = json.load(file)

# text = ""   
# for item in json_data[:1]:
#     # Process each item (which is a dictionary)
#     for key, value in item.items():
#         q = item.qu
#         # text = f"Q: {q} A: {a}"
#         print(f'{key}: {value}')

for item in json_data[:1]:
    q = item["question"]
    a = item["answer"]
    s = item["source"]
    text = f"Q: {q} A: {a} S: {s}"
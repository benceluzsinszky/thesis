import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np


endpoints = {}
# reading the JSON data using json.load()
file = "./resources/fmd_data.json"
with open(file) as train_file:
    data = json.load(train_file)


for i in data:
    endpoints[i["name"]] = {"hits": i["hits-overall"], "latency": i["median-overall"]}


df = pd.DataFrame.from_dict(endpoints, orient="index")
df["vector_length"] = np.sqrt(df["hits"] ** 2 + df["latency"] ** 2)

df["hits_normalized"] = df["hits"] / df["hits"].max()
df["latency_normalized"] = df["latency"] / df["latency"].max()
df["normalized_length"] = np.sqrt(
    df["hits_normalized"] ** 2 + df["latency_normalized"] ** 2
)

df.sort_values(by=["vector_length"], inplace=True, ascending=False)
print(df)

# Plotting the data
plt.figure(figsize=(10, 6))
plt.scatter(
    df["latency"], df["hits"], color="blue", s=10
)  # s=10 makes the dots smaller
# plt.xscale("log")  # Set x-axis to logarithmic scale
# plt.yscale("log")  # Set y-axis to logarithmic scale
plt.xlabel("Latency")
plt.ylabel("Hits")
plt.title("Hits vs Latency")
plt.grid(True)
plt.axvline(x=2000, color="red", linestyle="--")

plt.show()


# df["timestamp"] = pd.to_datetime(df["timestamp"])

# grouped = df.groupby("load")

# throughput_data = []
# for load, group in grouped:
#     num_responses = len(group)
#     time_span = (
#         group["timestamp"].max() - group["timestamp"].min()
#     ).total_seconds()
#     if time_span < 1:
#         throughput = num_responses
#     else:
#         throughput = num_responses / time_span
#     throughput_data.append((load, throughput))

# throughput_df = pd.DataFrame(throughput_data, columns=["load", "throughput"])

# throughput_df = throughput_df.sort_values(by="load")

# plt.plot(throughput_df["load"], throughput_df["throughput"])
# plt.ylabel("Throughput [TPS]")
# plt.xlabel("Concurrent Users")
# plt.tick_params(axis="both", which="major")

# plt.show()

...

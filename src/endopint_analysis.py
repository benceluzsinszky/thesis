import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np

LATENCY_THRESHOLD = 2000

endpoints = []
# reading the JSON data using json.load()
file = "./resources/fmd_data.json"
with open(file) as train_file:
    data = json.load(train_file)


for i in data:
    endpoints.append(
        {
            "endpoint": i["name"].replace("endpoints.", ""),
            "hits": i["hits-overall"],
            "latency": i["median-overall"],
        }
    )


df = pd.DataFrame(endpoints)
df["vector_length"] = np.sqrt(df["hits"] ** 2 + df["latency"] ** 2)

df["hits_normalized"] = df["hits"] / df["hits"].max()
df["latency_normalized"] = df["latency"] / df["latency"].max()
df["normalized_length"] = np.sqrt(
    df["hits_normalized"] ** 2 + df["latency_normalized"] ** 2
)

df.sort_values(by=["normalized_length"], inplace=True, ascending=False)
print(df.head(15))


# Get the top 5 values in normalized length
df_under_threshold = df[df["latency"] < LATENCY_THRESHOLD]
top_5 = df_under_threshold.head(5)

plt.figure(figsize=(10, 6))
plt.scatter(df["latency"], df["hits"], color="blue", s=10)
plt.scatter(top_5["latency"], top_5["hits"], color="red", s=15)

# Annotate the top 5 points with their endpoint names
for idx, row in top_5.iterrows():
    plt.annotate(
        row["endpoint"],
        (row["latency"], row["hits"]),
        textcoords="offset points",
        xytext=(5, -2),
        ha="left",
        fontsize=8,
    )

plt.xscale("log")  # Set x-axis to logarithmic scale
plt.yscale("log")  # Set y-axis to logarithmic scale
plt.xlabel("Latency")
plt.ylabel("Hits")
plt.title("Hits vs Latency")
plt.grid(True)
plt.axvline(x=LATENCY_THRESHOLD, color="red", linestyle="--")

plt.show()

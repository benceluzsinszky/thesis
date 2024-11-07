import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def throughput(file_path: str):
    df = pd.read_csv(file_path)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    grouped = df.groupby("load")

    throughput_data = []
    for load, group in grouped:
        num_responses = len(group)
        time_span = (
            group["timestamp"].max() - group["timestamp"].min()
        ).total_seconds()
        if time_span < 1:
            throughput = num_responses
        else:
            throughput = num_responses / time_span
        throughput_data.append((load, throughput))

    throughput_df = pd.DataFrame(throughput_data, columns=["load", "throughput"])

    throughput_df = throughput_df.sort_values(by="load")

    plt.plot(throughput_df["load"], throughput_df["throughput"])
    plt.ylabel("Throughput [TPS]")
    plt.xlabel("Concurrent Users")
    plt.title("Throughput vs Concurrent Users")
    plt.show()


def latency_histogram(file_path: str):
    df = pd.read_csv(file_path)

    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 8))
    sns.histplot(
        data=df,
        x="latency",
        hue="endpoint",
        multiple="stack",
        palette="tab20",
        bins=100,
    )

    plt.xlabel("Latency")
    plt.ylabel("Count")
    plt.title("Latency Distribution by Endpoint")

    plt.show()


if __name__ == "__main__":
    # throughput("./results/20241104_120135.csv")
    latency_histogram("./results/20241102_160123.csv")

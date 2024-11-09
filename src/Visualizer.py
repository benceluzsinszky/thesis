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


def latency_histograms_per_load(file_path: str):
    load_points = [1, 5, 10, 20, 50, 100, 200]

    df = pd.read_csv(file_path)

    sns.set_theme(style="whitegrid")

    for load in load_points:
        df_load = df[df["load"] == load]

        plt.figure(figsize=(12, 8))
        sns.histplot(
            data=df_load,
            x="latency",
            hue="load",
            multiple="stack",
            palette="tab20",
            bins=150,
        )

        plt.xlabel("Latency")
        plt.ylabel("Count")
        plt.title(f"GET /session Latency Histogram  - {load} Concurrent Users")

        plt.show()


def latency_histogream_sum(file_path: str):
    df = pd.read_csv(file_path)

    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 8))
    sns.histplot(
        data=df,
        x="latency",
        hue="load",
        multiple="layer",
        palette="tab20",
        bins=150,
    )

    plt.xlabel("Latency")
    plt.ylabel("Count")
    plt.title("GET /session Summerized Latency Histogram")

    plt.show()


if __name__ == "__main__":
    file = "./results/get_session_sum_lucian.csv"
    throughput(file)
    # latency_histograms_per_load(file)
    # latency_histogream_sum(file)

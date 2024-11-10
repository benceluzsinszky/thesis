import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

LATENCY_THRESHOLD = 2


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
    plt.show()


def latency_histograms_per_load(file_path: str):
    load_points = [30]

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
            bins=30,
            legend=False,
        )

        plt.xlabel("Latency [s]", fontsize=16)
        plt.ylabel("Count", fontsize=16)
        plt.xlim(right=3, left=0)
        plt.axvline(x=LATENCY_THRESHOLD, color="red", linestyle="--", label="Threshold")

        plt.show()


def latency_histogram_sum(file_path: str):
    df = pd.read_csv(file_path)

    load_values = [1, 5, 25, 30, 50, 100, 200]
    df = df[df["load"].isin(load_values)]

    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 8))
    hist_plot = sns.histplot(
        data=df,
        x="latency",
        hue="load",
        multiple="layer",
        palette="tab20",
        bins=100,
    )

    plt.xlabel("Latency [s]", fontsize=16)
    plt.ylabel("Count", fontsize=16)
    plt.axvline(x=LATENCY_THRESHOLD, color="red", linestyle="--", label="Threshold")

    hist_plot.legend_.set_title("Concurrent Users")
    hist_plot.legend_.get_title().set_fontsize(16)
    for text in hist_plot.legend_.get_texts():
        text.set_fontsize(14)

    plt.show()


if __name__ == "__main__":
    file = "./results/get_session_sum_robert.csv"
    throughput(file)
    # latency_histograms_per_load(file)
    # latency_histogram_sum(file)

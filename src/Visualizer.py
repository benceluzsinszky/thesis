import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

LATENCY_THRESHOLD = 0.3


def throughput(df: pd.DataFrame):
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
    plt.ylabel("Throughput [TPS]", fontsize=18)
    plt.xlabel("Concurrent Users", fontsize=18)
    plt.tick_params(axis="both", which="major", labelsize=16)

    plt.show()


def latency_histograms_per_load(df: pd.DataFrame, load_points: list | None = None):
    if load_points is None:
        load_points = [1, 2, 4, 5, 10, 20, 50, 100, 200]

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

        plt.xlabel("Latency [s]", fontsize=18)
        plt.ylabel("Count", fontsize=18)
        plt.xlim(right=0.5, left=0)
        plt.axvline(
            x=LATENCY_THRESHOLD, color="red", linestyle="--", label="Threshold Latency"
        )
        plt.tick_params(axis="both", which="major", labelsize=16)

        plt.show()


def latency_histogram_sum(df: pd.DataFrame):
    load_values = [1, 2, 4, 5, 10, 20, 50, 100, 200]
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

    plt.xlabel("Latency [s]", fontsize=18)
    plt.ylabel("Count", fontsize=18)
    plt.axvline(
        x=LATENCY_THRESHOLD, color="red", linestyle="--", label="Threshold Latency"
    )

    hist_plot.legend_.set_title("Concurrent Users")
    hist_plot.legend_.get_title().set_fontsize(16)
    for text in hist_plot.legend_.get_texts():
        text.set_fontsize(14)
    plt.tick_params(axis="both", which="major", labelsize=16)

    plt.show()


def latency_curve(df: pd.DataFrame, load: int = 1):
    # Filter the data if necessary
    df = df[df["load"] == load]  # Uncomment and modify if you need to filter by load

    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 8))

    # Plot latency vs. number of requests (index)
    plt.plot(df.index, df["latency"], label="Latency")

    plt.axhline(
        y=LATENCY_THRESHOLD, color="red", linestyle="--", label="Threshold Latency"
    )

    plt.xlabel("Number of Requests", fontsize=18)
    plt.ylabel("Latency [s]", fontsize=18)
    plt.legend(fontsize=16)
    plt.tick_params(axis="both", which="major", labelsize=16)

    plt.show()


if __name__ == "__main__":
    file = "./results/available_languages_sum.csv"
    df = pd.read_csv(file)
    # throughput(df)
    latency_histograms_per_load(df, [4])
    # latency_histogram_sum(df)
    # latency_curve(df, 2)

import pandas as pd
import matplotlib.pyplot as plt


def visualize(df: pd.DataFrame):
    # df = df[["load", "throughput"]]

    # df = df.groupby("load", as_index=False).mean()

    # df = df.sort_values(by="load")

    # plt.plot(df["load"], df["throughput"])
    # plt.ylabel("Throughput [TPS]")
    # plt.xlabel("Load [Threads]")
    # plt.title("Knee Point")
    # plt.show()

    bucket_size_ms = 100
    bucket_size_s = bucket_size_ms / 1000  # Convert to seconds

    plt.hist(
        df["user_time"],
        bins=int((df["user_time"].max() - df["user_time"].min()) / bucket_size_s),
    )
    plt.xlabel("User Time (s)")
    plt.ylabel("Frequency")
    plt.title("Histogram of User Time with 100ms Buckets")
    plt.show()

    pass

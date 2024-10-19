import pandas as pd
import matplotlib.pyplot as plt

from args import get_csv_file_path

if __name__ == "__main__":
    df = pd.read_csv(get_csv_file_path())

    df = df[["load", "throughput"]]

    df = df.groupby("load", as_index=False).mean()

    df = df.sort_values(by="load")

    plt.plot(df["load"], df["throughput"])
    plt.ylabel("Throughput [TPS]")
    plt.xlabel("Load [Threads]")
    plt.title("Knee Point")
    plt.show()

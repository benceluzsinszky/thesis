import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib import cm

LATENCY_THRESHOLD = 2


def create_throughput_df(df: pd.DataFrame):
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="ISO8601")

    grouped = df.groupby("load")

    throughput_data = []
    for load, group in grouped:
        time_deltas = []
        for i in range(0, len(group), load):
            if i + load - 1 < len(group):
                start_time = group.iloc[i]["timestamp"]
                end_time = group.iloc[i + load - 1]["timestamp"]
                time_delta = (end_time - start_time).total_seconds()
                time_deltas.append(time_delta)

        if time_deltas:
            median_time_delta = np.median(time_deltas)

            if median_time_delta < 1:
                median_time_delta = 1

            throughput = load / median_time_delta
            throughput_data.append((load, throughput))

    throughput_df = pd.DataFrame(throughput_data, columns=["load", "throughput"])

    # smoothing
    # throughput_df["throughput"] = throughput_df["throughput"].ewm(span=25).mean()

    throughput_df = throughput_df.sort_values(by="load")

    return throughput_df


def throughput(df: pd.DataFrame):
    throughput_df = create_throughput_df(df)

    plt.plot(throughput_df["load"], throughput_df["throughput"])
    plt.ylabel("Throughput [TPS]")
    plt.xlabel("Concurrent Users")
    plt.tick_params(axis="both", which="major")

    plt.show()


def latency_histogram_of_load(df: pd.DataFrame, load: int):
    df = df[df["load"] == load]

    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 8))
    sns.histplot(
        data=df,
        x="latency",
        hue="load",
        multiple="stack",
        palette="tab20",
        binwidth=0.02,
        legend=False,
    )

    plt.xlabel("Latency [s]", fontsize=18)
    plt.ylabel("Count", fontsize=18)
    plt.xlim(left=0)
    plt.axvline(
        x=LATENCY_THRESHOLD, color="red", linestyle="--", label="Threshold Latency"
    )
    plt.tick_params(axis="both", which="major", labelsize=16)

    plt.show()


def latency_histogram_sum(df: pd.DataFrame):
    load_values = df["load"].unique()
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


def latency_curve_median(df: pd.DataFrame):
    grouped = df.groupby("load")

    median_latency_data = []
    for load, group in grouped:
        median_latency = group["latency"].median()
        median_latency_data.append((load, median_latency))

    median_latency_df = pd.DataFrame(
        median_latency_data, columns=["load", "median_latency"]
    )

    # remove last line
    median_latency_df = median_latency_df.iloc[:-1]

    plt.figure(figsize=(12, 8))
    plt.plot(median_latency_df["load"], median_latency_df["median_latency"], marker="o")
    plt.xlabel("Concurrent Users (Load)", fontsize=18)
    plt.ylabel("Median Latency [s]", fontsize=18)
    plt.title("Median Latency vs. Concurrent Users", fontsize=20)
    plt.tick_params(axis="both", which="major", labelsize=16)
    plt.grid(True)

    plt.show()


def create_latency_df(df: pd.DataFrame):
    grouped = df.groupby("load")

    latency_data = []
    for load, group in grouped:
        latency = group["latency"].mean()
        latency_data.append((load, latency))

    latency_df = pd.DataFrame(latency_data, columns=["load", "latency"])
    # latency_df["latency"] = latency_df["latency"].ewm(span=25).mean()

    # remove last line
    latency_df = latency_df.iloc[:-1]

    return latency_df


def latency_curve_avg(df: pd.DataFrame):
    avg_latency_df = create_latency_df(df)

    plt.figure(figsize=(12, 8))
    plt.plot(avg_latency_df["load"], avg_latency_df["latency"], marker="o")
    plt.xlabel("Concurrent Users (Load)", fontsize=18)
    plt.ylabel("Average Latency [s]", fontsize=18)
    plt.title("Average Latency vs. Concurrent Users", fontsize=20)
    plt.tick_params(axis="both", which="major", labelsize=16)
    plt.grid(True)

    plt.show()


def latency_histogram_3d(df: pd.DataFrame):
    df = df[df["latency"] <= 10]  # Filter data for better visualization

    latency = df["latency"]
    load = df["load"]

    # Create bins:
    #  - For latency, we use 50 equally spaced bins between its min and max.
    #  - For load, we assume discrete points. If they are exactly 1,2,...,9 then we
    #    create bins that separate each load value.
    latency_bins = np.linspace(latency.min(), latency.max(), 50)

    # Create load bins: for discrete values, we need bin edges.
    unique_loads = np.sort(df["load"].unique())
    # Create edges halfway between adjacent unique load values.
    load_edges = np.concatenate(
        (
            [unique_loads[0] - 0.5],
            (unique_loads[:-1] + unique_loads[1:]) / 2,
            [unique_loads[-1] + 0.5],
        )
    )

    # Compute the 2D histogram
    hist, latency_edges, load_edges = np.histogram2d(
        latency, load, bins=[latency_bins, load_edges]
    )

    # Normalize each load bin (i.e., each column) to sum to 100%.
    # hist shape is (len(latency_bins)-1, len(load_edges)-1)
    for col in range(hist.shape[1]):
        col_sum = hist[:, col].sum()
        if col_sum > 0:
            hist[:, col] = hist[:, col] / col_sum * 100

    # Compute bin centers for plotting.
    latency_centers = (latency_edges[:-1] + latency_edges[1:]) / 2
    load_centers = (load_edges[:-1] + load_edges[1:]) / 2

    # Create meshgrid for bar positions.
    latency_grid, load_grid = np.meshgrid(latency_centers, load_centers, indexing="ij")

    # Flatten the grids and histogram.
    x_pos = latency_grid.ravel()
    y_pos = load_grid.ravel()
    z_pos = np.zeros_like(x_pos)
    bar_heights = hist.ravel()

    # Compute bar widths in the x and y directions.
    dx = np.diff(latency_edges).mean() * np.ones_like(x_pos)
    dy = np.diff(load_edges).mean() * np.ones_like(y_pos)

    # Normalize bar heights for colormap
    norm = plt.Normalize(vmin=latency.min(), vmax=LATENCY_THRESHOLD)
    colors = cm.get_cmap("RdYlGn_r")(norm(x_pos))

    # Filter out bars with 0% height
    non_zero_mask = bar_heights > 0
    x_pos = x_pos[non_zero_mask]
    y_pos = y_pos[non_zero_mask]
    z_pos = z_pos[non_zero_mask]
    bar_heights = bar_heights[non_zero_mask]
    dx = dx[non_zero_mask]
    dy = dy[non_zero_mask]
    colors = colors[non_zero_mask]

    # Plotting the 3D bars.
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.bar3d(x_pos, y_pos, z_pos, dx, dy, bar_heights, color=colors, shade=True)

    ax.set_xlabel("Latency (s)")
    ax.set_ylabel("Concurrent Users (Load)")
    ax.set_zlabel("Percentage (%)")
    ax.set_title("3D Histogram of Latency vs. Concurrent Users\n(Normalized per Load)")

    plt.show()


def check_latency(df: pd.DataFrame, load: int) -> None:
    df = df[df["load"] == load]
    df = df[df["latency"].notna() & (df["latency"] != "N/A")]
    median_latency = df["latency"].median()
    print(median_latency)


def requests_sent_time(df: pd.DataFrame, load: int) -> None:
    # Filter the DataFrame for the specified load
    df = df[df["load"] == load].head(load)  # Limit to the first 'load' rows

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="ISO8601")

    # Subtract latency from timestamp to get the request sent time
    df["sent_time"] = df["timestamp"] - pd.to_timedelta(df["latency"], unit="s")

    # Normalize sent_time so the first timestamp is 0
    first_sent_time = df["sent_time"].min()
    df["normalized_sent_time"] = (df["sent_time"] - first_sent_time).dt.total_seconds()

    # Plot the normalized sent times
    plt.figure(figsize=(12, 8))
    plt.scatter(df["normalized_sent_time"], df.index, alpha=0.6, label="Requests")
    plt.xlabel("Time Since First Request (s)", fontsize=14)
    plt.ylabel("Request Index", fontsize=14)
    plt.title("Requests Sent Over Time", fontsize=16)
    plt.grid(True)
    plt.legend()
    plt.show()


def latency_and_throughput_curve(df: pd.DataFrame):
    throughput_df = create_throughput_df(df)
    latency_df = create_latency_df(df)

    # Create the figure and axis
    fig, ax1 = plt.subplots(figsize=(12, 8))

    # Plot throughput on the left y-axis
    ax1.plot(
        throughput_df["load"],
        throughput_df["throughput"],
        color="tab:blue",
        marker="^",
        label="Throughput [TPS]",
    )
    ax1.set_xlabel("Concurrent Users (Load Point)", fontsize=24, labelpad=20)
    ax1.set_ylabel("Throughput [TPS]", fontsize=24, labelpad=20)
    ax1.tick_params(axis="both", which="major", labelsize=20)
    ax1.set_xlim(left=0)
    ax1.set_ylim(bottom=0)

    # Create a second y-axis for latency
    ax2 = ax1.twinx()
    ax2.plot(
        latency_df["load"],
        latency_df["latency"],
        color="tab:red",
        marker="s",
        label="Latency [s]",
    )
    ax2.set_ylabel("Latency [s]", fontsize=24, labelpad=20)
    ax2.tick_params(axis="y", which="major", labelsize=20)

    # Add grid and title
    ax1.grid(True)

    # Add legends for both axes
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))

    plt.tight_layout()

    # Show the plot
    plt.show()


def compare_throughput(files: list[str] = None) -> None:
    plt.figure(figsize=(12, 8))  # Create a new figure
    markers = ["o", "s", "^", "D", "v", "P", "*"]
    for idx, file in enumerate(files):
        path = "./results/" + file
        df = pd.read_csv(path)
        throughput_df = create_throughput_df(df)
        label = "Apache"
        if "w_4" in file:
            label = "Gunicorn - 4 Workers"
        elif "w_8" in file:
            label = "Gunicorn - 8 Workers"
        elif "w_16" in file:
            label = "Gunicorn - 16 Workers"
        plt.plot(
            throughput_df["load"],
            throughput_df["throughput"],
            label=label,
            alpha=0.8,
            marker=markers[idx % len(markers)],
        )

    plt.xlabel("Concurrent Users (Load)", fontsize=18)
    plt.ylabel("Throughput [TPS]", fontsize=18)
    plt.title("Throughput Comparison", fontsize=20)
    plt.tick_params(axis="both", which="major", labelsize=16)
    plt.legend(loc="upper left")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    LANGUAGES = "available_languages"
    EXERCISE = "exercise_session_update"
    READING = "reading_session_update"
    USER_ACTIVITY = "upload_user_activity_data"
    USER_ARTICLE = "user_article"
    RECOMMENDED = "user_articles_recommended"

    APACHE = "apache"
    G4 = "gunicorn_w_4"
    G8 = "gunicorn_w_8"
    G16 = "gunicorn_w_16"

    endpoint = USER_ACTIVITY

    file_to_visualize = f"{endpoint}_{G4}.csv"

    path = "./results/" + file_to_visualize

    df = pd.read_csv(path)

    # latency_and_throughput_curve(df)
    compare_throughput(
        [
            f"{endpoint}_{APACHE}.csv",
            f"{endpoint}_{G4}.csv",
            f"{endpoint}_{G8}.csv",
            f"{endpoint}_{G16}.csv",
        ]
    )
    # latency_histogram_3d(df)

    # throughput(df)
    # latency_curve_avg(df)
    # latency_curve_median(df)
    # latency_histogram_of_load(df, 2000)
    # latency_histogram_sum(df)

    # check_latency(df, 355)
    # requests_sent_time(df, 1500)

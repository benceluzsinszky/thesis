import argparse

parser = argparse.ArgumentParser(description="Process some integers.")

parser.add_argument(
    "--threads", "-t", type=int, help="The number of threads. Default: 1", default=1
)

parser.add_argument(
    "--loops",
    "-l",
    type=int,
    help="The number of times the simulator will run. Default: 1",
    default=1,
)

parser.add_argument(
    "--endpoint",
    "-e",
    type=int,
    help="Use single endpoint, use the index of the endpoint from the config file.",
)
parser.add_argument(
    "--config_path",
    "-c",
    type=str,
    help="The path to the config file.",
    default="src/config.json",
)
parser.add_argument("--random", "-r", action="store_true", help="Use random endpoints.")

parser.add_argument(
    "--no_save",
    "-ns",
    help="Don't save the output .csv file.",
    action="store_true",
)

parser.add_argument(
    "--skip",
    "-s",
    help="Increment users by 10 every iteration, instead of 1.",
    action="store_true",
)

args = parser.parse_args()


def get_number_of_threads() -> int:
    return args.threads


def get_number_of_loops() -> int:
    return args.loops


def use_skip() -> bool:
    return args.skip


def use_endpoint() -> int:
    return args.endpoint


def get_config_path() -> str:
    return args.config_path


def use_csv_file() -> str:
    return not args.no_save

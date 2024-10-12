import argparse

parser = argparse.ArgumentParser(description="Process some integers.")

parser.add_argument(
    "--threads", "-t", type=int, help="The number of threads", default=1
)
parser.add_argument(
    "--endpoint",
    "-e",
    type=int,
    help="Use single endpoint, use the index of the endpoint from the config file",
)
parser.add_argument(
    "--user_profile",
    "-u",
    type=int,
    help="Use user profile, use the index of the user profile from the config file",
)
parser.add_argument(
    "--config_path",
    "-c",
    type=str,
    help="The path to the config file",
    default="config.json",
)
parser.add_argument("--random", "-r", action="store_true", help="Use random endpoints")

args = parser.parse_args()


def get_number_of_threads() -> int:
    return args.threads


def use_endpoint() -> int:
    return args.endpoint


def use_user_profile() -> int:
    return args.user_profile


def use_random() -> bool:
    return args.random


def get_config_path() -> str:
    return args.config_path

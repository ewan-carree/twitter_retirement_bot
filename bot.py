
import argparse
import json
import os


def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search-pattern", "-s", default="retraite",
                        help="Search pattern, You can search between a user, a hashtag or a keyword. For example: @user, '#hashtag', keyword. Dont forget to put the search pattern between quotes if it's an hashtag or else it won't work.")
    parser.add_argument("--max-results", "-m", type=int,
                        default=5, help="Maximum number of results")
    parser.add_argument("--output", "-o", type=str,
                        default="scrap.json", help="Output file name")
    args = parser.parse_args()
    return args


def get_scraper(args: argparse.Namespace) -> str:
    search_pattern = args.search_pattern
    first_char = search_pattern[0]
    if first_char == "@":
        return "twitter-user"
    elif first_char == "#":
        return "twitter-hashtag"
    else:
        return "twitter-search"


def search(search_pattern: str, scrapper: str, max_results: int, output: str) -> list[dict[str, str]]:
    os.system(
        f"snscrape --jsonl --max-results {max_results} {scrapper} '{search_pattern}' > {output}")

    # load JSON data from file
    with open(f"{output}", "r") as file:
        data = file.readlines()

    # parse JSON data into a list of dictionaries
    records: list[dict[str, str]] = [json.loads(record) for record in data]

    # remove the original file
    os.remove(f"{output}")

    # wrap records in a single dictionary
    format_json(records, output)

    return records


def format_json(records: list[dict[str, str]], output: str) -> None:
    wrapped_data = {"records": records}

    # save wrapped data to a new file
    with open(f"{output}", "w") as file:
        json.dump(wrapped_data, file, indent=4)


if __name__ == "__main__":
    args = get_arguments()
    scrapper = get_scraper(args)
    print(
        f"---------- Searching for {args.search_pattern} using {scrapper} scrapper ----------")
    print()

    if scrapper == "twitter-user" or scrapper == "twitter-hashtag":
        args.search_pattern = args.search_pattern[1:]

    records = search(args.search_pattern, scrapper,
                     args.max_results, args.output)
    for record in records:
        print(f'- {record["renderedContent"]}')
        print()
        print()

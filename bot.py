
import argparse
import json
import multiprocessing
import os
import datetime
import subprocess
import time

def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pattern", "-p", default="retraite",
                        help="Search pattern, You can search between a user, a hashtag or a keyword. For example: @user, '#hashtag', keyword. Dont forget to put the search pattern between quotes if it's an hashtag or else it won't work.")
    parser.add_argument("--n-results", "-n", type=int,
                        default=5, help="Number of results")
    parser.add_argument("--output", "-o", type=str,
                        default="scrap.json", help="Output file name")
    parser.add_argument("--langage", "-l", type=str,
                        default="fr", help="Langage of the tweets (fr, en, es, de, ...))")
    parser.add_argument("--since", "-s", type=str, default=datetime.datetime.now().strftime("%Y-%m-%d"),
                        help="Since when do you want to search. Format: YYYY-MM-DD")
    parser.add_argument("--until", "-u", type=str, default=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                        help="Until when do you want to search. Format: YYYY-MM-DD")
    args = parser.parse_args()
    return args


def get_scraper(args: argparse.Namespace) -> str:
    pattern = args.pattern
    first_char = pattern[0]
    if first_char == "@":
        return "twitter-user"
    elif first_char == "#":
        return "twitter-hashtag"
    else:
        return "twitter-search"
    

def analyze(n_results: int, output: str, until: str, lang: str) -> None:
    records: list[dict[str, str]] = []
    while True:
        with open(f"{output}", "r") as file:
            data: list[str] = file.readlines()
            if len(data) > n_results:
                break
        
    for str_record in data:
        time.sleep(0.001) # to avoid rate limit
        record:  dict[str, str] = json.loads(str_record)
        if record["lang"] == lang and record not in records and record["date"] <= until:
            records.append(record)
        if len(records) >= n_results:
            break
        
    format_json(records, output)

def format_json(records: list[dict[str, str]], output: str) -> None:
    wrapped_data = {"records": records}
    with open("sorted_" + output, "w") as file:
        json.dump(wrapped_data, file, indent=4)


if __name__ == "__main__":
    args = get_arguments()
    scrapper = get_scraper(args)
    print(
        f"---------- Searching for '{args.pattern}' {int(args.n_results)} times using {scrapper} scrapper ----------")

    if scrapper == "twitter-user" or scrapper == "twitter-hashtag":
        args.pattern = args.pattern[1:]
        
    # check if json exists
    if os.path.exists(f"{args.output}"):
        os.remove(f"{args.output}")
    if os.path.exists("sorted_" + f"{args.output}"):
        os.remove("sorted_" + f"{args.output}")
    
    write_process = subprocess.Popen("exec " + f"snscrape --jsonl --since {args.since} {scrapper} ' {args.pattern.strip()} ' > {args.output}", stdout=subprocess.PIPE, shell=True)
    
    read_process = multiprocessing.Process(target=analyze, args=(int(args.n_results), args.output, args.until, args.langage))
    read_process.start()
    
    read_process.join()
    write_process.kill()
    
    os.remove(f"{args.output}")   
    print("---------- Done, check json for more information ----------")

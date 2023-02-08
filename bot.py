
import argparse
import json
import multiprocessing
import os
import datetime
import subprocess
import time
from typing import Callable, Any


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

def time_it(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args : Any, **kwargs: Any):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Executed in {end - start:.6f} seconds")
        return result
    return wrapper

def progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', decimals: int =1, length: int =100, fill: str ='█') -> None:
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    if iteration == total: 
        print()

@time_it
def analyze(n_results: int, output: str, until: str, lang: str) -> None:
    records: list[dict[str, str]] = []
    remaining = n_results
    
    temp_size: int = 0
    while remaining != 0:
        with open(f"{output}", "r") as file:
            data: list[str] = file.readlines()
            if len(data) < n_results:
                progress_bar(len(data), n_results, "Scrapping")
                continue
            for str_record in data[temp_size:]:
                time.sleep(0.001)
                record = json.loads(str_record)
                if record["lang"] == lang and record not in records and record["date"] <= until:
                    records.append(record)
                    remaining -= 1
                    progress_bar(len(records), n_results, "Analyzing")
                    if remaining == 0:
                        break
                temp_size = len(data)
    
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

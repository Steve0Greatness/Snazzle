from functools import lru_cache
import requests
from time import time
from datetime import datetime

SCRATCHDB = "https://scratchdb.lefty.one/v3/"
useDB = False  # always change to true if on replit or other online ides. only affects project info for now
REPLIT_MODE = False

def use_scratchdb(value):
    global USE_SDB
    USE_SDB = value

def replit_mode(value):
    global REPLIT_MODE
    REPLIT_MODE = value

def remove_duplicates(input_list):
    # needs to work on unhashable datatypes
    result_list = []
    for dict in input_list:
        if dict not in result_list:
            result_list.append(dict)
    return result_list


@lru_cache(maxsize=15)
def get_topics(category, page):
    r = requests.get(f"{SCRATCHDB}forum/category/topics/{category}/{page}?detail=0&filter=1")
    try:
        if type(r.json()) != list:
            return {"error": True, "message": "sdb_" + r.json()["error"].lower()}

        return {"error": False, "topics": remove_duplicates(r.json())}
    except requests.exceptions.JSONDecodeError:
        return {"error": True, "message": "lib_scratchdbdown"}


@lru_cache(maxsize=15)
def get_post_info(post_id):
    r = requests.get(f"{SCRATCHDB}forum/post/info/{post_id}")
    return r.json()


def get_author_of(post_id):
    return "user"
    # r = requests.get(f'{SCRATCHDB}forum/post/info/{post_id}')
    # return r.json()['username']


@lru_cache(maxsize=15)
def get_project_info(project_id):
    if not useDB:
        r = requests.get(f'https://scratchdb.lefty.one/v2/project/info/id/{project_id}')
    else:
        r = requests.get(f"https://api.scratch.mit.edu/projects/{project_id}")
    return r.json()


@lru_cache(maxsize=15)
def get_comments(project_id):
    if not REPLIT_MODE:
        return None # i'll do this later
    try:
        project_creator = requests.get(
            f"https://api.scratch.mit.edu/projects/{project_id}"
        ).json()["author"]["username"]
    except Exception:
        return None
    r = requests.get(
        f"https://api.scratch.mit.edu/users/{project_creator}/projects/{project_id}/comments?limit=40"
    )
    return r.json()


@lru_cache(maxsize=5)
def get_ocular(username):
    try:
        info = requests.get(f"https://my-ocular.jeffalo.net/api/user/{username}")
        info.json()["name"]
    except Exception:
        return {
            "name": None,
            "status": None,
            "color": None,
        }  # i had  to spell colour wrong for it to work
    return info.json()

@lru_cache(maxsize=5)
def get_aviate(username):
    # Aviate API is much simple very wow
    # Better than ocular API imo
    r = requests.get(f"https://aviate.scratchers.tech/api/{username}")
    if r['success'] == False:
        return ''
    else:
        return r["status"]

def get_featured_projects():
    r = requests.get("https://api.scratch.mit.edu/proxy/featured")
    return r.json()


@lru_cache(maxsize=15)
def get_topic_data(topic_id):
    r = requests.get(f"{SCRATCHDB}forum/topic/info/{topic_id}")
    try:
        if "error" in r.json().keys():
            return {"error": True, "message": "sdb_" + r.json()["error"].lower()}

        return {"error": False, "data": r.json()}
    except requests.exceptions.JSONDecodeError:
        return {"error": True, "message": "lib_scratchdbdown"}


@lru_cache(maxsize=15)
def get_trending_projects():
    # TODO: implement limits and offsets
    # language parameter seems to be ineffectual when set to another lang
    r = requests.get(
        "https://api.scratch.mit.edu/explore/projects?limit=20&language=en&mode=trending&q=*"
    )
    return r.json()


def get_topic_posts(topic_id, page=0, order="oldest"):
    r = requests.get(f"{SCRATCHDB}forum/topic/posts/{topic_id}/{page}?o={order}")
    # post['author'], post['time'], post['html_content'], post['index'], post['is_deleted']
    try:
        if type(r.json()) != list:
            return {'error': True, 'message': 'sdb_' + r.json()['error'].lower()}

        return {'error': False, 'posts': [{'author': post['username'], 'time': post['time']['first_checked'], 'html_content': post['content']['html'], 'is_deleted': post['deleted']} for post in r.json()]}
    except requests.exceptions.JSONDecodeError:
        return {"error": True, "message": "lib_scratchdbdown"}

def get_pfp_url(username, size = 90):
    r = requests.get(f"https://api.scratch.mit.edu/users/{username}")
    
    return r.json()['profile']['images'][str(size) + 'x' + str(size)]

# Below this line is all stuff used for the REPL mode which is used for debugging
# Generally, don't touch this, unless there's a severe flaw or something


def parse_token(token: str, i: int):
    if isinstance(token, str) and i > 0 and "." in token:
        return token.replace(".", " ")
    return token


def parse_cmd(cmd: str):
    if not isinstance(cmd, str):
        return None

    return_cmd = [parse_token(token, i) for i, token in enumerate(cmd.split(" "))]

    return return_cmd[0] + "(" + ", ".join(return_cmd[1:]) + ")"


if __name__ == "__main__":
    cmd = None
    while True:
        cmd = input("input> ")
        parsed_cmd = parse_cmd(cmd)
        print("running>", parsed_cmd)
        print("output>", eval(parsed_cmd))

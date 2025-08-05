import requests
import random
import os
import time

USER_NAMES = os.environ["USER_NAMES"].split(",")
JELLYFIN_URL = os.environ.get("JELLYFIN_URL")
JELLYFIN_API_KEY = os.environ["JELLYFIN_API_KEY"]
MOVIES_LIMIT = int(os.environ.get("MOVIES_LIMIT", 3))
REFRESH_TIME = int(os.environ.get("REFRESH_TIME", 30))

HEADERS = {
    "Authorization": f'MediaBrowser Token="{JELLYFIN_API_KEY}"',
}

def add_movies(user_name, user_id):
    try:
        response = requests.get(
            f"{JELLYFIN_URL}/Users/{user_id}/Items",
            headers=HEADERS,
            params={
                "Recursive": "true",
                "IncludeItemTypes": "Movie",
                "isPlayed": "false",
                "Tags": f"#jellyfomo-{user_name}",
            }
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching movies: {e}")
        return
    
    active_movies = response.json().get("Items", [])
    if len(active_movies) >= MOVIES_LIMIT : return
    active_movies_ids = [movie['Id'] for movie in active_movies]

    try:
        response = requests.get(
            f"{JELLYFIN_URL}/Users/{user_id}/Items",
            headers=HEADERS,
            params={
                "Recursive": "true",
                "IncludeItemTypes": "Movie",
                "isPlayed": "false",
                "ExcludeItemIds": ",".join(active_movies_ids),
            }
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching candidates movies: {e}")
        return

    candidates_movies = response.json().get("Items", [])

    while candidates_movies and len(active_movies) < MOVIES_LIMIT:
        movie = random.choice(candidates_movies)
        try:
            response = requests.get(
                f"{JELLYFIN_URL}/Users/{user_id}/Items/{movie['Id']}",
                headers=HEADERS,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching movie {movie['Name']} details: {e}")
            continue

        candidates_movies.remove(movie)
        movie = response.json()
        movie['Tags'].append(f"#jellyfomo-{user_name}")

        try:
            response = requests.post(
                f"{JELLYFIN_URL}/Items/{movie['Id']}",
                headers=HEADERS,
                json=movie
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error updating movie {movie['Name']} tags: {e}")
            continue
        active_movies.append(movie)
        print(f"Added #jellyfomo-{user_name} to movie {movie['Name']}")


def remove_watched_movies(user_name, user_id):
    try:
        response = requests.get(
            f"{JELLYFIN_URL}/Users/{user_id}/Items",
            headers=HEADERS,
            params={
                "Recursive": "true",
                "IncludeItemTypes": "Movie",
                "isPlayed": "true",
                "Tags": f"#jellyfomo-{user_name}",
            }
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching watched movies: {e}")
        return
    watched_movies = response.json().get("Items", [])

    for movie in watched_movies:
        try:
            response = requests.get(
                f"{JELLYFIN_URL}/Users/{user_id}/Items/{movie['Id']}",
                headers=HEADERS,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching movie {movie['Name']} details: {e}")
            continue

        movie = response.json()
        movie['Tags'] = [tag for tag in movie.get('Tags', []) if tag != f"#jellyfomo-{user_name}"]

        try:
            response = requests.post(
                f"{JELLYFIN_URL}/Items/{movie['Id']}",
                headers=HEADERS,
                json=movie
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error updating movie {movie['Name']} tags: {e}")
            continue
        print(f"Removed #jellyfomo-{user_name} tag from movie {movie['Name']}")

def get_user_id(user_name):
    try:
        response = requests.get(
            f"{JELLYFIN_URL}/Users",
            headers=HEADERS
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching users: {e}")
        return None
    
    users = response.json()
    user = next((user for user in users if user['Name'] == user_name), None)

    return user['Id'] if user else None

if __name__ == "__main__":
    users = []
    for user_name in USER_NAMES:
        user_id = get_user_id(user_name)
        if not user_id:
            print(f"User {user_name} not found, skipping.")
            continue
        users.append((user_name, user_id))

    while True:
        for user_name, user_id in users:
            remove_watched_movies(user_name, user_id)
            add_movies(user_name, user_id)
        time.sleep(REFRESH_TIME)
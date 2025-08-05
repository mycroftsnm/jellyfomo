# Jellyfomo
Feeling overwhelmed by your Jellyfin movie collection? jellyfomo limits how many movies you have active at once, helping you beat that “what should I watch?” anxiety.

## So what does it do?
It keeps only a set number of active movies per user, swapping finished ones automatically.

## Installation
Use the provided [compose.yaml](https://github.com/mycroftsnm/jellyfomo/blob/main/compose.yaml) and set at least the `JELLYFIN_URL`, `JELLYFIN_API_KEY`, `USER_NAMES` environment variables.

## Usage
On the first run, Jellyfomo will automatically create a tag in the format `'#jellyfomo-username'` for each configured user. It will then assign that tag to up to `MOVIES_LIMIT` random movies the user has not watched yet.

> **Note**: Jellyfomo tags start with `#` so they appear higher in the list.

----------

To view your selection, filter the movie library by your Jellyfomo tag (e.g., `#jellyfomo-charly`).

As you watch movies, Jellyfomo will automatically remove the tag from watched ones and assign it to new unseen picks. Keeping your selection fresh and within the limit.


[Demo video](https://github.com/user-attachments/assets/6472599f-5d08-4374-87e1-7e862121f029)
> (Of course, in a real scenario you'd **watch** the movies — not just mark them as played 😄)



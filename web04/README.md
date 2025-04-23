# Viby Notes

|         |                               |
| ------- | ----------------------------- |
| Authors | Alessandro Bombarda <@ale18v> |
| Points  | 500                           |
| Tags    | web                           |

## Challenge Description

There's a new kind of coding I call _vibe coding_, where you fully give in to the vibes, embrace exponentials, and forget that the code even exists. It's possible because the LLMs (e.g. Cursor Composer w Sonnet) are getting too good. Also I just talk to Composer with SuperWhisper so I barely even touch the keyboard. I ask for the dumbest things like "decrease the padding on the sidebar by half" because I'm too lazy to find it. I "Accept All" always, I don't read the diffs anymore. When I get error messages I just copy paste them in with no comment, usually that fixes it. The code grows beyond my usual comprehension, I'd have to really read through it for a while. Sometimes the LLMs can't fix a bug so I just work around it or ask for random changes until it goes away. It's not too bad for throwaway weekend projects, but still quite amusing. I'm building a project or webapp, but it's not really coding - I just see stuff, say stuff, run stuff, and copy paste stuff, and it mostly works.

Website: [https://viby.challs.ulisse.ovh:42691](https://viby.challs.ulisse.ovh:42691)

---

**NOTE:** The admin always connects with HTTP (like in the attached files)!

**NOTE:** The service name in the `docker-compose.yml` file has been updated from `nginx` to `web04-nginx`. **Everywhere** you see `nginx:8080` should be `web04-nginx:8080`. A new attachment is **NOT** provided ATM.

## Overview

The challenge consists of a blogging website. Registered users can create posts and add private notes to each post. Posts are public and even unauthenticated users can check them out, but in order to add notes they must be logged in.

Posts can be shared with the admin, who will type the flag as a private note on that post. As it is private, it can't be seen by other users.
Users can also upload custom css in their profile page that is included in all post pages.

## Code analysis

The backend is written in flask and served with gunicorn. The python backend is reverse proxied by Nginx.
The peculiarity is that there is an heavy focus on caching which is not usually seen in CTFs:

```nginx.conf
location / {
    # Rate limit requests
    limit_req zone=ip burst=20 nodelay;

    proxy_cache my_cache;
    proxy_no_cache $dont_cache;
    add_header X-Cache $upstream_cache_status always;
    proxy_pass http://backend:8000;

    location ~* \.(css|js|html|jpg|png|gif|svg)$ {
        rewrite ^/public/(.*) /$1 break;
        add_header X-Cache $upstream_cache_status always;
        proxy_ignore_headers Cache-Control;
        proxy_cache_valid 200 1h;
        proxy_pass http://backend:8000;
    }
}
```

Nginx has caching enabled for all locations proxied to the backend and it decides whether to cache or not depending on the `Cache-Control` header returned by the backend.
As a matter of fact the code has a `@cache_control` decorator that adds caching headers to the endpoints.
We also see that there's a blacklist on endpoints that should not be cached:

```
map $request_uri $dont_cache {
    default "0";
    ~*/posts/.* "1";
}

# ...
# location /
    proxy_no_cache $dont_cache;
# ...
```

Meaning that any request with `/posts/` in it will not be cached.

## Cache your CSS

The idea here is to try to have our post cached by nginx with our custom CSS so we can trigger some actions on the admin browser.
The main obstacles to achieving this behaviour are the blacklist and the fact that the endpoint issues `Cache-Control: no-store` which commands caches not to store the response:

```
@app.get("/posts/view/<uuid:post_id>")
@cache_control(public=False, no_store=True)
@with_user(required=False)
def view_post(post_id: uuid.UUID, user_id: uuid.UUID | None):
    post = utils.get_post_by_id(post_id, notes_by=user_id)
    if not post:
        return abort(404)

    css = utils.get_css(user_id)
    return render_template("/post/view.html", posts=[post],
                           show_actions=user_id and str(
                               user_id) == post["user_id"],
                           css=css)
```

Recall that the nginx config ignores caching headers for "static" routes:

```
    location ~* \.(css|js|html|jpg|png|gif|svg)$ {
        rewrite ^/public/(.*) /$1 break;
        add_header X-Cache $upstream_cache_status always;
        proxy_ignore_headers Cache-Control;
        proxy_cache_valid 200 1h;
        proxy_pass http://backend:8000;
    }
```

The rewrite rule is broken because it is lacking the string terminator at the end (`$`).
So if we send an URL such as `/public/posts/view/<post_id>%0A.css` the location will match and the URL will be rewritten to `/posts/view/<post_id>` because the group will match until the encoded newline `%0A`.
We can bypass the blacklist by URL-encoding the `/`: if we request `/public%2Fposts/view/<post_id>%0A.css` the `/posts/.*` regex will not match as `$request_uri` is the non-normalized URL.

Another important fact to note is that nginx uses the normalized and rewritten URL as a cache key.
Thus `/public%2Fposts/view/<post_id>%0A.css` will be stored as `/posts/view/<post_id>` inside the cache, exactly like the backend receives it.

To sum up:

1. We upload custom css
2. Create a post with id `X`
3. Request `/public%2Fposts/view/X%0A.css`

Then all subsequent requests to `/posts/view/X` will be our cached version.

## Exploit

One might expect to extract the flag via a CSS keylogger given that we can inject our CSS in the page where the admin is typing the flag.
To my knowledge this is not possible as the value of the input would have to be set explicitly (e.g like React does via JS). It is possible that the frontend framework used (MaterializeCSS) does this but I was not able to reproduce.
Anyways there is a clever idea that results in a simpler exploit:

1. Create 2 posts with ids `id_a` and `id_b`
2. Share post `a` with admin and he will comment the flag there
3. Upload the following CSS: `body { background-image: url("http://challenge/public%2fposts/view/id_a%0a.css")}`
4. Cache post `b` with your own css by requesting `/public%2Fposts/view/id_b%0a.css`
5. Have admin visit your cached post `b`. The css rule will trigger a request by the admin to `http://challenge/public%2fposts/view/id_a%0a.css`. This will cache his view of the post with his private notes, including the flag.
6. Access `/posts/view/id_a` and you will see the flag.

# MCPI-Reborn Local Skin Server
A way to manage and run skin servers for MCPI Reborn.
 - Wallee/Red-exe-Engineer

## Features
 - Run with no arguments to start the HTTP server.
 - Upload a skin file through CLI or HTTP/POST.
 - Delete skins from the local database.
 - List all skin names with their URL-safe base64 identifiers.

## Install & Run
```sh
$ git clone https://github.com/Red-exe-Engineer/skin-server.git
$ cd skin-server
$ python main.py
```

## Enable in MCPI-Reborn
To get the skin server to work with MCPI-Reborn you need to set the environment variable `MCPI_SKIN_SERVER` to the server's address/port.
```sh
$ MCPI_SKIN_SERVER=localhost:8080 ./minecraft-pi-reborn-x-y-z.AppImage # Replace with path to your MCPI-Reborn executable.
```

## Changing Address/Port
The address/port config is in `main.py`. I couldn't be bothered to add more CLI arguments or a proper config.

You can also set `ALLOW_QUERY` to True/False to enable GET requests for `/player` and `/players`

## CLI Arguments

| Long     | Short | Arguments                | Description                                                                 |
|----------|-------|--------------------------|-----------------------------------------------------------------------------|
| --upload | -u    | skin_file, optional:name | Uploads a skin to the database. Will use the file name if no name is given. |
| --delete | -d    | skin_name                | Deletes a skin from the database.                                           |
| --list   | -l    |                          | List all skin names and URL-safe base64 encoded titles.                     |
| --help   | -h    |                          | Displays help information.                                                  |

## HTTP

### GET `/`
Returns a friendly server message.

### GET `/players`
Returns a list of registered skins as clickable HTML links.

### GET `/player/<NAME>`
Redirects internally to the base64-encoded skin, returning the raw PNG.

### GET `/<base64(skin_name)>.png`
Returns the skin PNG.

### POST `/upload`
Uploads a skin using JSON:
```json
{
  "name": "<skin_name>",
  "data": "<base64_png_data>"
}
```
Example:
```sh
$ curl -X POST http://localhost:8080/upload/ \
     -H "Content-Type: application/json" \
     -d '{"name": "Alex", "data": "'"$(base64 -w 0 Alex.png)"'"}'
```

## Why Use This?
MCPI-Reborn requires your Github and MCPI username be the same to get a working skin.

While this is a great authentication method, my own Github username (Red-exe-Engineer) is a bit long, and I prefer going by "Wallee" in games or online.

So, why should you use it? I don't know. You figure it out. :D

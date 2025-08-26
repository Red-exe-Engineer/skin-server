""" 
Messily created by Wallee/Red-exe-Engineer.
A tool to maintain and serve a custom skin server for MCPI.


Optional arguments (CLI):
    -u --upload [skin_file] [optional:name]
        Uploads a skin to the database. Will use the file name if no name is given.

    -d --delete [skin_name]
        Deletes a skin from the database.

    -l --list
        List all skin names and URL-safe base64 encoded titles.

    -h --help
        Prints this help message.

HTTP API:
    GET /<base64(skin_name)>.png
        Retrieves a skin from the database.

    GET /player/(player_name)
        Plain-text version of the base64 skin retriever.

    GET /players
        Returns a list of registered player skins.

    POST /upload
        Uploads a skin using JSON:
        {
            "name": "<skin_name>",
            "data": "<base64_png_data>"
        }
    
    GET /
        Prints a simple server message.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from base64 import urlsafe_b64decode, urlsafe_b64encode, b64decode
from sys import argv
import json
import os


ADDRESS: str = "localhost"
PORT: int = 8080

ALLOW_QUERY: bool = True

# Path template for accessing skins on disk
SKIN_PATH: str = f'{os.path.dirname(__file__)}/skins/' + "{}"


def get_b64_name(name: str) -> str:
    return urlsafe_b64encode(name.encode()).decode()


def upload_skin(name: str | bytes, data: bytes) -> bool:
    """
    Saves a skin to the local database.

    Args:
        name (str): The skin name (filename without extension).
        data (bytes): Raw PNG data to be written.

    Returns:
        bool: True if successfully written, False otherwise.
    """

    if isinstance(name, str):
        name = get_b64_name(name)

    try:
        with open(SKIN_PATH.format(name) + ".png", "wb") as file:
            file.write(data)

        print("[UPLOAD]:", name)
        return True
    
    except Exception as error:
        print("[UPLOAD ERROR]:", error)
        return False


def download_skin(name: str) -> bytes | None:
    """
    Loads skin data from the database if it exists.

    Args:
        name (str): Skin name (filename without extension).

    Returns:
        bytes | None: PNG file contents if found, None otherwise.
    """

    if os.path.exists(skin := SKIN_PATH.format(name)):
        with open(skin, "rb") as file:
            print("[FOUND]:", skin)
            return file.read()

    print("[MISSING]:", name)
    return None


class MCPISkinServer(BaseHTTPRequestHandler):
    """
    HTTP handler class for serving and uploading MCPI skins.
    """

    def do_GET(self):
        response_data: bytes = b''

        if self.path == "/": # /
            response_data = b'Hello!\nSkin server by Wallee/Red-exe-Engineer'
            self.send_response(200)

        if ALLOW_QUERY:
            if self.path.startswith("/player/"): # /players/{player_name}/
                self.path = "/" + get_b64_name(self.path.split("/")[2]) + ".png"

            if self.path.startswith("/players"): # /players/

                # I love maps. Pure. Chaos.
                response_data = b'\n'.join(
                    map(
                        lambda name: f'<a href="/player/{name}">{name}</a>\n<br>'.encode(),
                        map(
                            lambda b64_name: urlsafe_b64decode(b64_name[:-4].encode()).decode(),
                            os.listdir(SKIN_PATH.format(""))
                        )
                    )
                )
                self.send_response(200)

        if self.path.endswith(".png"):
            try:
                response_data = download_skin(self.path) or b''

                if response_data:
                    self.send_response(200)
                else:
                    response_data = b'File not found'
                    self.send_response(404)

            except Exception as error:
                self.send_response(400)
                response_data = f"Invalid request: {error}".encode()

        if not response_data:
            self.send_response(404)

        self.end_headers()
        self.wfile.write(response_data)

    def do_POST(self):
        """
        Handles POST requests:
            - "/upload" expects JSON containing "name" and base64-encoded "data".
        Example:
            curl -X POST http://localhost:8080/upload/ \
                -H "Content-Type: application/json" \
                -d '{"name": "Alex", "data": "'"$(base64 -w 0 Alex.png)"'"}'
        """

        if self.path.startswith("/upload"):
            length = int(self.headers.get("Content-Length", 0))

            try:
                response = json.loads(self.rfile.read(length))
                name = response.get("name")
                data = response.get("data")

                if not name or not data:
                    raise ValueError("Missing 'name' or 'data' field")

                if upload_skin(name, b64decode(data.encode())):
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'Upload successful')
                    return

                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Upload failed')

            except Exception as error:
                self.send_response(400)
                self.end_headers()
                print(f"Invalid JSON: {error}")


if __name__ == "__main__":
    if not os.path.exists("skins"):
        print("Creating /skins directory. Upload skins using --upload or manually move the named files.")
        os.mkdir("skins")

    if len(argv) == 1:
        print(f'Starting server on {ADDRESS}:{PORT}')
        server = HTTPServer((ADDRESS, PORT), MCPISkinServer)

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            server.server_close()
            exit()

    if argv[1] in ("-u", "--upload"):
        if len(argv) < 3:
            exit("Missing path to skin. Usage:\n--upload [skin_file] [optional:name]")
        
        path = argv[2]

        try:
            if len(argv) > 3:
                name = argv[3]
            else:
                name = os.path.basename(path).removesuffix(".png")

            with open(path, "rb") as file:
                skin_data = file.read()

            upload_skin(name, skin_data)

        except Exception as error:
            exit("[ERROR]: " + str(error))

    elif argv[1] in ("-d", "--delete"):
        if len(argv) != 3:
            exit("Missing skin name. Usage:\n--delete [skin_name]")

        path = f'skins/{argv[2]}.png'

        if not os.path.exists(path):
            exit("Player not in skin database. Nothing to do.")
        
        try:
            os.remove(path)
            print(f"[DELETE]: {argv[2]}")

        except Exception as error:
            exit("Error: " + str(error))

    elif argv[1] in ("-l", "--list"):
        skin_names = sorted(
            map(
                lambda x: urlsafe_b64decode(x.removesuffix(".png")).decode(),
                os.listdir("skins")
            ),
            key=len
        )

        if not skin_names:
            exit()


        max_length = len(skin_names[-1])
        max_length_b64 = len(get_b64_name(skin_names[-1]))

        print(f'{"NAME":-^{max_length}} + {"BASE64":-^{max_length_b64}}')

        for name in skin_names:
            print(f'{name:<{max_length}} | {urlsafe_b64encode(name.encode()).decode()}')

    elif argv[1] == "--help":
        print(__doc__)

    else:
        exit("Invalid usage. Use --help for more info.")

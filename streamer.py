from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from remotezip import RemoteZip
import mimetypes
import requests
import logging
import os
import re

ARK_SERVER = os.environ.get("ARK_SERVER", "http://staffaccess.dl.bl.uk")

app = FastAPI()

logger = logging.getLogger(__name__)


def StreamerResponse(url: str, ark_path: str):

    # If ark_path is not set, proxy the whole file back with the right Content-Type:
    # Needs to return the actual item even if there's a slash after the ARK.
    if ark_path == None or ark_path == "":
        r = requests.get(url, stream=True)
        logger.info(f"  {r.status_code}")
        return StreamingResponse(r.iter_content(chunk_size=10*1024),
                media_type=r.headers['Content-Type'])

    def iterfile(url): 
        with RemoteZip(url) as z:
            if ark_path:
                try:
                    info = z.getinfo(ark_path)
                except Exception as e:
                    info = None
            else:
                info = None
            # List content?
            if info == None or info.is_dir():
                for name in z.namelist():
                    if name.startswith(ark_path):
                        yield f"{name}\n"
            else:
                # Return an item:
                with z.open(ark_path) as file_like:
                    yield from file_like

    # Guess mimetype:
    type, encoding = mimetypes.guess_type(ark_path)
    if not type:
        type = "text/plain"

    return StreamingResponse(iterfile(url), media_type=type)


@app.get("/ark:/81055/{ark_id}")
def get_by_ark(ark_id: str):
    backend_url = f"{ARK_SERVER}/ark:/81055/{ark_id}"
    return StreamerResponse(backend_url, None)

@app.get("/ark:/81055/{ark_id}/{ark_path:path}")
def get_by_ark_and_path(ark_id: str, ark_path:str):
    backend_url = f"{ARK_SERVER}/ark:/81055/{ark_id}"
    logger.info(f"ark_and_path {backend_url} / {ark_path}")
    return StreamerResponse(backend_url, ark_path)

@app.get("/proxy/{backend_url_and_path:path}")
def get_by_url(backend_url_and_path:str):
    
    # Use Regex to spot the ARK ID and separate the Path off the end.
    m = re.search("(.*)/ark:/(\d+)/([^\/]+)(.*)", backend_url_and_path)
    backend_url = f"{m.group(1)}/ark:/{m.group(2)}/{m.group(3)}"
    ark_path = None
    if m.group(4):
        ark_path = m.group(4)
        ark_path = ark_path.lstrip("/")

    logger.info(f"by_url {backend_url} / {ark_path}")

    return StreamerResponse(backend_url, ark_path)


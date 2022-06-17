from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from remotezip import RemoteZip
import mimetypes
import os

ARK_SERVER = os.environ.get("ARK_SERVER", "http://staffaccess.dl.bl.uk")

app = FastAPI()


@app.get("/ark:/81055/{ark_id}/{ark_path:path}")
def main(ark_id: str, ark_path:str):

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

    backend_url = f"{ARK_SERVER}/ark:/81055/{ark_id}"

    # Guess mimetype:
    type, encoding = mimetypes.guess_type(ark_path)
    if not type:
        type = "text/plain"

    return StreamingResponse(iterfile(backend_url), media_type=type)

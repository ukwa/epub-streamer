# epub-streamer
A simple standalone service to stream the contents of zipped ePubs.


## Development

```bash
source venv/bin/activate
pip install -r requirements.txt
uvicorn streamer:app --reload
```
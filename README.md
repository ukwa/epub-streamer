# epub-streamer
A simple standalone service to stream the contents of zipped ePubs.


## Development

```bash
source venv/bin/activate
pip install -r requirements.txt
uvicorn streamer:app --reload
```

## Change Log

- 1.0.0 - initial streaming reader version
- 1.0.1 - added hacky workaround for ePubs with wrong content type #4
 
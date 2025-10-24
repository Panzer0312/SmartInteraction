from fastapi import FastAPI
import redis, json

app = FastAPI()
r = redis.Redis(host="redis", port=6379)

@app.get("/results")
def get_results():
    results = r.lrange("results", 0, -1)
    return [json.loads(x) for x in results]

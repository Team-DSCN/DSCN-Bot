import aiohttp

class Requests:
    async def get(self, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.get(*args, **kwargs) as r:
                json_object = await r.json()

                return {"status":r.status, "json":json_object}

import httpx


async def fetch_external_user(user_id: int) -> dict:
    url = f"https://jsonplaceholder.typicode.com/users/{user_id}"

    timeout = httpx.Timeout(10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url)
        response.raise_for_status()

        return response.json()
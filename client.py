import errno

import aiofiles
import asyncio
import hashlib
import aiohttp
import sys
import os


async def http_mv_client(mv_http_remote, mv_http_dest):
    # Prepare stage
    if not os.path.exists(mv_http_dest):
        os.makedirs(mv_http_dest)

    # Do magic
    async with aiohttp.ClientSession() as session:
        # List files
        async with session.get(mv_http_remote) as response:
            files = (await response.json())["files"]

        # For each file
        for file in files:
            # Download file
            async with session.get(f"{mv_http_remote}/download/{file}") as response:
                if response.status != 200:
                    print(f"Error downloading {file}")
                    break
                if not os.path.exists(os.path.dirname(os.path.join(mv_http_dest, file))):
                    try:
                        os.makedirs(os.path.dirname(os.path.join(mv_http_dest, file)))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
                async with aiofiles.open(os.path.join(mv_http_dest, file), mode='wb') as f:
                    async for data in response.content.iter_chunked(1024):
                        await f.write(data)

            # Calculate hash
            local_hash = hashlib.sha256()
            async with aiofiles.open(os.path.join(mv_http_dest, file), mode='rb') as f:
                while True:
                    data = await f.read(1024)
                    if not data:
                        break
                    local_hash.update(data)
            local_hash = local_hash.hexdigest()

            # Remove file
            async with session.get(f"{mv_http_remote}/remove/{local_hash}/{file}") as response:
                if response.status != 200:
                    print(f"Error deleting {file}")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(http_mv_client(sys.argv[1], sys.argv[2]))
    loop.close()

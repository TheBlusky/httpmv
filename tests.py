from uvicorn import Config, Server
import server as http_mv_server
import aiofiles
import asyncio
import glob
import os

from client import http_mv_client


async def do_tests():
    # Create dummy files
    os.makedirs("tests")
    os.makedirs("tests/client")
    os.makedirs("tests/server")
    os.makedirs("tests/server/empty_dir")
    os.makedirs("tests/server/sub1")
    os.makedirs("tests/server/sub1/sub2")
    for filename in [
        "tests/server/f1",
        "tests/server/f2",
        "tests/server/sub1/f3",
        "tests/server/sub1/sub2/f4",
    ]:
        async with aiofiles.open(filename, mode='wb') as f:
            await f.write(os.urandom(10240))

    # Launch server
    http_mv_server.files_path = os.path.join(os.getcwd(), "tests/server")
    http_mv_server.files_pattern = "**"
    server = Server(config=Config(http_mv_server.app, host='127.0.0.1', port=8000))
    loop = asyncio.get_event_loop()
    loop.create_task(server.serve(sockets=None))
    await asyncio.sleep(2)  # Create server

    # Launch client
    await http_mv_client("http://127.0.0.1:8000", "tests/client")

    # Check
    files_local = glob.glob("tests/**", recursive=True)
    files_supposed = [
        "tests/client/f1",
        "tests/client/f2",
        "tests/client/sub1/f3",
        "tests/client/sub1/sub2/f4",
        "tests\\client\\f1",
        "tests\\client\\f2",
        "tests\\client\\sub1\\f3",
        "tests\\client\\sub1\\sub2\\f4",
    ]
    for file in files_local:
        if file in files_supposed:
            os.remove(file)
    os.rmdir("tests/client/sub1/sub2")
    os.rmdir("tests/client/sub1")
    os.rmdir("tests/client/")

    # Exit server
    server.handle_exit(None, None)
    await asyncio.sleep(2)  # Gracefully

    # Clean
    os.rmdir("tests/server/sub1/sub2")
    os.rmdir("tests/server/sub1")
    os.rmdir("tests/server/empty_dir")
    os.rmdir("tests/server")
    os.rmdir("tests")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_tests())
    loop.close()

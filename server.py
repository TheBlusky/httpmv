from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, FileResponse
import aiofiles
import hashlib
import uvicorn
import glob
import os
import sys

app = Starlette(debug=bool(os.environ.get("MV_DEBUG", False)))

files_path = os.environ.get("MV_FP", ".")
files_pattern = os.environ.get("MV_FP", "**")


def get_files():
    pwd = os.getcwd()
    os.chdir(files_path)
    files = [f for f in glob.glob(files_pattern, recursive=True) if not os.path.isdir(f)]
    os.chdir(pwd)
    return files


@app.route('/')
async def http_mv_list(request):
    files = get_files()
    return JSONResponse({"files": files})


@app.route('/download/{file}')
async def http_mv_download(request):
    files = get_files()
    file = request.path_params['file']
    if file not in files:
        raise HTTPException(404)
    return FileResponse(os.path.join(files_path, file))


@app.route('/remove/{hash}/{file}')
async def http_mv_remove(request):
    files = get_files()
    file = request.path_params['file']
    if file not in files:
        raise HTTPException(404)
    file = os.path.join(files_path, file)
    local_hash = hashlib.sha256()
    async with aiofiles.open(file, mode='rb') as f:
        while True:
            data = await f.read(1024)
            if not data:
                break
            local_hash.update(data)
    local_hash = local_hash.hexdigest()
    given_hash = request.path_params['hash']
    if local_hash != given_hash:
        raise HTTPException(
            406,
            detail=f"Wrong hash, expected: {local_hash}, received: {given_hash}"
        )
    os.remove(file)
    return JSONResponse({'status': 'ok'})

if __name__ == '__main__':
    if len(sys.argv) >= 1:
        files_path = sys.argv[1]
    if len(sys.argv) >= 2:
        files_pattern = sys.argv[2]
    uvicorn.run(app, host='0.0.0.0', port=8000)

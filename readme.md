# HTTP mv - Move file through the power... of the Internet

## Purpose

I needed to be able to retrieve files from one server to another, and delete it once retrieved. That's the purpose of
this project.

**Warning !!!** This project comes with **NO SECURITY**. If misconfigured, files will be exposed on the Internet, and
anyone retrieving it will be able to delete it ! Usage of reverse proxy ensuring authentification / authorization /
filtering is strongly advised.

## Usage

- Server: `python server.py [path] [pattern]`
    - `path` is the directory you want to move
    - `pattern` is a mask for files you want to move
- Client: `python client.py [remote url] [destination]`
    - `remote url` is the server location
    - `destination` is the directory you want files to be moved

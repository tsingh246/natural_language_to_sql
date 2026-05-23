import uvicorn


if __name__ == "__main__":
    uvicorn.run("src.nl_to_sql.api:app", host="127.0.0.1", port=8765)


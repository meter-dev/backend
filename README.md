# Meter

## TL;DR

```bash
cp meter.toml.example meter.toml
docker build . -t meter-web
docker run --rm -p 8000:8000 meter-web
# 然後就能在這邊看到 API 文件了，可以用 swagger 直接戳幾下試試
# http://127.0.0.1:8000/docs
# see more: https://fastapi.tiangolo.com/#interactive-api-docs-upgrade
```

## Dev

### Prerequisite

- poetry
- python 3.10

### Setup

```bash
cp meter.toml.example meter.toml
poetry install
poetry run uvicorn meter.main:app
# 一樣，文件在 http://127.0.0.1:8000/docs
```

> 可以加上 `--reload` 讓 FastAPI 會 hot reloading

### Config

我們使用 `meter.toml` 這個檔案來做 config，開啟 web server 前可以先把 `meter.toml.example` 複製一份出來。

### Project Architecture

- `meter/api` 放各種 API router，基本上一種 resource 一個檔案
- `meter/domain` 放無關 web API 的核心邏輯，但目前這邊直接把 ORM model 當 domain model 來用，耦合稍微嚴重
  - model 的設計是參考 SQLModel 文件的 [Multiple Models with FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/) 做的，可以快速的把 domain logic mapping 到 web API 層，如果有需要的話之後再拆吧
  - 無關特定 entity 的 domain logic 要不要寫成 class method 我沒有強烈的意見，但如果需要使用到 DB session 的我建議另外拆一個 `{Domain}Service`（Repository 就先算了吧），避免還需要注入 session 給 domain model

### TBD

- 測試如果懶得測太多或許就先在 API 這層做 e2e testing 即可，但時間許可我覺得還是從更裡面做 unit testing 更完整，不過因為拿 service 的邏輯多少依賴的 FastAPI 的 DI，所以會變得有點小麻煩
  - 這邊或許可以靠 FastAPI gen 出來的 OpenAPI doc 來 gen python client 比較輕鬆？待討論
- 我不確定目前 DB session 這樣用會不會產生無謂的 lock，或許有辦法的話簡單寫點 load testing 可以幫助我們評估有沒有優化效能的必要

## References

- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [SQLModel](https://sqlmodel.tiangolo.com/)

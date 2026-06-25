# infra/ — Docker & deployment

`docker-compose.yml` = postgres(pgvector/pgvector:pg16) + api + web · `docker-compose.ollama.yml` =
overlay เปิด Ollama เฉพาะเครื่องที่รัน local AI · `.env.example` = แม่แบบ env (ไม่มี secret จริง).

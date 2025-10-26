# Godot Docs and Forums Chatbot

This repo is the application base for RAG based Chatbot for the Godot Docs and Forums.

## Architecture Diagram and Application Demo

![Architecture](./assets/diagram.png)

https://github.com/user-attachments/assets/8dc453ce-b889-4cc6-a4fc-55742a0a445e

## API Docs

Below are the primary API endpoints exposed by the FastAPI application. Examples show JSON request bodies and typical JSON responses. Use the interactive docs at /docs when the server is running for live examples.

### Health

- GET `/` or `/health`

Response (200):

```json
{"status": "ok", "message": "RAG Chatbot API is running."}
```

### Query

- POST `/api/v1/query/`

Request body (application/json):

```json
{
  "query": "How do I create a Node in Godot?",
  "session_id": "session-1234",
  "state": {
    "model_name": "gpt-4o-mini",
    "category": "docs",
    "sub_category": "tutorials",
    "temperature": 0.7,
    "top_k": 5,
    "memory_service": "default"
  }
}
```

Typical response (200):

```json
{
  "response": {
    "answer": "You can create a Node in Godot by...",
    "sources": [
      {"content": "Creating nodes - docs.godotengine.org", "source": "https://docs.godotengine.org/..."}
    ]
  }
}
```

- POST `/api/v1/query/reddit`

Same request body as above, but include `reddit_username` and `relevance` in the `state` when appropriate. Typical response shape is the same as the main query endpoint.

### Sessions

- GET `/api/v1/session/?user_id={user_id}`

Response (200):

```json
{
  "sessions": [
    {"session_id": "session-1234", "user_id": "user_abc", "title": "My Chat", "time_created": "2025-10-24T12:00:00Z", "time_updated": "2025-10-24T12:00:00Z"}
  ]
}
```

- POST `/api/v1/session/`

Request body:

```json
{
  "user_id": "user_abc",
  "title": "Godot debugging"
}
```

Response (201/200):

```json
{
  "session_id": "session-1234",
  "user_id": "user_abc",
  "title": "Godot debugging"
}
```

- PUT `/api/v1/session/{session_id}`

Request body:

```json
{
  "title": "Renamed session"
}
```

Response (200):

```json
{
  "detail": "Session updated successfully",
  "session": {"session_id": "session-1234", "title": "Renamed session"}
}
```

- DELETE `/api/v1/session/{session_id}`

Response (200):

```json
{ "detail": "Session deleted" }
```

- DELETE `/api/v1/session/{user_id}` (delete all sessions for a user)

Response (200):

```json
{ "detail": "User sessions deleted" }
```

- GET `/api/v1/session/messages?session_id={session_id}`

Response (200):

```json
{
  "messages": [
    {
      "message_id": "msg-1",
      "session_id": "session-1234",
      "content": {"text": "Answer text..."},
      "sources": [{"content": "doc", "source": "..."}],
      "timestamp": "2025-10-24T12:34:56Z"
    }
  ]
}
```

- PUT `/api/v1/session/message/like` (query params)

Example: `/api/v1/session/message/like?message_id=msg-1&like='[like|dislike]'`

Response (200):

```json
{ "detail": "Message liked successfully" }
```

- PUT `/api/v1/session/message/feedback` (query params)

Example: `/api/v1/session/message/feedback?message_id=msg-1&feedback=typo&stars=4`

Response (200):

```json
{ "detail": "Feedback submitted successfully" }
```

### Sources

- POST `/api/v1/source/`

Request: (no body required; this endpoint lists sources)

Response (200):

```json
{
  "sources": [
    {"id": "source-1", "name": "Godot docs", "type": "website"}
  ]
}
```

- DELETE `/api/v1/source/{source_id}`

Response (200):

```json
{ "message": "Source {source_id} deleted successfully." }
```

---


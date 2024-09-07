# Initial architecture draft

```mermaid
sequenceDiagram
    participant frontend
    participant flask api
    participant analytics-service
    frontend->>flask api: POST request with all new nodes
    flask api->>analytics-service: new node coordinates
    analytics-service->>flask api: new node coordinates + flows
    flask api->>frontend: update frontend with nodes
    frontend->>frontend: update nodes
```

- We need to specify what we're doing. If we want to find places where a person should add a new bike stop, we need to really understand what are the key questions we have to answer to know how this will affect the graph flows. 
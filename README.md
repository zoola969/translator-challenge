to enable requests to google api you need to generate an API key https://cloud.google.com/docs/authentication/api-keys

## Known problems and solutions
The current implementation has several areas that require improvement to meet production standards. Here are the specific issues and proposed solutions:

#### Migration Management:
- **Current Issue**: Instead of using a proper migration system, the application creates collections if they do not exist at each startup.
- **Proposed Solution**: Replace this approach with a more robust migration tool, such as `mongodb-migrations`, to ensure schema changes are managed and tracked properly.

#### Google API Integration:
- **Current Issue**: The official Google library is used for making API requests, but only v2 API works with simple APIKey authentication. v3 requires a more complex authentication. Additionally, the library only provides an asynchronous interface for v3 API, forcing the use of a synchronous code in a `ThreadPoolExecutor` to avoid blocking the event loop.
- **Proposed Solution**: Transition to using the v3 API and its asynchronous client, or write a custom client using `httpx` or `aiohttp` for better integration and performance.

#### Database Connection Pooling:
- **Current Issue**: The current implementation does not utilize a connection pool for the database, which can lead to an excessive number of connections under high load.
- **Proposed Solution**: Implement a connection pool to manage database connections efficiently and handle high-load scenarios gracefully.

#### Unit Testing:
- **Current Issue**: There are no tests for the business logic due to time constraints, as considerable effort was spent on understanding the Google API.
- **Proposed Solution**: Develop comprehensive unit tests for the business logic to ensure reliability and maintainability of the codebase.


### How to run
1. create .env file in the root directory with the following content:
```dotenv
API_KEY=$your APIKey to google translate api
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=password
MONGO_HOST=translator-challenge-db
MONDO_PORT=27017
MONGO_DB_NAME=translates
MONGO_COLLECTION_NAME=words
```
2. run `docker compose up --build`
3. go to http://localhost:8000/docs
4. use `/system/words/populate` to generate some initial data

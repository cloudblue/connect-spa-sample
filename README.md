# Multi-Account Extension Example App

This is an example application that demonstrates how to obtain the required credentials to show embedded content from a multi-account extension. It's intended for learning purposes.

## Docker Setup

You can use Docker to run the app locally. We've included a `docker-compose.yml` file in the project root that makes it easy to get started.

### Prerequisites

- Docker: You need Docker installed on your local machine to run the application with Docker Compose. [Get Docker](https://www.docker.com/get-started)

- Docker Compose: Docker Compose is included with Docker Desktop on Windows and Mac. On Linux, you'll need to install it separately. [Get Docker Compose](https://docs.docker.com/compose/install/)

- Environment variables: The app requires certain environment variables to run correctly. You'll need to create a `.env` file in the project root with the following environment variables:

  ```
  TIER_ACCOUNT_ID=your_account_id
  API_HOST=your_api_host
  API_KEY=your_api_key
  ```
  
  You can refer to the `.env.dist` file in the project root for example values.

### Starting the App

To start the app, navigate to the project root in your terminal and run:

```bash
docker-compose up
```

This will start the backend app and the frontend development server.

### Developing the Frontend

To develop the frontend, you'll need to start the Vite server. First, log into the Docker container:

```bash
docker exec -it [container_id] /bin/bash
```

Then navigate to the `/frontend` folder and start the Vite server:

```bash
cd /frontend
npm run dev
```

The Vite server will start on `localhost:5173`.

### Running Tests

You can run the tests by executing the "test" service from the Docker Compose file. Run the following command:

```bash
docker-compose run test
```

### Linting

You can lint your Python and JavaScript code by running the "format" service:

```bash
docker-compose run format
```

This command will run `isort` and `black` for Python files, and `npm run lint` and `npm run format` for JavaScript files.

---


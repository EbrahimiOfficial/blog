# Dockerized Application

This project is containerized using Docker for easy deployment and local development. It requires PostgreSQL and Redis to be installed and running.

---

## Prerequisites

1. Install **Docker** and **Docker Compose**:
   - [Docker](https://www.docker.com/get-started)
   - [Docker Compose](https://docs.docker.com/compose/install/)

2. Install **PostgreSQL**:
   - On Ubuntu:
     ```bash
     sudo apt update
     sudo apt install postgresql
     ```
   - Ensure the database is running.

3. Install **Redis**:
   - On Ubuntu:
     ```bash
     sudo apt update
     sudo apt install redis
     ```
   - Ensure the Redis server is running:
     ```bash
     sudo systemctl start redis
     sudo systemctl enable redis
     ```

---

## Setup

1. **Prepare `.env` File:**
   Create a `.env` file in the project root and fill it with the necessary environment variables:

   ```env
    ALLOWED_HOSTS=
    SECRET_KEY=your_secret_key
    DEBUG=True
    DB_NAME=db_name
    DB_USER=db_user
    DB_PASSWORD=db_password
    DB_HOST=localhost
    DB_PORT=5432
   ```

2. **Build and Run:**
   Run the following command to build and start the services:

   ```bash
   docker-compose up --build
   ```

---

## Endpoints

### 1. **List Posts**

**Endpoint:**  
`GET api/blog/posts/`

**Description:**  
Retrieve a list of posts with their details, including whether the user has rated each post.

**Response Example:**
```json
[
        {
        "id": 1,
        "title": "How Bitcoin Works?",
        "average_rating": "3.000",
        "rating_count": 5,
        "user_rating": 3
    },
        {
        "id": 2,
        "title": "Ethereum Staking",
        "average_rating": "3.500",
        "rating_count": 50,
        "user_rating": 2
    }
]
```

---

### 2. **Rate a Post**

**Endpoint:**  
`POST api/blog/posts/ratings`

**Description:**  
Submit a rating for a specific post. If the post is already rated by the user, the rating will be updated.

**Request Example:**
```json
{
    "post_id": 1,
    "score": 5
}
```

**Response Example:**
```json
{
    "success": true
}
```

---


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

3. **Run Celery and Celery Beat:**
   Celery is used to handle asynchronous tasks, and Celery Beat schedules periodic tasks.

   - **Start Celery Worker Queues:**
     Run the following commands to start the Celery workers:

     ```bash
     celery -A bitpin worker -l info --concurrency=2
     ```

     ```bash
     celery -A bitpin worker -Q blog_queue -n worker -l info --concurrency=2
     ```

   - **Start Celery Beat:**
     Run the following command to start the Celery Beat scheduler:

     ```bash
     celery -A bitpin  beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
     ```


   **Tip:** It’s a good idea to use separate terminals or tmux sessions to monitor these services.

---

Let me know if you'd like further customization or additional clarifications.
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

# **Problem**

In scenarios where a large group of users intentionally manipulates the ratings of a post, short-term rating spikes can distort the overall rating. This leads to inaccurate representation of user sentiment and undermines the integrity of the rating system. 

---

## **Solution**

The solution involves:

- **Grouping Ratings by Hour**:
  - Ratings are grouped into hourly intervals.
  - An average rating is calculated for each hour.

- **Computing the Final Average**:
  - The final average rating is derived from the average of all hourly averages.
  - This prevents any single hour (with unusually high or low activity) from dominating the final score.

- **Assigning a Default Rating**:
  - If no ratings exist for the post, a default rating of `3` is assigned to ensure consistency.

- **Controlling Updates**:
  - Updates to the average rating are performed only when a specific flag (`should_update_average_rating`) is set. This avoids redundant recalculations and ensures efficient updates. 

---
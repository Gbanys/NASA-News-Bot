# NASA News Bot

## Environment Configuration

Before running the application, make sure to create a `.env` file for local development. This file should contain the necessary environment variables, which you should configure according to your own setup.

### Required Environment Variables

You must set the following environment variables:

- **MYSQL_ROOT_PASSWORD**: Your MySQL root password
- **OPENAI_API_KEY**: Your OpenAI API key# NASA News Bot

## Environment Configuration

Before running the application, make sure to create a `.env` file for local development. This file should contain the necessary environment variables, which you should configure according to your own setup.

### Required Environment Variables

You must set the following environment variables:

- **MYSQL_ROOT_PASSWORD**: Your MySQL root password
- **OPENAI_API_KEY**: Your OpenAI API key


### Default Environment Variables

Additionally, you should include these default environment variables in your `.env` file:

```plaintext
DB_USER=root
DB_HOSTNAME=nasa-news-bot_mysql_1
BACKEND_LOAD_BALANCER_URL=nasa-news-bot_backend_1:5000
BACKEND_WEBSOCKET_URL=localhost:5000

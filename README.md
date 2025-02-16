# NASA News Bot

## Environment Configuration

Before running the application, make sure to create a `.env` file for local development. This file should contain the necessary environment variables, which you should configure according to your own setup.

### Required Environment Variables

You must set the following environment variables:

- **MYSQL_ROOT_PASSWORD**: Your MySQL root password
- **OPENAI_API_KEY**: Your OpenAI API key


### Default Environment Variables

Additionally, you should include these default environment variables in your `.env` file:

DB_USER=root
DB_HOSTNAME=mysql
BACKEND_LOAD_BALANCER_URL=nasa-news-bot-backend-1:5000
BACKEND_WEBSOCKET_URL=localhost:5000

##Starting the application

Firstly, ensure that Docker and docker compose are installed. For this to work docker compose v2 should be installed.
(Optional) Then run the below command in the terminal:

```make build```

Once all the images have been built you can run all the containers using the below command. Alternatively, you can just run
the below command without running `make build`. The command below should build images if they haven't been built already and then run the containers.

```make start```

Finally, once all containers are running, ensure that the qdrant vectorstore is populated with embeddings.
You may choose to use the snapshot file that is provided and then run this command:

```make restore-snapshot```

IN PRODUCTION:

Create a storage class by getting the FileSystemID from Amazon EFS. The EFS storage will be mounted to the pods
in the Kubernetes cluster. The file for creating the storage class object is called "efs-storage-class.yaml"

Deploy a persistent volume claim object which is defined in a template yaml file called "qdrant-snapshot-restoration-pvc.yaml"

Use this command to restore to MySQL database:

```cat schema.sql | kubectl exec -i mysql-primary-0 -- mysql -u root -p$MYSQL_ROOT_PASSWORD```

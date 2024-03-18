# SFTP File Synchronization with Apache Airflow

## How to Spin Up the Environment
1. **Prerequisites:**
   - Ensure you have the latest version of Docker installed.
   - If using Windows, a Linux VM is required for running Docker containers.

2. **Starting the Project:**
   - Run the `start_project.sh` script to set up the environment.


## Assumptions Made
1. **Server Setup:**
- It is assumed that both the source and target servers have been set up and configured properly with the required SFTP user accounts.

2. **Airflow Connections Management:**
- The assumption is made that Airflow's UI will be used for managing connections to the SFTP servers.

3. **Batch Processing:**
- The project assumes batch processing of files rather than real-time streaming.

## Decisions Taken
1. **Scalability:**
- Celery is utilized to provide parallelism to the workers, allowing for scalability in processing multiple files concurrently.

2. **Extensibility:**
- Airflow is chosen as the middle-man for file synchronization, allowing for easy integration of additional transformation layers. 
- It's decided that Airflow server will not be used as the target server, enabling the possibility of adding multiple layers of transformation on the Airflow machine.

3. **Abstraction:**
- To cater to the requirement of interchangeable source and target servers, the Strategy pattern is employed to increase the level of abstraction. This allows for flexibility in changing underlying Class.

## Trade-offs
1. **Fixed Configuration:**
- The configuration is hardcoded, which may not be suitable for long-term maintenance. Future improvements could involve using a database for storing connections, environment variables, etc.
2. **Performance vs Complexity:**
- Using Airflow for file synchronization adds complexity to the system but provides scalability and extensibility. There's a trade-off between system complexity and performance optimization that needs to be considered.

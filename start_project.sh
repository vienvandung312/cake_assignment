# Build the sftp image if not exists
docker build -f Dockerfile_sftp_server -t sftp-server .

# Get airflow ready
docker compose -f airflow-docker-compose.yml --profile flower up -d

# Get sftp source ready
docker run -itd --name sftp-source -h source_sftp --network cake_assignment_default sftp-server bash
docker exec sftp-source service ssh start

# Get sftp target ready
docker run -itd --name sftp-target -h target_sftp --network cake_assignment_default sftp-server bash
docker exec sftp-target service ssh start    
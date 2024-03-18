from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.sftp.sensors.sftp import SFTPSensor
from airflow.providers.sftp.hooks.sftp import SFTPHook
import logging
from abc import ABC,abstractmethod

class FileTransferHookInterface(ABC):
    @abstractmethod
    def list(self, path):
        pass

    @abstractmethod
    def get(self, remote_full_path, local_full_path):
        pass

    @abstractmethod
    def put(self, local_full_path, remote_full_path):
        pass

class SFTPHookStrategy(FileTransferHookInterface):
    def __init__(self, sftp_conn_id):
        self.sftp_conn_id = sftp_conn_id
        self.hook = SFTPHook(ssh_conn_id=self.sftp_conn_id)
    
    def list(self,path):
        return self.hook.list_directory(path)
    
    def get(self, remote_full_path, local_full_path):
        return self.hook.retrieve_file(remote_full_path,local_full_path)

    def put(self, remote_full_path, local_full_path):
        return self.hook.store_file(remote_full_path, local_full_path)

class OtherObjectStorageHookStrategy(FileTransferHookInterface):
    def __init__(self, sftp_conn_id):
        # How the Object Storage Instantiates
        pass    
    def list(self,path):
        # How the Object Storage return the list of files
        pass
    
    def get(self, remote_full_path, local_full_path):
        # How the Object Storage download files
        pass
    
    def put(self, remote_full_path, local_full_path):
        # How the Object Storage upload files
        pass


def transform_files(**kwargs):
    print("Transforming files...")

def sync_files(source_hook, dest_hook, **kwargs):
    # List files on the source server
    source_files = source_hook.list('/home/airflow/filesystem/')
    
    # List files on the destination server
    dest_files = dest_hook.list('/home/airflow/filesystem/')
    
    # Identify new files
    new_files = [file for file in source_files if file not in dest_files]
    
    # Sync new files to destination server
    for file in new_files:
        source_hook.get(
            remote_full_path = f'/home/airflow/filesystem/{file}', 
            local_full_path = f'/tmp/{file}'
        )
        
        transform_files()
        
        dest_hook.put(
            local_full_path = f'/tmp/{file}', 
            remote_full_path = f'/home/airflow/filesystem/{file}'
        )
        
        logging.info(f'Syncing file {file}...')
    
    return f'Synced {len(new_files)} new files.'

# Define DAG parameters
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 15),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'sftp_sync',
    default_args=default_args,
    description='Monitor source SFTP server for new files, transform, and sync to destination SFTP server',
    schedule_interval=None,
    catchup=False
)

# Define tasks
sftp_sensor_task = SFTPSensor(
    task_id='sftp_sensor_task',
    path='/home/airflow/filesystem/',
    file_pattern='*',
    sftp_conn_id='source_sftp',
    timeout=60*5,
    poke_interval=30,
    dag=dag,
)

sync_files_task = PythonOperator(
    task_id='sync_files_task',
    python_callable=sync_files,
    op_kwargs={
        'source_hook': SFTPHookStrategy(sftp_conn_id='source_sftp'),
        'dest_hook': SFTPHookStrategy(sftp_conn_id='target_sftp')
    },
    provide_context=True,
    dag=dag,
)

sftp_sensor_task >> sync_files_task
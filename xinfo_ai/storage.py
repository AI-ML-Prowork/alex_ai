import paramiko
from django.http import JsonResponse
from .settings import *
from icecream import ic


VPS_HOST = os.getenv("VPS_HOST")
VPS_USER = os.getenv("VPS_USER")
VPS_PASSWORD = os.getenv("VPS_PASSWORD")



def list_vps_documents():
    """Connects to VPS via SSH and lists files in the Documents folder."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD)

        sftp = ssh.open_sftp()
        files = sftp.listdir(DOCUMENTS_PATH)

        sftp.close()
        ssh.close()

        return files
    except Exception as e:
        return str(e)
    


def ssh_connect():
    """Establishes an SSH connection to the VPS."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD)
    ic(ssh)
    return ssh


def ensure_remote_dir(sftp, remote_directory):
    """
    Recursively ensures that a remote directory exists.
    """
    dirs = remote_directory.split('/')
    path = ''
    for dir in dirs:
        path = f"{path}/{dir}" if path else dir
        ic(path)
        try:
            sftp.stat(path)
            ic(sftp.stat(path))
        except FileNotFoundError:
            sftp.mkdir(path)
            ic(sftp.mkdir(path))

def upload_file_to_vps(file, file_name, folder=None):
    """
    Uploads a file to the VPS 'Documents' folder and returns the public URL.
    """
    paramiko.util.log_to_file("paramiko_debug.log")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD)

        sftp = ssh.open_sftp()
        remote_folder = f"{DOCUMENTS_PATH}/{folder}" if folder else DOCUMENTS_PATH
        ic(remote_folder)

        ensure_remote_dir(sftp, remote_folder)

        remote_file_path = f"{remote_folder}/{file_name}"
        ic(remote_file_path)

        with sftp.file(remote_file_path, "wb") as remote_file:
            for chunk in file.chunks():
                remote_file.write(chunk)

        sftp.close()
        ssh.close()

        base_url = "https://alexai.store/media/"
        public_url = f"{base_url}{folder}/{file_name}" if folder else f"{base_url}{file_name}"
        ic(public_url)
        return public_url

    except Exception as e:
        return str(e)

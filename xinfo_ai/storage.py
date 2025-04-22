# import paramiko
# from django.http import JsonResponse
# from .settings import *



# def list_vps_documents():
#     """Connects to VPS via SSH and lists files in the Documents folder."""
#     try:
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD)

#         sftp = ssh.open_sftp()
#         files = sftp.listdir(DOCUMENTS_PATH)

#         sftp.close()
#         ssh.close()

#         return files
#     except Exception as e:
#         return str(e)
    


# def ssh_connect():
#     """Establishes an SSH connection to the VPS."""
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD)
#     return ssh



# def upload_file_to_vps(file, file_name, folder=None):
#     """
#     Uploads a file to the VPS 'Documents' folder and returns the public URL.

#     Returns
#     -------
#     str
#         The full public URL of the uploaded file.
#     """
#     paramiko.util.log_to_file("paramiko_debug.log")  ##### Logs SSH activity for the paramiko library......

#     try:
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD)
#         sftp = ssh.open_sftp()
#         remote_folder = f"{DOCUMENTS_PATH}/{folder}" if folder else DOCUMENTS_PATH
#         remote_file_path = f"{remote_folder}/{file_name}"
#         try:
#             sftp.stat(remote_folder)
#         except FileNotFoundError:
#             sftp.mkdir(remote_folder)

#         with sftp.file(remote_file_path, "wb") as remote_file:
#             for chunk in file.chunks(): 
#                 remote_file.write(chunk)
#         sftp.close()
#         ssh.close()
#         base_url = "https://discombglobal.com/media/" 
#         public_url = f"{base_url}{folder}/{file_name}" if folder else f"{base_url}{file_name}"
#         return public_url
#     except Exception as e:
#         return str(e)


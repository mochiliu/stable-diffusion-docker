import json
from gsheets import sheet_to_dataframe, dataframe_to_sheet, get_last_updated_time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from apiclient.http import MediaFileUpload
import mimetypes
import subprocess
import os
import pandas as pd
from datetime import timedelta, datetime, date
import pytz
import time
import papermill as pm
import sendgrid
from sendgrid.helpers.mail import *


ROOT_FOLDER = '1mh-hDd6bGgdcw1oxRcnPNcNrGJvgaHfi' #shared folder on my personal space
JOBS_SHEET = '18fVqjzsQx3twrO6j688p-S3BCtkUqgOAURQUcKBjK-g'
SCOPES = ['https://www.googleapis.com/auth/drive']
KERNEL_NAME = 'python3'
LOG_TIME_FORMATTING = '%Y-%m-%d %H:%M:%S %Z'
PROTECTED_FILES = ['service_loop.ipynb','stable_diffusion_animate_youtube.ipynb','stable_diffusion_animate_youtube_papermill.ipynb','requirements.txt']
UPLOAD_EXTENSIONS = ['.mp4','.txt']
DELETE_EXTENSIONS = ['.mp4','.txt']
CORE_COLUMNS = ['Timestamp', 'YouTube_URL', 'model_name', 'constant_text']
LOOP_TIME_S = 300

gservice_credentials = json.load(open('/workspace/mnt/private/stablediffusion-364601-d8d8ab40fcd5.json'))
creds = service_account.Credentials.from_service_account_info(
        gservice_credentials, scopes=SCOPES)
os.environ["GOOGLE_SERVICE_ACCT_JSON"] = json.dumps(gservice_credentials)
send_grid = json.load(open('/workspace/mnt/private/sendgrid.json'))

status_timestamps = []
status_messages = []
def update_status(status_message, write_to_sheet=True):
    #updates the status sheet
    status_timestamp = datetime.now(pytz.utc).strftime(LOG_TIME_FORMATTING)
    print(f'{status_timestamp}: {status_message}')
    if len(status_messages)>0 and status_messages[-1].startswith('checking'):
        # the last update was a check operation, pop the last items
        status_timestamps.pop()
        status_messages.pop()    
    status_timestamps.append(status_timestamp)
    status_messages.append(status_message)
    df_status = pd.DataFrame({'time': status_timestamps,'message':status_messages}) 
    if write_to_sheet:
        dataframe_to_sheet(df_status, JOBS_SHEET, 'Status')
        
def create_folder_gdrive(service, folder_name, parent_folder_id):
    #make a new folder on google drive
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    file = service.files().create(body=file_metadata,
                                        fields='id').execute()
    new_folder_id = file.get('id')
    return new_folder_id

def upload_file_gdrive(service, file_name, parent_folder_id):
    #make a new pdf file 
    file_metadata = {
        'name': file_name,
        'parents': [parent_folder_id]
    }
    mimetype = mimetypes.MimeTypes().guess_type(file_name)[0]
    media = MediaFileUpload(file_name,
                            mimetype=mimetype,
                            resumable=True)
    file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    output_file_id = file.get('id')
    return output_file_id

def scan_for_files(extensions:list)->list:
    '''selects files with the extensions from the current directory'''
    files_with_extensions = []
    for file in os.listdir("./"):
        for extension in extensions:
            if file.endswith(extension):
                files_with_extensions.append(file)
    return files_with_extensions

def remove_files(files):
    for file in files:
        if not file in PROTECTED_FILES:
            os.remove(file)
            print(f'deleting {file}')
            
def send_email(to_email, link, title):
    if not "@" in to_email:
        return
    try:
        sg = sendgrid.SendGridAPIClient(api_key=send_grid['api_key'])
        from_email = Email(send_grid['from_email'])
        to_email = To(to_email)
        subject = f"your rendering of {title} is ready"
        content = Content("text/plain", link)
        mail = Mail(from_email, to_email, subject, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

while True: # loop forever
    try:
        loop_start_time = time.time()
        #check the gsheet if it has been edited in the last LOOPTIME seconds
        #allow the user to keep editing without starting any jobs
        time_since_last_update = datetime.now(pytz.utc) - get_last_updated_time(JOBS_SHEET)

        update_status(f'checking for new jobs')

        #check the gsheet for jobs
        df_todo_orig = sheet_to_dataframe(JOBS_SHEET, 'ToDo')
        df_completed_orig = sheet_to_dataframe(JOBS_SHEET, 'Completed')

        df_todo_orig = df_todo_orig[df_todo_orig['YouTube_URL'].str.strip().astype(bool)]
        # drop duplicated timestamps so that it is unique
        df_todo_orig = df_todo_orig.set_index('Timestamp', drop=True)
        df_todo_orig = df_todo_orig[~df_todo_orig.index.duplicated(keep='first')]
        df_todo_orig = df_todo_orig.reset_index()
        #determine which items are still todo using the timestamps as key
        todo_timestamps = set(df_todo_orig.get('Timestamp',[])).difference(set(df_completed_orig.get('Timestamp',[])))
        df_todo = df_todo_orig.loc[df_todo_orig['Timestamp'].isin(todo_timestamps)]

        created_at_timestamps = []
        gdrive_link = []
        titles = []
        for idx, job_row in df_todo.iterrows():
            # loop over the videos to make, run papermill
            try:
                timestamp_str = datetime.now(pytz.utc).strftime(LOG_TIME_FORMATTING)
                created_at_timestamps.append(timestamp_str)

                output_file = job_row.YouTube_URL.split('=')[-1]
                output_file_ipynb = 'out.ipynb'
                update_status(f'started job {job_row.YouTube_URL}')
                #clean working directory
                remove_files(scan_for_files(DELETE_EXTENSIONS))

                #use papermill to run the analysis
                nb = pm.execute_notebook(
                   'stable_diffusion_animate_youtube_papermill.ipynb',
                    output_file_ipynb,
                    kernel_name=KERNEL_NAME,
                    parameters=dict(YOUTUBE_URL=job_row.YouTube_URL, 
                                    MODEL_NAME = job_row.model_name,
                                    CONSTANT_TEXT=" " + job_row.constant_text,)
                )
                
                try:
                    with open('title') as f:
                        output_file = f.read() #replace file with the title of the music video if available
                except Exception as e:
                    pass

                #set up gdrive folder
                service = build('drive', 'v3', credentials=creds)
                new_folder_id = create_folder_gdrive(service, output_file, ROOT_FOLDER)

                #scrape for other relevant files in local directory like
                #contact sheet and animation videos
                files_to_upload = scan_for_files(UPLOAD_EXTENSIONS)
                file_ids = []
                for file_to_upload in files_to_upload:
                    if not file_to_upload in PROTECTED_FILES:
                        file_ids.append(upload_file_gdrive(service, file_to_upload, new_folder_id))
                
                link = f'https://drive.google.com/drive/folders/{new_folder_id}'
                #send notification email
                send_email(job_row.email, link, f"{output_file}: {job_row.comment}")
                
                #log
                gdrive_link.append(link)
                titles.append(output_file)
                status_txt = f'finshed job {output_file}'
            except Exception as e:
                gdrive_link.append(str(e))
                status_txt = str(e)
                titles.append('')
            update_status(status_txt)

        #update the completed sheet
        df_just_finished = df_todo.copy()
        df_just_finished['created_at'] = created_at_timestamps
        df_just_finished['link'] = gdrive_link
        df_just_finished['title'] = titles

        df_completed = pd.concat([df_just_finished,df_completed_orig])
        dataframe_to_sheet(df_completed, JOBS_SHEET, 'Completed')

    except Exception as e:
        print(e)

    sleep_time = LOOP_TIME_S - (time.time() - loop_start_time)
    if sleep_time > 0:
        time.sleep(sleep_time)       # sleep accordingly so the full iteration takes a fixed time


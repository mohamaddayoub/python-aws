import requests
import boto3
import smtplib
import os
import paramiko
import time
import schedule

EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
PASSPHRASE_SERVER = os.environ.get('PASSPHRASE_SERVER')


def restart_server_and_container():
    print('Restarting Server...')
    ec2_client = boto3.client('ec2')
    instance_id = 'i-0571db2a30911c345'
    response = ec2_client.reboot_instances(InstanceIds=[instance_id])
    print("The server is rebooted. SUCCESS!")

    # restart the application
    while True:
        instance_status = ec2_client.describe_instance_status(InstanceIds=[instance_id])
        if instance_status['InstanceStatuses'][0]['InstanceState']['Name'] == 'running':
            time.sleep(20)
            restart_container()
            print("The Container is restarted. SUCCESS!!")
            break


def restart_container():
    print('Restarting Container...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='18.216.102.73', username='admin', key_filename='/Users/md/.ssh/jenkins-server.pem',
                passphrase=PASSPHRASE_SERVER)
    stdin, stdout, stderr = ssh.exec_command('docker start 567b55f3e721')
    print(stdout.readline())
    ssh.close()


def send_notification(email_msg):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        message = f"Subject: SITE DOWN\n{email_msg}"
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, message)


def monitor_server():
    try:
        response = requests.get('http://ec2-18-216-102-73.us-east-2.compute.amazonaws.com:8080')
        if response.status_code == 200:
            print('The Website is running successfully!')
        else:
            print('The Website is down. Fix it!!')
            print('Sending Email........')
            msg = f"The Website returned{response.status_code}. Please fix it!"
            send_notification(msg)
            restart_container()

    except Exception as ex:
        print(f"Connection Error happened{ex}")
        msg = f"Application not accessible at all. Please fix it!"
        send_notification(msg)

        # restart the server and container
        restart_server_and_container()


schedule.every(5).minutes.do(monitor_server)
while True:
    schedule.run_pending()




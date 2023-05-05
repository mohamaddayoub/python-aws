import boto3
import schedule

ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')


def list_of_instances_status():
    statuses = ec2_client.describe_instance_status(
        IncludeAllInstances=True
    )
    for status in statuses['InstanceStatuses']:
        inst_id = status['InstanceId']
        inst_state = status['InstanceState']['Name']
        inst_status = status['InstanceStatus']['Status']
        system_status = status['SystemStatus']['Status']
        print(f"Instance {inst_id} is {inst_state} with {inst_status}/{system_status}")
    print("#################################\n")


schedule.every(5).seconds.do(list_of_instances_status)

while True:
    schedule.run_pending()

import boto3

instance_ohio = boto3.client('ec2')

reservations = instance_ohio.describe_instances()['Reservations']

instance_ids_ohio = []

for res in reservations:
    instances = res['Instances']
    for inst in instances:
        instance_ids_ohio.append(inst['InstanceId'])

response = instance_ohio.create_tags(
    Resources=instance_ids_ohio,
    Tags=[
        {
            'Key': 'environment',
            'Value': 'test'
        },
    ]
)

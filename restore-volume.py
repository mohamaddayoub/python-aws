import boto3
from operator import itemgetter

ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')

instance_id = 'i-0b8512e4dc94b925d'

# get the volume that attached to that instance
volumes = ec2_client.describe_volumes(
    Filters=[
        {
            'Name': 'attachment.instance-id',
            'Values': [
                instance_id
            ]
        },
    ]
)
instance_volume = volumes['Volumes'][0]
print(f"Volume ID: {instance_volume['VolumeId']} \n##################")

# get the latest snapshot from that volume
snapshots = ec2_client.describe_snapshots(
    Filters=[
            {
                'Name': 'volume-id',
                'Values': [
                    instance_volume['VolumeId']
                ]
            },
        ],
)

latest_snapshots = sorted(snapshots['Snapshots'], key=itemgetter('StartTime'), reverse=True)[0]
print(f"Snapshot ID: {latest_snapshots['SnapshotId']} \n##################")

# create a volume form tha latest snapshot
new_volume = ec2_client.create_volume(
    AvailabilityZone="us-east-2c",
    SnapshotId=latest_snapshots['SnapshotId'],
    TagSpecifications=[
        {
            'ResourceType': 'volume',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'prod'
                }
            ]
        }
    ]
)
# attach the volume after to be at available state
while True:
    vol = ec2_resource.Volume(new_volume['VolumeId'])
    print(vol.state)
    if vol.state == 'available':
        ec2_client.attach_volume(
            Device='/dev/xvdb',
            InstanceId=instance_id,
            VolumeId=new_volume['VolumeId']
        )
    break

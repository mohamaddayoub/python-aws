import boto3
import schedule

ec2_client = boto3.client('ec2')

volumes = ec2_client.describe_volumes(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    'prod'
                ]
            }
        ]
    )

for volume in volumes['Volumes']:
    new_snapshots = ec2_client.create_snapshot(
            VolumeId=volume['VolumeId']
    )
    print(f"Volume ID: {volume['VolumeId']} Snapshot ID: {new_snapshots['SnapshotId']}\n")

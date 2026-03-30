import boto3
from datetime import datetime, timedelta

ec2 = boto3.client('ec2')

DAYS_IDLE = 7

def get_old_instances():
    instances = ec2.describe_instances()
    old_instances = []

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            launch_time = instance['LaunchTime'].replace(tzinfo=None)
            if datetime.utcnow() - launch_time > timedelta(days=DAYS_IDLE):
                old_instances.append(instance['InstanceId'])

    return old_instances

def stop_instances(instance_ids):
    if instance_ids:
        print(f"Stopping instances: {instance_ids}")
        ec2.stop_instances(InstanceIds=instance_ids)

def find_unused_volumes():
    volumes = ec2.describe_volumes()
    unused = [v['VolumeId'] for v in volumes['Volumes'] if v['State'] == 'available']
    return unused

def find_unassociated_eips():
    addresses = ec2.describe_addresses()
    return [eip['AllocationId'] for eip in addresses['Addresses'] if 'InstanceId' not in eip]

def main():
    print("Running Idle Resource Cleanup...")

    old_instances = get_old_instances()
    stop_instances(old_instances)

    unused_volumes = find_unused_volumes()
    print(f"Unused Volumes: {unused_volumes}")

    unused_eips = find_unassociated_eips()
    print(f"Unassociated EIPs: {unused_eips}")

if __name__ == "__main__":
    main()
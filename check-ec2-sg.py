import boto3
import json

client = boto3.client('ec2')

sg_rules = client.describe_security_group_rules().get('SecurityGroupRules')

sg_list = [] # will possibly contain duplicate values

for item in sg_rules:
    sg = item.get('GroupId')
    sg_list.append(sg)
sg_id_list = set(sg_list) # Get a list of unique values

sg_with_ssh_open_to_world = []

for item in sg_rules:
    sg = item.get('GroupId')
    if item.get('FromPort')==22 and item.get('CidrIpv4')=='0.0.0.0/0':
        sg_with_ssh_open_to_world.append(sg)

resource = client.describe_instances().get('Reservations')  # Here, we filter to get only the list of the key "Reservation"

ec2_instances = [] # Here, we will filter the reservation list and get the sub-list with key "Instances"

for item in resource:
    instance = item.get('Instances')
    ec2_instances.append(instance)

running_ec2_instances = []

for item1 in ec2_instances:
    for item2 in item1:
        v = item2.get('State').get('Name')
        if v not in ('running', 'stopped'):
            pass
        else:
            running_ec2_instances.append(item2)

running_ec2_instances_id = [] # all ec2 instance id with security ssh rule open to the world
count = 0 # To enable us count the number of instances that will be terminated

for item1 in running_ec2_instances:  # we loop into the securityGroups list to get the security group id
    id = item1.get('InstanceId')
    sg = item1.get('SecurityGroups')
    for item2 in sg:
        sg_id = item2.get('GroupId') # we loop into the securityGroups list to get the security group id
        if sg_id in sg_with_ssh_open_to_world:
            running_ec2_instances_id.append(id)
            count = count+1
running_ec2_instances_id = list(set(running_ec2_instances_id)) # remove all duplicates using the "set" function, then converting it to a list

try:
    response = client.terminate_instances(InstanceIds = running_ec2_instances_id)
    print(count, "ec2 instances have been successfully terminated.")
except:
    print('There is no running ec2 intance with security group ssh rule opened to the world')
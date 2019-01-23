import boto3

session = boto3.Session(profile_name='eclipsedev')
ec2 = session.resource('ec2')
asc = boto3.client('autoscaling')

img = ec2.Image('ami-0080e4c5bc078760e')
instances = ec2.create_instances(ImageId=img.id, InstanceType='t2.micro', MaxCount=1, MinCount=1, KeyName='python-automation-kp', SecurityGroups=['pydev-sg'])
inst = instances[0]
inst.wait_until_running()
print(inst.public_ip_address)
print(inst.public_dns_name)
print(inst.id)


# response = asc.create_auto_scaling_group(
#     AutoScalingGroupName='autonotif-asg',
#     InstanceId=inst.id,
#     MinSize=1,
#     MaxSize=4,
#     DesiredCapacity=1,
#     DefaultCooldown=15
# )
#
# print(response)

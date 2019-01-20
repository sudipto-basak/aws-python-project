# coding: utf-8

import boto3
session = boto3.Session(profile_name='pythondev')
ec2 = session.resource('ec2')
sg = ec2.create_security_group(Description='python dev security group', GroupName='pydev-sg')
sg.id
ec2.create_tags(Resources=[sg.id], Tags={'Key': 'Name', 'Value': 'pydev-sg'})
ec2.create_tags(Resources=[sg.id], Tags=[{'Key': 'Name', 'Value': 'pydev-sg'}])
ami_name = ec2.Image('ami-035be7bafff33b6b6 ').name
ami_name = ec2.Image('ami-035be7bafff33b6b6').name
ami_name
img = ec2.Image.filter(Owners=['amazon'])
img = ec2.Image.filters(Owners=['amazon'])
img = ec2.images.filters(Owners=['amazon'])
img = ec2.images.filter(Owners=['amazon'])
img
img = ec2.images.filter(Owners=['amazon'], Filters=[{'Name': 'name', 'Values' : [ami_name] }])
img.id
img
for i in img:
    print(i)
    
img.name
list(img)
list(img).id
img = ec2.images.filter(Owners=['amazon'], Filters=[{'Name': 'name', 'Values' : [ami_name] }])
del img
ec2.images.filter(Owners=['amazon'], Filters=[{'Name': 'name', 'Values' : [ami_name] }])
list(ec2.images.filter(Owners=['amazon'], Filters=[{'Name': 'name', 'Values' : [ami_name] }]))
img = ec2.Image(id='ami-035be7bafff33b6b6')
img.id
img.name
ec2.create_instances(ImageId=img.id, InstanceType='t2.micro', MaxCount=1, MinCount=1, KeyName='pythondev-mac')
ec2.create_instances(ImageId=img.id, InstanceType='t2.micro', MaxCount=1, MinCount=1, KeyName='pythondev_mac')
inst = ec2.Instance(id='i-0acec51c15be22a72')
inst.public_dns_name
sg
sg.authorize_egress(IpPermissions=[{ 'FromPort': 22, 'ToPort': 22, 'IpRanges' : [{ 'CidrIp' : '0.0.0.0/0' }]}])
sg.authorize_egress(IpPermissions=[{ 'FromPort': 22, 'ToPort': 22, 'IpProtocol': 'tcp', 'IpRanges' : [{ 'CidrIp' : '0.0.0.0/0' }]}])
inst.public_dns_name
sg.authorize_ingress(IpPermissions=[{ 'FromPort': 22, 'ToPort': 22, 'IpRanges' : [{ 'CidrIp' : '0.0.0.0/0' }]}])
sg.authorize_ingress(IpPermissions=[{ 'FromPort': 22, 'ToPort': 22, 'IpProtocol': 'tcp', 'IpRanges' : [{ 'CidrIp' : '0.0.0.0/0' }]}])
sg.id
inst.modify_attribute(Groups=[sg.id])
sg.authorize_ingress(IpPermissions=[{ 'FromPort': 80, 'ToPort': 80, 'IpProtocol': 'tcp', 'IpRanges' : [{ 'CidrIp' : '0.0.0.0/0' }]}])
inst.public_dns_name
get_ipython().run_line_magic('history', '')

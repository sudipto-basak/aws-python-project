import boto3

session = boto3.Session(profile_name='eclipsedev')
asc = boto3.client('autoscaling')

asc.execute_policy(AutoScalingGroupName='autonotif-asg', PolicyName='scale-up')
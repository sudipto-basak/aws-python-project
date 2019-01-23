import os

def post_to_slack(event, context):
    slack_webhook_url =  os.environ['SLACK_WEBHOOK_URL']
    print("Slack URL :- {}".format(slack_webhook_url))

    print(event)

    return


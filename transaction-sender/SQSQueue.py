import boto3
sqs_client = boto3.client('sqs')

class SQSQueue:
    def __init__(self, url):

        self.url = url

    def get_message(self):
        response = sqs_client.receive_message(
        QueueUrl=self.url,
        AttributeNames=[]
        )
        message = response['Messages'][0]
        reciept_handle = message['ReceiptHandle']


        sqs_client.delete_message(
            QueueUrl=self.url,
            ReceiptHandle=reciept_handle
        )
        return message

    def push_message(self, message):
        return sqs_client.send_message(
            QueueUrl=self.url,
            DelaySeconds=0,
            MessageBody=message)


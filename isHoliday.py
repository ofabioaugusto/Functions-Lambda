import json
from datetime import date
import boto3
import os

clientdb = boto3.client('dynamodb')

def lambda_handler(event, context):
    
    today = str(date.today())

    table_name = os.environ['TABLE_NAME']

    data = clientdb.query(TableName=table_name, ExpressionAttributeValues={':varString': {'S':str(today),},}, KeyConditionExpression='holiday = :varString',)
    
    if len(data['Items']) > 0:
        holiday_date = data['Items'][0]['holiday']['S']
        holiday_description = data['Items'][0]['description']['S']
        holiday_enable = data['Items'][0]['enable']['BOOL']
        
        if holiday_date == today and holiday_enable == True:
            return {
                'statusCode': 200,
                'isHoliday': True,
                'description': holiday_description
            }
            
    return {
        'statusCode': 200,
        'isHoliday': False,
        'description': ''
    }

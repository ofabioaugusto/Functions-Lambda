import json
import boto3
import os

client_db = boto3.client('dynamodb')
client_profile = boto3.client('customer-profiles')

def lambda_handler(event, context):
    eventParameters = event['Details']['Parameters']
    CustomerId = eventParameters.get('CustomerId')
    CustomerNumber = eventParameters.get('CustomerNumber')
    
    table_name = os.environ['TABLE_NAME']
    domain_name = os.environ['DOMAIN_NAME']
    
    if CustomerId == None or CustomerNumber == None:
        return {
            'statusCode': 500,
            'lambdaResult': 'Parametros faltantes.'
        }
    
    response = client_db.query(TableName=table_name, ExpressionAttributeValues={":varString": {"S":str(CustomerId),},}, KeyConditionExpression="CustomerId = :varString",)

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        items = response.get("Items")
        if items != None:
            if len(items) > 0:
                Address = items[0]['Address']['S']
                BirthDate = items[0]['BirthDate']['S']
                CPF = items[0]['CPF']['S']
                Email = items[0]['Email']['S']
                FirstName = items[0]['FirstName']['S']
                LastName = items[0]['LastName']['S']
            else:
                return {
                    'statusCode': 500,
                    'lambdaResult': 'CustomerId not found'
                }
    
    profile_id = None
    account_number = None
    
    response = client_profile.search_profiles(DomainName=domain_name, KeyName='_phone', Values=[CustomerNumber])
    
    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        items = response.get("Items")
        if items != None:
            if len(items) > 0:
                profile_id = items[0].get("ProfileId")
                account_number = items[0].get("AccountNumber")
                if account_number != CPF:
                    response = client_profile.update_profile(
                        DomainName=domain_name,
                        ProfileId=profile_id,
                        PhoneNumber=CustomerNumber,
                        AccountNumber=CPF,
                        AdditionalInformation=CPF,
                        FirstName=FirstName,
                        LastName=LastName,
                        BirthDate=BirthDate,
                        EmailAddress=Email,
                        Address={'Address1': Address},
                        MailingAddress={'Address1': Address},
                        BillingAddress={'Address1': Address}
                    )
                    message="Perfil atualizado."
                else:
                    message="Perfil identificado."
            else:
                response = client_profile.create_profile(
                    DomainName=domain_name,
                    PhoneNumber=CustomerNumber,
                    AccountNumber=CPF,
                    AdditionalInformation=CPF,
                    FirstName=FirstName,
                    LastName=LastName,
                    BirthDate=BirthDate,
                    EmailAddress=Email,
                    Address={'Address1': Address},
                    MailingAddress={'Address1': Address},
                    BillingAddress={'Address1': Address}
                )
                message="Perfil criado."

    return {
        'id': CustomerId,
        'cpf': CPF,
        'first_name': FirstName,
        'last_name': LastName,
        'address': Address,
        'birth_date': BirthDate,
        'email': Email,
        'statusCode': 200,
        'lambdaResult': message
    }

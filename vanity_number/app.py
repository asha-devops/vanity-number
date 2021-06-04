import phonenumbers
import boto3
import os
import time
import json
from datetime import datetime
from wordify import *


if os.getenv("AWS_SAM_LOCAL"):
    db_name = boto3.resource(
        'dynamodb',
        endpoint_url="http://localhost:8000/"
    ).Table("customer-details")
else:
    db_name = boto3.resource('dynamodb').Table('customer-details')

def parse_contactnumber(contact_number):
    try:
        parsed_contactnumber = phonenumbers.parse(contact_number, None)
        if phonenumbers.is_valid_number(parsed_contactnumber):
            return {
                "country_code": parsed_contactnumber.country_code,
                "contact_number": parsed_contactnumber.national_number
            }
        else:
            return None
    except:
        print("contact number invalid, valid contact number starts with country code (example: +44 for UK)")
        return None


def update_database(contact_number, vanity_numbers):
    timestamp = int(time.mktime(datetime.now().timetuple()))
    try:
        db_name.put_item(
                TableName='customer-details',
                Item={
                    'ContactNumber': contact_number,
                    'CallDateTime' : timestamp,
                    'VanityNumbers' : vanity_numbers
                }
            )
        return {"success":"data stored successful"}
    except:
        return {"failed": "unable to write data"}

def fetch_data(contact_number):
    try:
        response = db_name.query(
        KeyConditionExpression = "ContactNumber = :v1",
        ExpressionAttributeValues = {
        ':v1': contact_number,
        },
        ScanIndexForward=False,
        Limit=1
        )

        items = response['Items']

        if len(items) == 0:
            return None
        else:
            now= datetime.fromtimestamp(response['Items'][0]['CallDateTime'])
            items[0]['CallDateTime'] = str(now)
            return items[0]
    except:
        return None


def lambda_handler(event, context):
    """Lambda function main handler

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    Number = event['Details']['ContactData']['CustomerEndpoint']['Address']
    if parse_contactnumber(Number):
        parsed_number = str(parse_contactnumber(Number).get('contact_number'))
        print(f"contact number entered is {Number}")
        vanity_numbers = find_words_from_numbers(parsed_number,max_number_results_to_output=5)
        if fetch_data(Number):
            print(f"Best Vanity number for contact number {fetch_data(Number).get('ContactNumber')} are {fetch_data(Number).get('VanityNumbers')}")
            return { "ContactNumber": fetch_data(Number).get('ContactNumber'),
                     "VanityNumber01": fetch_data(Number).get('VanityNumbers')[0],
                     "VanityNumber02": fetch_data(Number).get('VanityNumbers')[1],
                     "VanityNumber03": fetch_data(Number).get('VanityNumbers')[2],
                     "VanityNumber04": fetch_data(Number).get('VanityNumbers')[3],
                     "VanityNumber05": fetch_data(Number).get('VanityNumbers')[4]
                     }
        else:
            update_database(Number,vanity_numbers)
            print(f"Best Vanity number for contact number {fetch_data(Number).get('ContactNumber')} are {fetch_data(Number).get('VanityNumbers')}")
            return { "ContactNumber": fetch_data(Number).get('ContactNumber'),
                     "VanityNumber01": fetch_data(Number).get('VanityNumbers')[0],
                     "VanityNumber02": fetch_data(Number).get('VanityNumbers')[1],
                     "VanityNumber03": fetch_data(Number).get('VanityNumbers')[2],
                     "VanityNumber04": fetch_data(Number).get('VanityNumbers')[3],
                     "VanityNumber05": fetch_data(Number).get('VanityNumbers')[4]
                     }
    else:
        return { "message": "failed" }
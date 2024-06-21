import argparse
import os
import json
import subprocess
from dotenv import load_dotenv
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.identity import DefaultAzureCredential

def list_all_role_assignments_on_subscription_level(subscription_id: str):
    """
    DEVOPS-58 jira story
    :return: all role assignemnts in the subscription level
    """
    load_dotenv()
    scope=f'{subscription_id}'.format(subscription_id=subscription_id)
    print(f'Current Scope is : {scope}')
    # Create client
    # # For other authentication approaches, please see: https://pypi.org/project/azure-identity/

    authorization_client = AuthorizationManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=subscription_id,
        api_version="2018-01-01-preview"
    )
    # Retrieve role assignment
    get_all_role_assignment = authorization_client.role_assignments.list_for_subscription()
    print(f'Role assignments retrieved.... ')
    get_all_role_assignment_list = []
    for role_assignment in get_all_role_assignment:
        print(role_assignment)
        role_assignment_dict = {}
        role_assignment_dict['id'] = role_assignment.id
        role_assignment_dict['name'] = role_assignment.name
        role_assignment_dict['type'] = role_assignment.type
        role_assignment_dict['principal_id'] = role_assignment.principal_id
        get_all_role_assignment_list.append(role_assignment_dict)
    return get_all_role_assignment_list


def main():
    """ To test the code"""
    parser = argparse.ArgumentParser("Retrieve role assignments in Azure using python")
    parser.add_argument("--subscription_id", help="subscription id in azure", required=True, type=str)

    args = parser.parse_args()
    subscription_id = args.subscription_id
    print("Proccess to retrieve azure role assignments initiated......")
    # get_all_role_assignment_list = list_all_role_assignments_on_subscription_level(subscription_id=subscription_id)
    get_all_role_assignment_list = list_role_assgnmnt_azcli(subscription_id=subscription_id)
    file_name = f'role_assignments_{subscription_id}.json'
    # Assuming role_assignment_dict is already populated
    with open(file_name, 'w') as json_file:
        json.dump(get_all_role_assignment_list, json_file, indent=4)


if __name__ == "__main__":
    main()
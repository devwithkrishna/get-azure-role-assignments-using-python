import argparse
import os
import json
from dotenv import load_dotenv
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.common.credentials import ServicePrincipalCredentials
from azure.graphrbac import GraphRbacManagementClient
from azure.graphrbac.models import GraphErrorException
from azure.core.exceptions import ResourceNotFoundError


def list_all_role_assignments_on_subscription_level(subscription_id: str):
    """
    DEVOPS-58 jira story
    :return: all role assignemnts in the subscription level
    """
    scope=f'{subscription_id}'.format(subscription_id=subscription_id)
    print(f'Current Scope is : {scope}')
    # Create client
    # # For other authentication approaches, please see: https://pypi.org/project/azure-identity/

    authorization_client = AuthorizationManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=subscription_id,
    )
    # Retrieve role assignment
    get_all_role_assignment = authorization_client.role_assignments.list_for_subscription()
    print(f'Role assignments retrieved.... ')
    get_all_role_assignment_list = []
    for role_assignment in get_all_role_assignment:
        # print(role_assignment)
        role_assignment_dict = {}
        role_assignment_dict['id'] = role_assignment.id
        role_assignment_dict['name'] = role_assignment.name
        role_assignment_dict['type'] = role_assignment.type
        role_assignment_dict['principal_id'] = role_assignment.principal_id
        role_assignment_dict['principal_type'] = role_assignment.principal_type
        role_assignment_dict['role_definition_id'] = role_assignment.role_definition_id
        role_assignment_dict['assignment_creation_time'] = (role_assignment.created_on).strftime("%d-%m-%Y, %H:%M:%S") #dd-mm-yyyy hh-mm-ss formt
        role_assignment_dict['scope'] = role_assignment.scope
        get_all_role_assignment_list.append(role_assignment_dict)
    return get_all_role_assignment_list


def graph_rbac_to_access_ad(get_all_role_assignment_list: list[dict]):
    """
    This function is used to access Microsoft Entra id to query user / groups / sp details
    """
    client_id = os.getenv('AZURE_CLIENT_ID')
    secret = os.getenv('AZURE_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID')
    credentials =ServicePrincipalCredentials(secret=secret,client_id=client_id,tenant= tenant_id,resource="https://graph.windows.net")
    graphrbac_client = GraphRbacManagementClient(
        credentials,
        tenant_id, base_url=None
    )

    for role_assignment in get_all_role_assignment_list:
        # if role assignment is for user
        if role_assignment['principal_type'] == "User":
            upn = role_assignment['principal_id']
            user_name = graphrbac_client.users.get(upn_or_object_id=upn)
            # print(user_name)
            role_assignment['principal_name'] = user_name.given_name
        # if role assignment was for a group
        elif role_assignment['principal_type'] == "Group":
            obj_id = role_assignment['principal_id']
            group_name = graphrbac_client.groups.get(object_id=obj_id)
            # print(group_name)
            role_assignment['principal_name'] = group_name.display_name
        # if role assignment was for a sp
        elif role_assignment['principal_type'] == "ServicePrincipal":
            spn_id = role_assignment['principal_id']
            try:
                sp_name = graphrbac_client.service_principals.get(object_id=spn_id)
                role_assignment['principal_name'] = sp_name.app_display_name

            except GraphErrorException as e:
                if "does not exist" in str(e):
                    role_assignment['principal_name'] = "NA"
                    # print("NA")
                else:
                    raise e
    return get_all_role_assignment_list


def role_definition_id_to_role_name(role_def_to_name: list[dict],subscription_id:str):
    """Get role name from role definition id"""
    # scope = f'{subscription_id}'.format(subscription_id=subscription_id)
    client = AuthorizationManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=subscription_id,
    )

    for role_def in role_def_to_name:
        full_role_definition_id = role_def['role_definition_id']
        # Extract the role definition ID from the full path
        role_definition_id = full_role_definition_id.split('/')[-1]
        scope = f'/subscriptions/{subscription_id}'
        try:
            response = client.role_definitions.get(
                scope=scope,
                role_definition_id=role_definition_id
            )
            role_def['rbac_role_name'] = response.role_name
            print(f"Role definition ID {role_definition_id} corresponds to role name {response.role_name}")
        except ResourceNotFoundError as e:
            print(f"ResourceNotFoundError: {e.message}")
            role_def['role_name'] = "NA"
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            role_def['role_name'] = "NA"
    return role_def_to_name

def main():
    """ To test the code"""
    parser = argparse.ArgumentParser("Retrieve role assignments in Azure using python")
    parser.add_argument("--subscription_id", help="subscription id in azure", required=True, type=str)

    args = parser.parse_args()
    subscription_id = args.subscription_id
    load_dotenv()
    print("Proccess to retrieve azure role assignments initiated......")
    get_all_role_assignment_list = list_all_role_assignments_on_subscription_level(subscription_id=subscription_id)
    file_name = f'role_assignments_{subscription_id}.json'
    # Assuming role_assignment_dict is already populated
    with open(file_name, 'w') as json_file:
        json.dump(get_all_role_assignment_list, json_file, indent=4)

    # read from microsoft entra id
    file_name = f'role_assignments_with_name{subscription_id}.json'
    get_all_role_assignment = graph_rbac_to_access_ad(get_all_role_assignment_list=get_all_role_assignment_list)
    with open(file_name, 'w') as json_file:
        json.dump(get_all_role_assignment, json_file, indent=4)

    role_def_to_name = role_definition_id_to_role_name(role_def_to_name=get_all_role_assignment, subscription_id= subscription_id)

    file_name = 'role_assignments_with_principal_name_and_rbac_role.json'
    with open(file_name, 'w') as json_file:
        json.dump(role_def_to_name, json_file, indent=4)

if __name__ == "__main__":
    main()
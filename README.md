# get-azure-role-assignments-using-python
This repository contains python code to get the role assignments from azure


# What this repository do

```markdown
This repo contains the source code which can be used to list the role assignments on a subscription level
for Azure using Python azure SDK's.
```

## parameters 

| inputs | description | mandatory |
|--------|-------------|-----------|
|subscription_id| azure subscription id| :heavy_check_mark: |

## Authentication

Authentication to Azure is done using service principal credentials

have a `.env file`

```yaml
AZURE_CLIENT_ID="xxx"
AZURE_CLIENT_SECRET="xxx"
AZURE_TENANT_ID="xxx"
AZURE_SUBSCRIPTION_ID="xxx"
```
Where xxx refers to the actual values. These will vary for everyone

using python-dotenv module and fucntion load_dotenv() uses it for local testing.

# Final output 

```json
{
        "id": "/subscriptions/<subscription id>/providers/Microsoft.Authorization/roleAssignments/<assignment id>",
        "name": "<name>",
        "type": "Microsoft.Authorization/roleAssignments",
        "principal_id": "<principal id>",
        "principal_type": "< group or user or service principal>",
        "role_definition_id": "<role definition id>",
        "assignment_creation_time": "<when assignment was created>",
        "scope": "/subscriptions/<subscription id>",
        "principal_name": "<principal name>",
        "rbac_role_name": "<Azure Rbac or custom role namess>"
    }
```

* for local testing the code creates this as a json file.

# How to run the code locally

```commandline
python3 role_assignments.py --subscription_id <subscription id> 
```

### For package management poetry is used.


## Refernces

[role-assignments-list](https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-list-rest)
[role-based-access-control built-in-roles](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles)
[AuthorizationManagementClient](https://learn.microsoft.com/en-us/rest/api/authorization/role-definitions/get?view=rest-authorization-2022-04-01&tabs=Python)
[azure graph rbac](https://learn.microsoft.com/en-us/python/api/azure-graphrbac/azure.graphrbac.operations.service_principals_operations.serviceprincipalsoperations?view=azure-python-previous#azure-graphrbac-operations-service-principals-operations-serviceprincipalsoperations-get)
# TypeGenieAPIClient
Python API client to access TypeGenie API. 

# Documentation
Check out detailed API documentation at [https://api.typegenie.net](https://api.typegenie.net)

## Installation
Run the following to install:

`pip install typegenie`


## Using `typegenie-cli`
Once a model has been deployed, you can use `typegenie-cli` to test the model quality. 

```bash
typegenie-cli -dsi <DATASET-ID> -dpi <DEPLOYMENT-ID> -u <ACCOUNT-USER-ID> -p <PASSWORD> -ui <USER-ID> --multiline
```

where `<USER-ID>` is the id of the user that exists within the deployment `<DEPLOYMENT-ID>` The tool
 randomly samples dialogues from the given dataset, and shows messages with different colors.
 
Use `ctr+c` to start a new dialogue and `ctr+c` twice to exit. 

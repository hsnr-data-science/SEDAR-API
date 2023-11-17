# Import needed python modules
import os
import random

# Import all SEDAR modules
from sedarapi import SedarAPI

#--------------------------------------------------------------
#---------------------------- Main ----------------------------
#--------------------------------------------------------------
if __name__ == "__main__":
#Test variables
    base_url = "http://127.0.0.1:5000"
    email = "admin"
    password = "admin"
    random_number = random.randint(10000,99999)
    datasource_definition_file = "csv_default.json"
    dataset_file_path = "username.csv"
    datasource_definition_text = {
        "name":"Python_Ingestion_1",
        "read_format":"csv",
        "read_options":
            {
                "delimiter":";",
                "header":"true",
                "inferSchema":"true"
            },
        "write_type":"DEFAULT",
        "read_type":"SOURCE_FILE",
        "id_column":"Identifier",
        "source_files":["username"]
    }
    search_parameters = {
        "query": "Fro",
        "source_search": False,
        "semantic_search": False,
        "author": "",
        "schema": "",
        "zone": "",
        "tags": [],
        "sort_target": "",
        "sort_direction": "",
        "status": "",
        "limit": "10",
        "rows_min": "",
        "rows_max": "",
        "with_auto_wildcard": True,
        "search_schema_element": False,
        "filter_schema": False,
        "is_pk": False,
        "is_fk": False,
        "size_min": "",
        "size_max": "",
        "notebook_search": False,
        "notebook_type": "",
        "hasRun": False,
        "hasNotebook": False,
        "hasRegModel": False,
        "selectedExperiment": "\"\"",
        "selectedMetrics": "[]",
        "selectedParameters": "[]"
    }
    workspace_user_update_parameter = {
        "add": False,
        "email": f"PythonUser_{random_number}",
        "can_read": True,
        "can_write": False,
        "can_delete": False
    }
    
    sedar = SedarAPI(base_url)
    sedar.connection.logger.setLevel("INFO")

    try:
        # Login to the data lake and save the user
        print("Login to the Data Lake...")
        admin_user = sedar.login(email, password)
        print("Success!\n")

        # Get Wiki markdown
        print("Get Wiki markdown...")
        wiki = sedar.get_wiki()
        print("Success!\n")

        # Update the Wiki markdown
        print("Update the Wiki markdown...")
        new_markdown = "::Edited with Python::" + wiki.content
        wiki = wiki.update(new_markdown)
        print("Success!\n")

        # Get Hive alive check
        #print("Check Hive components...")
        #sedar.get_hive_health()
        #print("Success!\n")

        # Get general stats
        print("Get general Stats...")
        print(sedar.get_stats())
        print("Success!\n")

        # Get error logs
        print("Get error logs...")
        print(sedar.get_error_logs())
        print("Success!\n")

        # Download access logs
        print("Download access logs...")  
        sedar.get_access_logs(download_path=os.path.join(os.getcwd(), 'access.log'))
        print("Success!\n")

        # Create a new user
        print("Create a new user...")  
        new_user = sedar.create_user(email=f"PythonUser_{random_number}", password="postman", firstname="Mister",
                                    lastname="Postman", username=f"PythonUser_{random_number}",is_admin=True)
        print("Success!\n")
        
        # Edit our user
        print("Edit our user...")
        new_user.update(firstname="NewEditedUser.")
        print("Success!\n")

        # Create our own workspace
        print("Create our own Workspace...")
        my_workspace = sedar.create_workspace(title="Python created", description="Python-Test", wrong_param="bla")
        print("Success!\n")

        # Edit our workspace
        print("Edit our Workspace...")
        my_workspace = my_workspace.update(title="Edited Workspace")
        print("Success!\n")

        # Delete our workspace
        print("Delete our workspace...")
        my_workspace.delete()
        print("Success!\n")

        # Get all Workspaces
        print("Get all Workspaces...")
        workspaces = sedar.get_all_workspaces()
        print("Success!\n")

        # Get the Default Workspace
        print("Get the Default Workspace...")
        for workspace in workspaces:
            if workspace.content["title"] == "Default Workspace":
                default_workspace = workspace
                break
        print("Success!\n")

        # Get all Workspace Users
        print("Get all Workspace Users...")
        workspace_users = default_workspace.get_workspace_users()
        print("Success!\n")
        
        # Update Workspace User Permissions
        #print("Update Workspace User Permissions...")
        #default_workspace.update_workspace_user_permissions(**workspace_user_update_parameter)
        #print("Success!\n")

        # Delete our user
        print("Delete our user...")
        new_user.delete()
        print("Success!\n")

        # Create a Dataset
        print("Create a Dataset...")
        new_dataset = default_workspace.create_dataset(datasource_definition_text, dataset_file_path)
        print("Success!\n")

        # Get all Datasets of the default Workspace
        print("Get all Datasets of our Workspace...")
        datasets = default_workspace.get_all_datasets()
        print("Success!\n")

        # Get the first of the default Workspace
        print("Get the first Dataset of our Workspace...")
        some_dataset = default_workspace.get_dataset(datasets[0].id)
        print("Success!\n")

        # Update our Dataset
        print("Update our Dataset...")
        new_dataset = new_dataset.update(title="Python_Dataset-Edited",description="Python-Edit", author="Nico Kuth")
        print("Success!\n")

        # Ingest our updated Dataset
        print("Ingest our updated Dataset...")
        ingest_res = new_dataset.ingest()
        print("Success!\n")

        # Publish our Dataset
        print("Publish our Dataset...")
        new_dataset.publish()
        print("Success!\n")

        # Get the logs of our Dataset
        print("Get the logs of our Dataset...")
        dataset_logs = new_dataset.get_logs()
        print("Success!\n")
        
        print(sedar.get_current_user().content)

        # Search our Dataset
        print("Search our Dataset...")
        search_results = default_workspace.search_datasets(search_parameters)
        print("Success!\n")
        
        for dataset in search_results:
            print(dataset.content)

        # Create an Ontology
        print("Create an Ontology...")
        file = {'file': ('foaf.rdf', open('foaf.rdf', 'rb'), 'application/rdf+xml')}
        new_ontology = default_workspace.create_ontology(title="Foaf", description="Uploaded with Python", file=file)
        print("Success!\n")
        
        # Get all Ontologies of the default Workspace
        print("Get all Ontologies of our Workspace...")
        ontologies = default_workspace.get_all_ontologies()
        print("Success!\n")

        # Get the Default Ontology 'FOAF'
        for ontology in ontologies:
            if ontology.content["title"] == "FOAF":
                default_ontology = ontology
                break

        # Get the IRI of our Ontology
        print("Get the IRI of our Ontology...")
        new_ontology_iri = new_ontology.get_iri()
        print("Success!\n")

        # Execute a construct query
        print("Execute a construct query...")
        construct_query = f"PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?person WHERE {{ ?person a foaf:Person. }}"
        construct_res = new_ontology.execute_construct_query(construct_query)
        print("Success!\n")

        # Download our Ontology
        print("Download our Ontology...")
        new_ontology.download("ontology_download")
        print("Success!\n")

        # Update our Ontology
        print("Update our Ontology...")
        new_ontology = new_ontology.update(title="Foaf_Edited",description="Python-Edit")
        print("Success!\n")

        # Delete our Ontology
        print("Delete our Ontology...")
        #new_ontology.delete()
        print("Success!\n")

        # Add a tag to our dataset
        print("Add a tag to our dataset...")
        new_tag = new_dataset.add_tag(default_ontology,annotation="<http://xmlns.com/foaf/0.1/Person>",title="Python-Tag")
        print("Success!\n")

        # Add a tag to our dataset
        print("Get all tags of our Dataset...")
        all_tags = new_dataset.get_tags()
        print("Success!\n")

        # Delete our Tag from the Dataset
        print("Delete our Tag from the Dataset...")
        new_tag.delete()
        print("Success!\n")

        # Get all experiments of our workspace
        print("Get all experiments of our workspace...")
        all_experiments = default_workspace.get_all_experiments()
        print("Success!\n")

        # Create a new experiment in our workspace
        print("Create a new experiment in our workspace...")
        new_experiment = default_workspace.create_experiment(f"Python-Experiment_{random_number}")
        print("Success!\n")


        runs = new_experiment.get_all_runs()

        # Delete our Experiment
        print("Delete our Experiment...")
        new_experiment.delete()
        print("Success!\n")

        # Delete our dataset
        print("Delete our dataset...")
        new_dataset.delete()
        print("Success!\n")

        # Logout
        print("Logout...")
        sedar.logout()
        print("Success!\n")

    except Exception as e:
        print(e)
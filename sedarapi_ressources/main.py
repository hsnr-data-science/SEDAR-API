# Import needed python modules
import random
import time
import os

# Import the "sedarapi" package
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
    dataset_update_file_path = "username2.csv"
    datasource_definition_text = {
        "name":"MyNewDataset",
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
    datasource_definition_update_text = {
        "name":"MyNewDataset",
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
        "source_files":["username2"]
    }
    search_parameters = {
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
        "is_pk": True,
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

        df = sedar.get_all_workspaces()[0]
        ds = df.get_dataset("52489214b90b4356bc185340aa8a309e")
        

        # Test Mlflow-stuff.
        #
        #exp.deploy_run(runs[0], "Example_Run"
        model = df.get_all_registered_models()[0]
        exp = df.get_all_experiments()[0]

        notebook = exp.create_jupyter_code("Unsupervised Learning", "sklearn.cluster.DBSCAN", [ds], "Python-Code-Deploay", "descr", True, True)
        runs = exp.get_all_runs()
        exp.deploy_run(runs[0], "Test-Deploy")

        print("Logout...")
        sedar.logout()
        print("Success!\n")

    except Exception as e:
        print(e)


# Code als Backup, damit die erstellten Tests nicht weg sind.
def nonExecutedCode():
        

    # Test Mlflow-stuff.
    #exp.create_jupyter_code("Supervised Learning", "sklearn.svm.SVC", [ds], "Python-Test", "descr", True, False)
    notebook = ds.get_notebooks()[0]
    #exp.deploy_run(runs[0], "Example_Run"
    model = df.get_all_registered_models()[0]
    exp = df.get_all_experiments()[0]
    runs = exp.get_all_runs()

    for run in runs:
        print(run.id)

    print("------------------------")
    print("Model name:  " + model.name)
    print("Model version: " + model.version)
    print("Model Stage: " + model.stage)

    model = model.handle_transition("archived")

    print("------------------------")
    print("--- After Transition ---")
    print("------------------------")
    print("Model name:  " + model.name)
    print("Model version: " + model.version)
    print("Model Stage: " + model.stage)



# test new annotation implementation
    ds = df.get_dataset("969e8e0d2f124382a18f4c10b3655dff")
    default_ontology = df.get_ontology("25f75713328e4d3db86f23af185648b5")

    annotation_list = df.ontology_annotation_search("Person")
    for annotation in annotation_list:
        if annotation.title == "Person":
            anon = annotation
    
    ds.add_tag("Tag_Title", default_ontology, anon)





#
    workspaces = sedar.get_all_workspaces()

    # Get the default workspace
    for workspace in workspaces:
        if workspace.title == "Default Workspace":
            df = workspace

    ds = df.get_dataset("969e8e0d2f124382a18f4c10b3655dff")
    default_ontology = df.get_ontology("25f75713328e4d3db86f23af185648b5")

    annotation_list = default_ontology.get_all_annotations()
    #annotation_list = df.ontology_annotation_search("Person")
    for annotation in annotation_list:
        print(annotation.title)
        if annotation.title == "Person":
            anon = annotation
    
    ds.add_tag("Tag_Title", default_ontology, anon)

    iri = default_ontology.get_iri()
    print(iri)
    



    # Files & Entities
    # Login to the data lake and save the user
    print("Login to the Data Lake...")
    admin_user = sedar.login(email, password)
    print("Success!\n")

    workspaces = sedar.get_all_workspaces()

    # Get the default workspace
    for workspace in workspaces:
        if workspace.title == "Default Workspace":
            df = workspace

    ds = df.get_dataset("52489214b90b4356bc185340aa8a309e")
    #ds2 = df.get_dataset("6132285d13c2437792158116808ff37d")
    #onto = df.get_ontology("43ff44a3468e4dcb8c77b5566f207805")
    default_ontology = df.get_all_ontologies()[0]
    annotation_list = default_ontology.get_all_annotations()
    for annotation in annotation_list:
        if annotation.title == "Person":
            anon = annotation

    default_ontology.download()
    entity = ds.get_all_entities()[0]
    #entity = entity.update(name="NewDisplayName", description="Updated via Python-API")
    #entity.add_annotation(anon, "Python-Added-Annotation")
    #entity.remove_annotation("0922b9bb8d804c0bbdc6eec1b5241e56")
    #attribute = ds.get_all_attributes()[0]
    #fk_attribute = ds2.get_all_attributes()[0]

    #file = ds2.get_all_files()[0]
    file = file.update(description="Updated via Python-API")
    #file.add_annotation(anon, description="Python-Added-Annotation")

    #attribute.create_foreign_key_construct(default_ontology, anon, ds2, fk_attribute)








    workspaces = sedar.get_all_workspaces()

    # Get the default workspace
    for workspace in workspaces:
        if workspace.title == "Default Workspace":
            df = workspace

    ds = df.get_dataset("d1d5297531254396b64952c913fc2216")
    #ds2 = df.get_dataset("6132285d13c2437792158116808ff37d")
    #onto = df.get_ontology("43ff44a3468e4dcb8c77b5566f207805")
    default_ontology = df.get_all_ontologies()[0]
    annotation_list = default_ontology.get_all_annotations()
    for annotation in annotation_list:
        if annotation.title == "Person":
            anon = annotation

    #Constraints = ds.get_cleaning_suggestions()
    #for constraint in Constraints:
    #    print(f"Name: {constraint.name}")
    #    print(f"Code: {constraint.code}")
    #    print("-----------------------")


    #ds.validate_cleaning_constraints([Constraints[0], Constraints[1]])
    #val = ds.get_current_validations()
    #print(val)
    attributes = ds.get_all_attributes()

    for attribute in attributes:
        print(attribute.name)
    attribute = attributes[0].name
    cleaner = ds.get_cleaner()
    suggestions = cleaner.get_constraint_suggestions()
    cleaner.add_is_complete_constraint(attribute)
    #cleaner.add_is_unique_constraint("Lastname")
    
    filters = cleaner.get_filter_suggestions()
    #cleaner.execute_local_filters(datasource_definition_text)
    print(cleaner.get_local_constraints())

    response = cleaner.validate_local_constraints()

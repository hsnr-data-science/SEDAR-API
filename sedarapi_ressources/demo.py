# Import the "sedarapi" package
from sedarapi import SedarAPI

#--------------------------------------------------------------
#---------------------------- Main ----------------------------
#--------------------------------------------------------------
if __name__ == "__main__":
    # sedar configuration vars
    base_url = "http://127.0.0.1:5000"
    email = "admin"
    password = "admin"
    
    # paths to local datasets
    dataset_file_path = "./sedarapi_ressources/ressources/username.csv"

    # datasource definitions
    datasource_definition_file = "./sedarapi_ressources/ressources/csv_default.json"
    datasource_definition_text = {
        "name":"Python-Dataset",
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

    sedar = SedarAPI(base_url)
    sedar.connection.logger.setLevel("INFO")

    try:
        sedar.login(email, password)

        workspaces = sedar.get_all_workspaces()

        for workspace in workspaces:
            if workspace.title == "Default Workspace":
                default_workspace = workspace

        dataset = default_workspace.create_dataset(datasource_definition_text, dataset_file_path)

        foaf = default_workspace.get_all_ontologies()[0]

        annotations = foaf.get_all_annotations()

        for annotation in annotations:
            if annotation.title == "Person":
                anon = annotation

        tag = dataset.add_tag("MyTag", foaf, anon)

        dataset.ingest()
        dataset.publish()

        sedar.logout()
    except Exception as e:
        print(e)

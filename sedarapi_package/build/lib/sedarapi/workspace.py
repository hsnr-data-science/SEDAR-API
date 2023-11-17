# Import needed python modules
from __future__ import annotations
from typing import Type
from typing import List
import json
import os

# Import needed SEDAR modules
from .commons import Commons
from .dataset import Dataset
from .user import User
from .ontology import Ontology
from .ontology import Annotation
from .mlflow import Experiment
from .mlflow import ExperimentModel

class Workspace:
    #--------------------------------------------------------------
    def __init__(self, connection: Type[Commons], workspace_id: str):
        self.id = workspace_id
        self.connection = connection
        self.logger = self.connection.logger
        self.content = self._get_workspace_json(self.id)

        # Extract some members from the "content" attribute
        self.title = self.content["title"]
        self.description = self.content["description"]
        # ...

    #--------------------------------------------------------------
    #--------------------- Interface methods ----------------------
    #--------------------------------------------------------------
    def update(self, title: str = None, description: str = None) -> Workspace:
        """
        Updates the details of the specified workspace.

        Args:
            title (str): The new title of the workspace.
            description (str, optional): The description of the workspace.

        Returns:
            Workspace: An instance of the Workspace class representing the updated workspace. 
            The content of the workspace details can be accessed using the `.content` attribute.

        Raises:
            Exception: If there's an error during the update process.

        Description:
            This method updates the details of a specific workspace by sending a PUT request to the '/api/workspaces/{workspace_id}' endpoint. 
            The title and description of the workspace can be updated.

        Notes:
            - The method requires appropriate permissions to update a workspace.
            - The returned Workspace object contains various details about the workspace, including associated users and their permissions.

        Example:
            workspace = sedar.get_all_workspaces()[0]
            try:
                updated_workspace = workspace.update(title="New Workspace Title", description="Updated Description")
                print(updated_workspace.content["title"], updated_workspace.content["description"])
            except Exception as e:
                print(e)
        """
        return Workspace(self.connection, self._update_workspace(self.id, title, description)["id"])
    
    def delete(self) -> bool:
        """
        Deletes the specified workspace.

        Args:
            None

        Returns:
            bool: True if the workspace was successfully deleted, otherwise False.

        Raises:
            Exception: If there's an error during the deletion process.

        Description:
            This method deletes a specific workspace by sending a DELETE request to the '/api/workspaces/{workspace_id}' endpoint.

        Notes:
            - The method requires appropriate permissions to delete a workspace.
            - Ensure that the workspace exists and is accessible before attempting to delete it.

        Example:
            workspace = sedar.get_all_workspaces()[0]
            try:
                success = workspace.delete()
                if success:
                    print("Workspace successfully deleted!")
                else:
                    print("Failed to delete workspace.")
            except Exception as e:
                print(e)
        """
        return self._delete_workspace(self.id)
    
    def get_workspace_users(self) -> List[User]:
        """
        Retrieves the list of users associated with a specific workspace.

        Args:
            None

        Returns:
            List[User]: A list of User instances, each representing a user associated with the workspace. 
                The details of each user can be accessed using the `.content` attribute of the User instance.

        Raises:
            Exception: If there's an error during the retrieval process.

        Description:
            This method retrieves a list of users associated with a specific workspace by sending 
            a GET request to the '/api/workspaces/{workspace_id}/users' endpoint.

        Notes:
            - The method requires appropriate permissions to view workspace users.
            - The returned list can be empty if no users are associated with the workspace.

        Example:
            workspace = sedar.get_all_workspaces()[0]
            try:
                users = workspace.get_workspace_users()
                for user in users:
                    print(user.content['email'], user.content['firstname'])
            except Exception as e:
                print(e)
        """
        users_info = self._get_all_workspace_users_json(self.id)
        return [User(self.connection, user_info["email"]) for user_info in users_info]

    def update_workspace_user_permissions(self, user: Type[User], add: bool = None, can_read: bool = None, can_write:bool = None, can_delete:bool = None) -> User:
        """
        Updates the permissions for a specific user in the workspace.

        Args:
            user (User): An instance of the User class representing the user whose permissions need to be updated.
            add (bool): Specifies whether the user should be added or removed from the workspace. `True` to add, `False` to remove.
            can_read (bool): Specifies if the user has read permissions.
            can_write (bool): Specifies if the user has write permissions.
            can_delete (bool): Specifies if the user has delete permissions.

        Returns:
            User: An instance of the User class representing the user with updated permissions. 
            The content of the user details can be accessed using the `.content` attribute.

        Raises:
            Exception: If there's a failure in updating the user permissions.

        Description:
            This method updates the permissions of a specific user in the workspace by sending a PUT request to the 
            '/api/v1/workspaces/{workspace_id}/users' endpoint.

        Notes:
            - Ensure the provided user exists in the system
            - If the 'add' parameter is not provided, the method will only update the user's permissions without adding or removing them from the workspace.

        Example:
            user = sedar.login(email, password)
            workspace = sedar.get_all_workspaces()[0]
            user = sedar.create_user(...)
            try:
                updated_user = workspace.update_workspace_user_permissions(user, add=True, can_read=True, can_write=True, can_delete=False)
                print(updated_user.content)
            except Exception as e:
                print(e)
        """
        return User(self.connection, self._update_workspace_user_permissions(self.id, user.content["email"], add, can_read, can_write, can_delete)["email"])

    #####################
    # Dataset Interface #
    #####################

    def get_all_datasets(self, get_unpublished: bool = True) -> List[Dataset]:
        """
        Retrieves all datasets associated with the workspace.

        Returns:
            List[Dataset]: A list of Dataset instances representing each dataset in the workspace. 
            The content of each dataset can be accessed using the `.content` attribute.

        Args:
            get_unpublished (bool): Specifies if the list contains only unpublished datasets. This parameter should not be changed.

        Raises:
            Exception: If there's a failure in retrieving the datasets.

        Description:
            This method fetches all datasets associated with the current workspace by sending a GET request 
            to the '/api/v1/workspaces/{workspace_id}/datasets' endpoint.

        Notes:
            - Ensure the Workspace instance is correctly initialized and authenticated before calling this method.

        Example:
            workspace = sedar.get_all_workspaces()[0]
            try:
                datasets = workspace.get_all_datasets()
                for dataset in datasets:
                    print(dataset.content['title'])
            except Exception as e:
                print(e)
        """
        datasets_info = self._get_all_datasets_json(self.id,get_unpublished)
        return [Dataset(self.connection, self.id, dataset_info["id"]) for dataset_info in datasets_info]
    
    def get_favorite_datasets(self) -> List[Dataset]:
        """
        Retrieves all favorite datasets of the authenticated user associated with the workspace.

        Args:
            None

        Returns:
            List[Dataset]: A list of Dataset instances representing each favorite dataset in the workspace. 
            The content of each dataset can be accessed using the `.content` attribute.

        Raises:
            Exception: If there's a failure in retrieving the datasets.

        Description:
            This method fetches all favorite datasets associated with the current workspace by sending a GET request 
            to the '/api/v1/workspaces/{workspace_id}/datasets/favorites' endpoint.

        Notes:
            - Ensure the Workspace instance is correctly initialized and authenticated before calling this method.

        Example:
            workspace = sedar.get_all_workspaces()[0]
            try:
                favorite_datasets = workspace.get_favorite_datasets()
                for dataset in favorite_datasets:
                    print(dataset.content['title'])
            except Exception as e:
                print(e)
        """
        datasets_info = self._get_favorite_datasets_json(self.id)
        return [Dataset(self.connection,self.id, dataset_info["id"]) for dataset_info in datasets_info]
    
    def get_dataset(self, dataset_id: str) -> Dataset:
        """
        Retrieves a specific dataset from the SEDAR workspace.

        Args:
            dataset_id (str): The ID of the dataset to retrieve.

        Returns:
            Dataset: An instance of the Dataset class representing the retrieved dataset.
            The content of the dataset details can be accessed using the `.content` attribute.

        Raises:
            Exception: If there's a failure in retrieving the dataset.

        Description:
            This method fetches the details of a specific dataset within the SEDAR workspace.
            It sends a GET request to the '/api/v1/workspace/{workspace_id}datasets/{dataset_id}' endpoint and checks the response.

        Notes:
            - Make sure to provide the dataset_id when calling this method.
            - Ensure the dataset_id provided exists in the SEDAR workspace.

        Example:
            workspace = sedar.get_all_workspaces()[0]
            dataset_id = "1234"
            try:
                dataset = sedar.get_dataset(dataset_id)
                print(dataset.content['title'])
            except Exception as e:
                print(e)
        """
        return Dataset(self.connection, self.id, dataset_id)
    
    def create_dataset(self, datasource_definition: any, file_paths: str) -> Dataset:
        """
        Creates a new datasource definition in the SEDAR system attached to the specified workspace.

        Args:
            datasource definition (str or dict): It can be a path to a JSON file or a dictionary containing the definition.
            file_paths (str or dict): Either a single path to a file (str) or a dictionary of file names to file paths. 

        Returns:
            Dataset: An instance of the Dataset class representing the newly created dataset. 
            The content of the dataset details can be accessed using the `.content` attribute.

        Raises:
            Exception: If there's a failure in creating the dataset.

        Description:
            This method creates a new dataset within the SEDAR workspace. 
            It sends a POST request to the '/api/v1/workspace/{workspace_id}/datasets' endpoint with the provided details and checks the response.

        Notes:
            - Ensure the provided datasource definition is valid and aligns with the expected format.
            - Currently the API can only process single files. Use a str file_path for now.

        Example:
            workspace = sedar.get_all_workspaces()[0]
            try:
                new_dataset = workspace.create_dataset("datasource-definiton.json", "username.csv")
                print(new_dataset.content['title'])
            except Exception as e:
                print(e)
        """
        return Dataset(self.connection,self.id, self._create_dataset(self.id, datasource_definition, file_paths)["id"])
    
    def search_datasets(self, query, advanced_search_parameters: dict=None, ignore_errors: bool = False) -> List[Dataset]:
        """
        Searches for datasets in the SEDAR system inside the specified workspace.

        Args:
            query (str): A typical query string for a text based search.
            ignore_errors (bool, optional): See under "Notes". If set to true, no exception will be thrown if server error occurs.
            advanced_search_parameters (dict, optional): Additional search parameters.
                Currently accepted as advanced parameters are:
                    "source_search":  bool,
                    "semantic_search": bool,
                    "author": str,
                    "schema": str,
                    "zone": str,
                    "tags": [],
                    "sort_target": str,
                    "sort_direction": str,
                    "status": str,
                    "limit": str,
                    "rows_min": str,
                    "rows_max": str,
                    "with_auto_wildcard": bool,
                    "search_schema_element": bool,
                    "filter_schema": bool,
                    "is_pk": bool,
                    "is_fk": bool,
                    "size_min": str,
                    "size_max": str,
                    "notebook_search": bool,
                    "notebook_type": str,
                    "hasRun": bool,
                    "hasNotebook": bool,
                    "hasRegModel": bool,
                    "selectedExperiment": "\"\"",
                    "selectedMetrics": "[]",
                    "selectedParameters": "[]"

        Returns:
            List[Dataset]: A list of Dataset instances representing each favorite dataset in the workspace. 
            The content of each dataset can be accessed using the `.content` attribute.

        Raises:
            Exception: If the dataset search fails.

        Description:
            This method searches for datasets within the specified workspace.
            It sends a POST request to the '/api/v1/workspace/{workspace_id}/search' endpoint with the provided details and checks the response.

        Notes:
            - While the system is ingesting a new dataset, it will throw an error when trying to search for a dataset. Be careful while using this method shortly after an ingestion.
                You can use the "ignore_errors" parameter so your code will not be interrupted if the search fails. Use with caution.
            - The dataset search will only find published datasets.
            - If no advanced_search_parameters are given, the needed parameters for the api call will be set automatically.
            - Not all advanved parameters need to be specified. You can hand this method a dict with only the needed parameters.
            - If there is no result, the return can be empty

        Example:
            workspace = sedar.get_all_workspaces()[0]
            try:
                search_result = workspace.search_datasets("Some_dataset_title")
            except Exception as e:
                print(e)
        """
        search_results = self._search_datasets(self.id, query, advanced_search_parameters, ignore_errors)
        return [Dataset(self.connection,self.id, dataset_info["id"]) for dataset_info in search_results]
    
    ######################
    # Ontology Interface #
    ######################

    def get_all_ontologies(self) -> List[Ontology]:
        """
        Retrieves a list of all available ontologies in the SEDAR workspace.

        Args:
            None

        Returns:
            List[Ontology]: A list of ontology objects, each representing an ontology available in the SEDAR workspace.
            The content of each dataset can be accessed using the `.content` attribute.

        Raises:
            Exception: If there's a failure in retrieving the ontologies.

        Description:
            This method fetches all the ontologies present within the SEDAR workspace. 
            It sends a GET request to the /api/v1/workspaces/{workspace_id}/ontologies endpoint and checks the response.

        Notes:
            - The returned list can vary in size, from being empty (no ontologies) to containing multiple ontology entries.
            - Each ontology object in the list provides various details like author, creation date, description, 
            graph name, file name, and more.

        Example:
            try:
                ontologies = sedar.get_all_ontologies()
                for ontology in ontologies:
                    print(ontology.title)
            except Exception as e:
                print(e)
        """
        ontologies_info = self._get_all_ontologies_json(self.id)
        return [Ontology(self.connection, self.id, ontology_info["id"]) for ontology_info in ontologies_info]
    
    def get_ontology(self, ontology_id: str) -> Ontology:
        """
        Fetches a specific ontology within the workspace using the ontology's ID.

        Args:
            ontology_id (str): The unique identifier for the ontology.

        Returns:
            Ontology: An instance of the Ontology class representing the fetched ontology. 
            The content of the ontology details can be accessed using the `.content` attribute.

        Raises:
            Exception: If there's an error while fetching the ontology.

        Description:
            This method fetches the details of a specific ontology within the workspace. 
            It sends a GET request to the '/api/v1/workspaces/{workspace_id}/ontologies/{ontology_id}' 
            endpoint and returns the ontology details wrapped in an Ontology object.

        Example:
            ```python
            workspace = sedar.get_all_workspaces()[0]
            ontology_id = "1234"
            try:
                dataset = sedar.get_ontology(ontology_id)
                print(ontology.content['title'])
            except Exception as e:
                print(e)
            ```
        """
        return Ontology(self.connection, self.id, self._get_ontology_json(self.id,ontology_id)["id"])
    
    def create_ontology(self, title: str, description:str , file_path: str) -> Ontology:
        """
        Creates a new ontology within the workspace.

        Args:
            title (str): The title of the ontology.
            description (str): A description of the ontology.
            file_path (str): The path to the ontology file that is to be uploaded.

        Returns:
            Ontology: An instance of the Ontology class representing the newly created ontology. 
            The content of the ontology details can be accessed using the `.content` attribute.

        Raises:
            Exception: If there's an error while creating the ontology or if the ontology file is not found.

        Description:
            This method allows for the creation of a new ontology within the workspace. 
            It sends a POST request to the '/api/v1/workspaces/{workspace_id}/ontologies' 
            endpoint with the ontology title, description, and the ontology file. 
            After a successful creation, it returns the ontology details wrapped in an Ontology object.

        Notes:
            - Ensure that the ontology file at the provided path exists and is accessible.
            - The ontology file should be in a valid format for the creation to be successful.
            - Ensure that the user has the necessary permissions to create an ontology in the workspace.

        Example:
            ```python
            workspace = Workspace(connection, "workspace_id")
            ontology = workspace.create_ontology("My Ontology", "This is a description.", "/path/to/ontology.rdf")
            print(ontology.content)
            ```
        """
        return Ontology(self.connection, self.id, self._create_ontology(self.id, title, description, file_path)["id"])
    
    def search_ontologies(self, query_string: str, graph_name: str = "?g", is_query: bool = False, return_raw: bool = False):
        """
        Searches ontologies within the workspace using a provided query string.

        Args:
            query_string (str): The SPARQL query string used for searching.
            graph_name (str, optional): The graph name to search within. Defaults to "?g".
            is_query (bool, optional): Indicates whether the provided string is a SPARQL query. Defaults to False.
            return_raw (bool, optional): If True, returns the raw response, otherwise returns a list of triples. Defaults to False.

        Returns:
            Search Result (List[str, str, str] or JSON): If `return_raw` is False, returns a list of triples (subject, predicate, object). 
            If `return_raw` is True, returns the raw JSON response.

        Raises:
            Exception: If there's an error during the search process.

        Description:
            This method searches the ontologies within the workspace using a provided SPARQL query string.
            It sends a GET request to the '/api/v1/workspaces/{workspace_id}/ontologies/search' endpoint 
            with the provided parameters. The method can return the raw JSON response or a more structured 
            list of triples depending on the `return_raw` parameter.

        Notes:
            - The method assumes that the user is familiar with SPARQL to construct the query string.
            - If the `is_query` flag is set to False, the method will treat the `query_string` as a regular string and not as a SPARQL query.
            - The `graph_name` parameter can be used to narrow down the search to a specific ontology graph.

        Example:
            ```python
            workspace = sedar.get_all_workspaces()[0]
            triples = workspace.search_ontologies("SELECT * WHERE {?s ?p ?o}", is_query=True)
            for subject, predicate, obj in triples:
                print(subject, predicate, obj)
            ```
        """
        response = self._search_ontologies(self.id, query_string, graph_name, is_query)

        # If "return_raw" is False, we prepare the data into a list of triples
        if not return_raw:
            triples = []
            for binding in response.get("results", {}).get("bindings", []):
                subject = binding["subject"]["value"]
                predicate = binding["predicate"]["value"]
                obj = binding["object"]["value"]
                triples.append((subject, predicate, obj))
            response = triples
        
        return response
    
    def ontology_annotation_search(self, search_term: str) -> List[Annotation]:
        """
        Searches for ontology annotations based on a given search term within the workspace.

        Args:
            search_term (str): The term used for searching annotations in the ontology.

        Returns:
            List[Dict[str, str, str, str, str]: A list of dictionaries, each representing a completion match.
                - "description" (str): A description of the completion (can be None).
                - "graph" (str): The graph identifier where the completion was found.
                - "graphName" (str): The name of the ontology graph.
                - "text" (str): A textual representation of the completion.
                - "value" (str): The URI value of the completion.

        Raises:
            Exception: If there's an error during the search process.

        Description:
            This method searches for ontology completions within the workspace using the provided search term.
            It sends a GET request to the '/api/v1/workspaces/{workspace_id}/ontologies/completion' endpoint 
            with the provided search term. The method returns a list of dictionaries representing each completion match.

        Notes:
            - The method leverages the ontology search completion feature of the backend to provide autocomplete suggestions for ontology terms.
            - Each completion match contains details like the textual representation, the URI value, and the graph where it was found.

        Example:
            ```python
            workspace = sedar.get_all_workspaces()[0]
            completions = workspace.ontology_completion_search("Person")
            for completion in completions:
                print(completion["text"], completion["value"])
            ```
        """
        annotations_info = self._ontology_completion_search(self.id, search_term)
        return [Annotation(self.connection, self.id, annotation_info) for annotation_info in annotations_info]
        #return self._ontology_completion_search(self.id, search_term)
    
    ####################
    # MLflow Interface #
    ####################

    def get_all_experiments(self) -> List[Experiment]:
        """
        Retrieves all MLflow experiments associated with the workspace.

        Args:
            None

        Returns:
            List[Experiment]: A list of MLflow instances representing each experiment in the workspace.
            The content of each experiment details can be accessed using it's `.content` attribute.

        Raises:
            Exception: If there's an error during the retrieval process.

        Description:
            This method fetches all MLflow experiments associated with the current workspace.
            It sends a GET request to the '/api/v1/mlflow/listExperiments' endpoint to retrieve 
            the experiments, then filters out experiments not associated with the current workspace.
            The method returns a list of MLflow instances for each experiment in the workspace.

        Notes:
            - The method leverages the MLflow API to fetch experiments.
            - Experiments are filtered based on the "workspace_id" tag.
            - Experiments without a "workspace_id" tag are also included in the results.

        Example:
            ```python
            workspace = sedar.get_all_workspaces()[0]
            experiments = workspace.get_all_experiments()
            for experiment in experiments:
                print(experiment.content["name"])
            ```
        """
        experiments_info = self._get_all_experiments_json(self.id)
        return [Experiment(self.connection, self.id, experiment_info["experiment_id"]) for experiment_info in experiments_info]

    def get_all_registered_models(self) -> List[ExperimentModel]:
        """
        Retrieves all registered MLflow models associated with the workspace.

        Returns:
            List[ExperimentModel]: A list of MLflow instances representing each experiment in the workspace.
            The content of each model can be accessed using it's `.content` attribute.

        Raises:
            Exception: If there's an error during the retrieval process.

        Description:
            This method fetches all registered MLflow models associated with the current workspace.
            It sends a GET request to the '/api/v1/mlflow/{workspace_id}/listRegisteredModels' endpoint to retrieve 
            the models, and then returns them as a list of dictionaries.

        Notes:
            - The method leverages the MLflow API to fetch registered models.
            - Models are filtered based on the "workspace_id" tag.

        Example:
            ```python
            workspace = sedar.get_all_workspaces()[0]
            registered_models = workspace.get_all_registered_models()
            for model in registered_models:
                print(model["name"], model["version"])
            ```
        """
        models_info = self._get_all_registered_mlflow_models(self.id)["models"]
        return [ExperimentModel(self.connection, self.id, model_info) for model_info in models_info]
    
    def create_experiment(self, title: str) -> Experiment:
        """
        Creates a new MLflow experiment within the workspace.

        Args:
            title (str): The title or name of the new experiment.

        Returns:
            MLflow: An instance of the MLflow class representing the created experiment. 
            The details of the experiment can be accessed using the `.content` attribute.

        Raises:
            Exception: If there's an error during the creation process.

        Description:
            This method creates a new MLflow experiment with the specified title within the current workspace.
            It sends a POST request to the '/api/v1/mlflow/createExperiment' endpoint with the experiment title 
            and workspace ID in the payload. The method then retrieves the details of the created experiment 
            and returns it as an instance of the MLflow class.

        Notes:
            - The method leverages the MLflow API to create a new experiment.
            - Ensure that you have the necessary permissions to create experiments within the workspace.

        Example:
            ```python
            workspace = Workspace(connection, "workspace_id")
            new_experiment = workspace.create_experiment("My New Experiment")
            print(new_experiment.content["name"])
            ```
        """
        return Experiment(self.connection, self.id, self._create_experiment(self.id, title)["experiment_id"])
    
    
    #--------------------------------------------------------------
    #------------- Private methods (implementations) --------------
    #--------------------------------------------------------------
    def _get_workspace_json(self, workspace_id):
        resource_path = f"/api/v1/workspaces/{workspace_id}"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("Failed to fetch Workspace. Set the logger level to \"Error\" or below to get more detailed information.")

        return response
    
    #--------------------------------------------------------------
    def _update_workspace(self, workspace_id, title, description):
        resource_path = f"/api/v1/workspaces/{workspace_id}"
        # Define the accepted paramters by the API here
        payload = {
            "title": None,
            "description": None
        }
        
        # Get the original Workspace
        workspace = self._get_workspace_json(workspace_id)

        # Reinstate the old values from the original Workspace
        for key in payload:
            payload[key] = workspace.get(key)

        # If a new value for a parameter is given to this method, assign it
        if title is not None:
            payload["title"] = title
        if description is not None:
            payload["description"] = description

        response = self.connection._put_resource(resource_path, payload)
        if response is None:
            raise Exception("The Workspace could not be updated. Set the logger level to \"Error\" or below to get more detailed information.")

        self.logger.info("The Workspace was updated successfully.")
        return response
    
    #--------------------------------------------------------------
    def _delete_workspace(self, workspace_id):
        resource_path = f"/api/v1/workspaces/{workspace_id}"

        response = self.connection._delete_resource(resource_path)
        if response is None:
            raise Exception("Failed to delete Workspace. Set the logger level to \"Error\" or below to get more detailed information.")

        return True
    

    #--------------------------------------------------------------
    # Workspace User related Operations
    #--------------------------------------------------------------
    def _get_all_workspace_users_json(self, workspace_id):
        resource_path = f"/api/v1/workspaces/{workspace_id}/users"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("Failed to fetch Workspace Users. Set the logger level to \"Error\" or below to get more detailed information.")

        return response
    
    #--------------------------------------------------------------
    def _update_workspace_user_permissions(self, workspace_id, email, add, can_read, can_write, can_delete):
        resource_path = f"/api/v1/workspaces/{workspace_id}/users"

        # Define the accepted paramters by the API here
        payload = {
            "add": None,
            "email": None,
            "can_read": None,
            "can_write": None,
            "can_delete": None
        }

        # Get all workspace users
        workspace_users = self._get_all_workspace_users_json(workspace_id)

        # Find the correct user and extract it's parameters
        for user in workspace_users:
            if user["email"] == email:
                payload["add"] = add
                payload["can_read"] = can_read
                payload["can_write"] = can_write
                payload["can_delete"] = can_delete
                break

        # If a new value for a parameter is given to this method, assign it
        if add is not None:
            payload["add"] = add
        if can_read is not None:
            payload["can_read"] = can_read
        if can_write is not None:
            payload["can_write"] = can_write
        if can_delete is not None:
            payload["can_delete"] = can_delete
                
        response = self.connection._put_resource(resource_path, payload)
        if response is None:
            raise Exception("The User permissions could not be updated. Set the logger level to \"Error\" or below to get more detailed information.")

        self.logger.info("The User permissions were updated successfully.")
        return response
    

    #--------------------------------------------------------------
    # Dataset related Operations
    #--------------------------------------------------------------
    def _get_all_datasets_json(self, workspace_id, get_unpublished=True):
        resource_path = f"/api/v1/workspaces/{workspace_id}/datasets"
        payload = {
            "get_unpublished":get_unpublished
        }
        response = self.connection._get_resource(resource_path, payload)
        if response is None:
            raise Exception("Failed to fetch all Datasets. Set the logger level to \"Error\" or below to get more detailed information.")
        return response
    
    #--------------------------------------------------------------
    def _get_favorite_datasets_json(self, workspace_id):
        resource_path = f"/api/v1/workspaces/{workspace_id}/favorites"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("The dataset could not be indexed. Set the logger level to \"Error\" or below to get more detailed information.")
    
        self.logger.info("The dataset was succesfully Indexed.")
        return response
    
    #--------------------------------------------------------------
    def _search_datasets(self, workspace_id, query, advaned_search_parameters, ignore_errors):
        resource_path = f"/api/v1/workspaces/{workspace_id}/search"
        payload = {
            "query": query,
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

        # Check if the user specifies a dict with advanced parameters (anything but the query itself)
        if advaned_search_parameters is not None:
            # Check all given parameters inside the dict and apply it to the payload, if possible
            for key in advaned_search_parameters:
                if key in payload:
                    payload[key] = advaned_search_parameters[key]
                else:
                    # If there was found a non existing parameter in "adavanced_search_parameters", warn the user.
                    self.logger.warning(f"The parameter '{key}' is not accepted as a search parameter and is therefore not being sent.")

        
        response = self.connection._post_resource(resource_path, payload)
        # If the user specifies that no exceptions are to be thrown, only a warning will be displayed. 
        # For further explanation, see the interface-method "search_dataset"
        if response is None and ignore_errors is False:
            raise Exception("Failed to search Datasets. Set the logger level to \"Error\" or below to get more detailed information.")
        
        if response is None and ignore_errors is True:
            self.warning("The server could not handle the search reqeust, but the 'ignore_errors' parameter is set.")
        
        return response
    
    #--------------------------------------------------------------
    def _create_dataset(self, workspace_id, datasource_definition, file_paths):
        resource_path = f"/api/v1/workspaces/{workspace_id}/datasets/create"

        # Check if the datasource definition is a file path. 
        if isinstance(datasource_definition, str):
            # If it is a valid path, open the file and convert it to json
            if os.path.exists(datasource_definition):
                with open(datasource_definition, "r") as f:
                    datasource_definition = json.load(f)
            else:
                self.logger.error(f"File not found: {datasource_definition}")
                return None

        # Create the payload with the datasource definition as a json-object and the title of the dataset
        payload = {
            "title": datasource_definition.get("name", "Untitled"),
            "datasource_definition": json.dumps(datasource_definition)
        }

        # Check if "file_paths" are either a str (= Single file) or a dictionary (= Multiple files)
        # If we got a single file_path
        if isinstance(file_paths, str):
            file_name = os.path.basename(file_paths)
            # If it is a valid path, open the file and add it to "files"
            if os.path.exists(file_paths):
                files = {Commons._remove_file_extension(file_name): (file_name, open(file_paths, 'rb'), "application/vnd.ms-excel")}
            else:
                self.logger.error(f"File not found: {file_paths}")
                return None
        
        # If we got a dictionary with multiple file_paths
        elif isinstance(file_paths, dict):
            # Open every single file inside "file_paths" and add it to "files"
            for key, path in file_paths.items():
                file_name = os.path.basename(path)
                # If it is a valid path, open the file and add it to "files"
                if os.path.exists(path):
                    files[Commons._remove_file_extension(file_name)] = (file_name, open(path, 'rb'), "application/vnd.ms-excel")
                else:
                    self.logger.error(f"File not found: {path}")
                    return None

        # Throw error if we do not get a dict or str as "file_paths"
        else:
            self.logger.error(f"Invalid type for files_pats: {type(file_paths)}")
            return None

        response = self.connection._post_resource(resource_path, data=payload, files=files)

        # Close all opened files
        for file_tuple in files.values():
            file_obj = file_tuple[1]  # Get the file object from the tuple
            file_obj.close()

        if response is None:
            raise Exception("The Dataset could not be created. Set the logger level to \"Error\" or below to get more detailed information.")

        self.logger.info("Dataset was created successfully.")
        return response

    #--------------------------------------------------------------
    # Ontology related Operations
    #--------------------------------------------------------------
    def _get_all_ontologies_json(self, workspace_id):
        resource_path = f"/api/v1/workspaces/{workspace_id}/ontologies"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("Failed to fetch all Ontologies. Set the logger level to \"Error\" or below to get more detailed information.")

        return response
    
    #--------------------------------------------------------------
    def _get_ontology_json(self, workspace_id, ontology_id):
        resource_path = f"/api/v1/workspaces/{workspace_id}/ontologies/{ontology_id}" 
    
        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("Failed to fetch Ontology. Set the logger level to \"Error\" or below to get more detailed information.")
    
        return response
    
    #--------------------------------------------------------------
    def _create_ontology(self, workspace_id, title, description, file_path):
        resource_path = f"/api/v1/workspaces/{workspace_id}/ontologies"
        payload = {
            "title": title,
            "description": description
        }
        
        # Check if the given file_path is valid
        if os.path.exists(file_path):
            # Open the Ontology file and save it as "ontology_file"
            with open(file_path, 'rb') as file:
                mimetype = Commons._check_mimetype(file_path)
                ontology_file = {'file': (os.path.basename(file_path), file, mimetype)}
                
                response = self.connection._post_resource(resource_path, data=payload, files=ontology_file)
                if response is None:
                    raise Exception("The Ontology could not be created. Set the logger level to \"Error\" or below to get more detailed information.")

                self.logger.info(f"The Ontology '{title}' was created successfully.")
                return response
        else:
            self.logger.error(f"File not found: {file_path}")
            return None
    
    #--------------------------------------------------------------
    def _search_ontologies(self, workspace_id, querystring, graph_name, is_query):
        resource_path = f"/api/v1/workspaces/{workspace_id}/ontologies/search" 
        payload = {
            "querystring": querystring,
            "graph_name":graph_name,
            "is_query": is_query
        }
        response = self.connection._get_resource(resource_path, payload)
        if response is None:
            raise Exception("Failed to fetch Ontology. Set the logger level to \"Error\" or below to get more detailed information.")
    
        return response
    
    #--------------------------------------------------------------
    def _ontology_completion_search(self, workspace_id, search_term):
        resource_path = f"/api/v1/workspaces/{workspace_id}/ontologies/completion"

        payload = {
            "search_term": search_term
        }

        response = self.connection._get_resource(resource_path, payload)
        if response is None:
            raise Exception("The Ontology completion search could not be executed. Set the logger level to \"Error\" or below to get more detailed information.")

        self.logger.info("Ontology completion search was executed successfully.")
        return response


    #--------------------------------------------------------------
    # MLflow related Operations
    #--------------------------------------------------------------
    def _get_all_experiments_json(self, workspace_id):
        resource_path = f"/api/v1/mlflow/listExperiments"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("Failed to fetch all Experiments. Set the logger level to \"Error\" or below to get more detailed information.")
        
        # It should be considered to implement the "get_experiments(workspace-wide)"-call api-sided. till then, all experiments will be fetched and then extracted
        # from the return itself, which is more vulnerable to changes to the api.

        # Filter the experiments
        filtered_experiments = []
        for experiment in response.get('experiments', []):
            # Get the workspace_id from the tags, if it exists
            experiment_workspace_id = None
            for tag in experiment.get('tags', []):
                if tag['key'] == 'workspace_id':
                    experiment_workspace_id = tag['value']
                    break

            # Add the experiment to the list if it belongs to the specified workspace or if it doesn't have a workspace
            if experiment_workspace_id == workspace_id or experiment_workspace_id is None:
                filtered_experiments.append(experiment)

        return filtered_experiments
    
    #--------------------------------------------------------------
    def _create_experiment(self, workspace_id, title):
        resource_path = f"/api/v1/mlflow/createExperiment"

        payload = {
            "name": title,
            "workspace_id": workspace_id
        }

        response = self.connection._post_resource(resource_path, payload)
        if response is None:
            raise Exception("The Experiment could not be created. Set the logger level to \"Error\" or below to get more detailed information.")

        all_experiments = self._get_all_experiments_json(workspace_id)

        self.logger.info("Experiment was created successfully.")
        for experiment in all_experiments:
                if experiment["name"] == title:
                    return experiment

    #--------------------------------------------------------------
    def _deploy_mlflow_run(self,**kwargs):
        self.logger.info("This functionality is not implemented yet.")
        pass
    
    #--------------------------------------------------------------
    def _get_all_registered_mlflow_models(self, workspace_id):
        resource_path = f"/api/v1/mlflow/{workspace_id}/listRegisteredModels"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("Could not fetch registered models. Set the logger level to \"Error\" or below to get more detailed information.")

        return response
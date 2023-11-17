# Import needed python modules
from __future__ import annotations
from typing import Type
from typing import List
import json

# Import needed SEDAR modules
from .commons import Commons
from .dataset import Dataset
from .notebook import Notebook

class Experiment:
    #--------------------------------------------------------------
    def __init__(self, connection: Type[Commons], workspace_id:str, experiment_id: str):
        self.connection = connection
        self.workspace = workspace_id
        self.id = experiment_id
        self.logger = self.connection.logger
        self.content = self._get_experiment_json(self.workspace, self.id)
        self.artifact_location = self.content["artifact_location"]

    #--------------------------------------------------------------
    #--------------------- Interface methods ----------------------
    #--------------------------------------------------------------
    def delete(self) -> bool:
        """
        Deletes the current experiment.

        Returns:
            bool: True if the experiment was successfully deleted.

        Raises:
            Exception: If there's an error during the deletion process.

        Description:
            This method deletes an experiment by sending a POST request to the '/api/v1/mlflow/deleteExperiment' endpoint.

        Notes:
            - Ensure that the experiment exists and can be deleted before calling this method.
            - The method requires appropriate permissions to delete an experiment.

        Example:
        ```python
        experiment = workspace_instance.get_all_experiments()[0]
        try:
            is_deleted = experiment.delete()
            if is_deleted is True:
                print("Experiment successfully deleted.")
        except Exception as e:
            print(e)
        ```
        """
        return self._delete_experiment(self.id)

    def get_all_runs(self) -> List[ExperimentRun]:
        """
        Retrieves all the runs associated with the current experiment.

        Returns:
            List[ExperimentRun]: A list of ExperimentRun objects representing each run.

        Raises:
            Exception: If there's an error during the retrieval process.

        Description:
            This method fetches all the runs for the current experiment by sending a POST request to the '/api/v1/mlflow/searchRuns' endpoint. Each run is then transformed into an ExperimentRun object.

        Notes:
            - The method requires appropriate permissions to fetch the runs for an experiment.

        Example:
        ```python
        experiment = workspace_instance.get_all_experiments()[0]
        try:
            runs = experiment.get_all_runs()
            for run in runs:
                print(run.id, run.content["info"]["run_name"])
        except Exception as e:
            print(e)
        ```
        """
        experiments_info = self._get_experiment_runs(self.id)
        return [ExperimentRun(self.connection, self.workspace, self.id, experiment_info) for experiment_info in experiments_info]

    def create_jupyter_code(self, method: str, model: str, datasets: List[Dataset], title: str, description: str, is_public: bool, withDeploy: bool) -> Notebook:
        """
        Creates a Jupyter code for the current experiment.

        Args:
            method (str): The machine learning method used.
            model (str): The machine learning model used.
            datasets (List[Dataset]): A list of Dataset objects that are used.
            title (str): The title of the Jupyter code.
            description (str): A description for the Jupyter code.
            is_public (bool): If set to True, the Jupyter code will be public.
            withDeploy (bool): If set to True, the code will be deployed. #Seems to be unfucntional currently#

        Returns:
            Notebook: An instance of the Notebook class, representing the created Jupyter code.

        Raises:
            Exception: If there's an error during the creation process.

        Description:
            This method creates a Jupyter code for the current experiment by sending a POST request to the '/api/v1/mlflow/createJupyterCode' endpoint. The response contains details about the created Jupyter notebook, which is then transformed into a Notebook object.

        Notes:
            - The method requires appropriate permissions to create a Jupyter code.
            - Ensure that the provided datasets exist and are accessible.

        Example:
        ```python
        experiment = workspace_instance.get_all_experiments()[0]
        datasets_list = workspace_instance.get_all_datasets()
        try:
            notebook = experiment.create_jupyter_code("Unsupervised Learning", "sklearn.cluster.DBSCAN", datasets_list, "Python-Code-Deploay", "descr", True, True)
            print("Notebook created with ID:", notebook.id)
        except Exception as e:
            print(e)
        ```
        """
        notebook_info = self._create_jupyter_code(self.workspace, self.id, method, model, datasets, title, description, is_public, withDeploy)
        # A successfull code creation will return the created Notebook. We return the notebook to the user.
        return Notebook(self.connection, self.workspace, notebook_info["dataset"], notebook_info["id"])

    def deploy_run(self, run: Type[ExperimentRun], model_name: str) -> bool:
        """
        Deploys the given experiment run.

        Args:
            run (Type[ExperimentRun]): An instance of the ExperimentRun class, representing the run to be deployed.
            model_name (str): The Title for the deployment.

        Returns:
            bool: True if the run was successfully deployed.

        Raises:
            Exception: If there's an error during the deployment process.

        Description:
            This method deploys a given experiment run by sending a POST request to the '/api/v1/mlflow/deployRun' endpoint. The provided run and model name are used as parameters for the deployment.

        Notes:
            - Ensure that the provided experiment run exists and is accessible.
            - The method requires appropriate permissions to deploy a run.

        Example:
        ```python
        experiment = workspace_instance.get_all_experiments()[0]
        experiment_run = experimente.get_all_runs()[0]
        try:
            is_deployed = experiment.deploy_run(experiment_run, "my_model_name")
            if is_deployed:
                print("Run deployed successfully.")
        except Exception as e:
            print(e)
        ```
        """
        return self._deploy_mlflow_run(self.workspace, run.id, self.artifact_location, model_name)

    #--------------------------------------------------------------
    #------------- Private methods (implementations) --------------
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
    def _get_experiment_json(self, workspace_id, experiment_id): 
        # It should be considered to implement the "get_experiment"-call api-sided. till then, all experiments will be fetched and then extracted
        # from the return itself, which is more vulnerable to changes to the api.
        
        # Get all experiments
        all_experiments = self._get_all_experiments_json(workspace_id)

        # Search for the experiment with the specified id
        for experiment in all_experiments:
            if experiment["experiment_id"] == experiment_id:
                return experiment

        # If no experiment with the specified id was found, return None
        self.logger.error(f"The experiment details for experiment '{experiment_id}' could not be retrived. Most likely the experiment does not exist.")
        return None
    
    #--------------------------------------------------------------
    def _delete_experiment(self, experiment_id):
        resource_path = f"/api/v1/mlflow/deleteExperiment"
        payload = {
            "experiment_id": experiment_id
        }
        
        response = self.connection._post_resource(resource_path, payload)
        if response is None:
            raise Exception(f"The Experiment with ID '{experiment_id}' could not be deleted. Set the logger level to \"Error\" or below to get more detailed information.")
        
        self.logger.info(f"The Experiment with ID '{experiment_id}' was deleted successfully.")
        return True
    
    #--------------------------------------------------------------
    def _get_experiment_runs(self, experiment_id):
            resource_path = f"/api/v1/mlflow/searchRuns"
            payload = {
                "experiment_id": experiment_id
            }
            
            response = self.connection._post_resource(resource_path, payload)
            if response is None:
                raise Exception(f"Failed to fetch runs for the Experiment with ID '{experiment_id}'. Set the logger level to \"Error\" or below to get more detailed information.")
            
            self.logger.info(f"The runs for the Experiment with ID '{experiment_id}' were retrieved successfully.")
            return response    
    
    #--------------------------------------------------------------
    def _create_jupyter_code(self, workspace_id, experiment_id, method, model, datasets, title, description, is_public, withDeploy):
        resource_path = f"/api/v1/mlflow/createJupyterCode"
        payload = {
            "workspace_id": workspace_id,
            "session_id": self.connection.session_id,   # The session_id is just a random uuid. This replicates the
                                                        # generation that normally would be done inside the frontend code
            "experiment_id": experiment_id,
            "method": method,
            "model": model,
            "datasets": None,
            "title": title,
            "description": description,
            "is_public": is_public,
            "withDeploy": withDeploy
        }

        # Prepare the datasets to the right format for the API-Call
        formatted_datasets = []
        for dataset in datasets:
            content = dataset.content
            formatted_string = f"{content['id']}!_!seperator!_!{content['title']}!_!seperator!_!{content['datasource']['currentRevision']}"
            formatted_datasets.append(formatted_string)

        # Convert the list of formatted datasets into a JSON string
        datasets_json_str = json.dumps(formatted_datasets)

        # Add the JSON string to the payload
        payload["datasets"] = datasets_json_str

        response = self.connection._post_resource(resource_path, payload)
        if response is None:
            raise Exception(f"Failed to create Jupyter code for Experiment '{experiment_id}'. Set the logger level to \"Error\" or below to get more detailed information.")
        
        self.logger.info(f"The Jupyter code for Experiment '{experiment_id}' was created successfully.")
        return response

    #--------------------------------------------------------------
    def _deploy_mlflow_run(self, workspace_id, run_id, artifact_location, model_name):
        resource_path = f"/api/v1/mlflow/deployRun"
        payload = {
            "workspace_id":workspace_id,
            "run_id":run_id,
            "artifact_uri":artifact_location,
            "model_name":model_name
        }

        response = self.connection._post_resource(resource_path, payload)
        if response is None:
            raise Exception(f"The run '{model_name}' could not be deployed. Set the logger level to \"Error\" or below to get more detailed information.")
        
        self.logger.info(f"The run '{model_name}' was deployed successfully.")
        return True
    

#--------------------------------------------------------------
#--------------- Helper Class "ExperimentRun" -----------------
#--------------------------------------------------------------
class ExperimentRun:
    """
    Get an ExperimentRun by executing the "get_all_runs()"-call on a mlflow-instance.
    """
    #--------------------------------------------------------------
    def __init__(self, connection: Type[Commons], workspace_id: str, experiment_id: str, content):
        self.connection = connection
        self.experiment = experiment_id
        self.workspace = workspace_id
        self.logger = self.connection.logger
        self.content = content
        self.id = content["info"]["run_id"]

    #--------------------------------------------------------------
    #--------------------- Interface methods ----------------------
    #--------------------------------------------------------------
    def add_to_notebook(self, notebook: Type[Notebook]):
        return self._add_experiment_run_to_notebook(notebook.id, self.id, self.experiment)

    #--------------------------------------------------------------
    #------------- Private methods (implementations) --------------
    #--------------------------------------------------------------
    def _add_experiment_run_to_notebook(self, notebook_id, run_id, experiment_id):
        resource_path = f"/api/v1/mlflow/deployRun"
        payload = {
            "notebook_id": notebook_id,
            "run_id":run_id,
            "experiment_id": experiment_id
        }

        response = self.connection._post_resource(resource_path, payload)
        if response is None:
            raise Exception(f"The run '{run_id}' could not be added to the Notebook '{notebook_id}'. Set the logger level to \"Error\" or below to get more detailed information.")
        
        self.logger.info(f"The run '{run_id}' was added to the Notebook '{notebook_id}' successfully.")
        return True        


#--------------------------------------------------------------
#-------------- Helper Class "ExperimentModel" ----------------
#--------------------------------------------------------------
class ExperimentModel:
    """
    Get an ExperimentModel by executing the "get_all_models()"-call on a workspace-instance.
    """
    #--------------------------------------------------------------
    def __init__(self, connection: Type[Commons], workspace_id: str, content):
        self.connection = connection
        self.workspace = workspace_id
        self.logger = self.connection.logger
        self.content = content
        
        # extract members from content
        self.name = content["name"]
        self.run = content["run_id"]
        self.status = content["status"]
        self.version = content["version"]
        self.stage = content["stage"]


    #--------------------------------------------------------------
    #--------------------- Interface methods ----------------------
    #--------------------------------------------------------------
    def handle_transition(self, stage: str) -> ExperimentModel:
        """
        Handles the transition for the current machine learning model.

        Args:
            stage (str): The desired stage for the model transition.
            Possible stages: "none", "staging", "production" or "archived"

        Returns:
            ExperimentModel: An updated instance of the ExperimentModel class after the transition.

        Raises:
            Exception: If there's an error during the model transition process.

        Description:
            This method handles the transition of a given machine learning model by sending a POST request to the '/api/v1/mlflow/handleTransition' endpoint. The provided stage is used as a parameter to indicate the desired state for the model.

        Notes:
            - Ensure that the provided stage is valid and the model is in a state that allows the desired transition.
            - The method requires appropriate permissions to handle model transitions.

        Example:
        ```python
        workspace_instance = Workspace(connection_instance, workspace_id)
        experiment_model = workspace_instance.get_all_registered_models()[0]
        try:
            updated_model = experiment_model.handle_transition("production")
            print(f"Model transitioned to {updated_model.stage}.")
        except Exception as e:
            print(e)
        ```
        """
        return self._handle_transistion_of_mlflow_model(self.name, self.version, stage)


    #--------------------------------------------------------------
    #------------- Private methods (implementations) --------------
    #--------------------------------------------------------------
    def _handle_transistion_of_mlflow_model(self, name, version, stage):
        resource_path = f"/api/v1/mlflow/handleTransition"
        payload = {
            "name": name,
            "version":version,
            "stage":stage
        }

        response = self.connection._post_resource(resource_path, payload)
        if response is None:
            raise Exception("Could start model transition handling. Set the logger level to \"Error\" or below to get more detailed information.")

        self.logger.info("The model transition was executed successfully.")
        return ExperimentModel(self.connection, self.workspace, self._get_mlflow_mode_mlflow_model_json(self.workspace, name))
    

    #--------------------------------------------------------------
    def _get_mlflow_mode_mlflow_model_json(self, workspace_id, model_name):
        resource_path = f"/api/v1/mlflow/{workspace_id}/listRegisteredModels"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("Could not fetch registered models. Set the logger level to \"Error\" or below to get more detailed information.")

        for model in response["models"]:
            if model["name"] == model_name:
                return model
        


# Import needed python modules
import json
import os
from typing import Type
from typing import List

# Import all SEDAR modules
from .commons import Commons
from .user import User
from .workspace import Workspace
from .wiki import Wiki

#------------------------------------------------------------------
#-------------------------- Main Class ----------------------------
#------------------------------------------------------------------
class SedarAPI:
    #--------------------------------------------------------------
    def __init__(self, base_url):
        """
        Initializes an instance of the SedarAPI class.

        Args:
            base_url (str): The base URL of the SEDAR API.

        Returns:
            None

        Raises:
            None

        Description:
            This method initializes the SedarAPI instance with the specified base URL. 
        
        Notes:
            - Please assign base_url with the complete url, including the "http://" part.
              See the example for more help.

        Example:
            base_url = "http://127.0.0.1:5000"
            sedar = SedarAPI(base_url)
        """
        self.connection = Commons(base_url)
        self.logger = self.connection.logger

    #--------------------------------------------------------------
    # Top Level Methods
    #--------------------------------------------------------------
    def login(self, email, password) -> User:
        """
        Performs the login process for the SEDAR API.

        Args:
            email (str): The user's email address.
            password (str): The user's password.

        Returns:
            bool: True if the login was successful.

        Raises:
            Exception: If the login fails.

        Description:
            This method authenticates the user with the provided email address and password
            and allows access to the SEDAR API. It sends a POST request to the '/api/auth/login'
            endpoint and checks the response.

        Notes:
            - Make sure to initialize the SEDAR API instance with the base URL before calling this method.
            - After a successful login, the 'get_component_health()' method is automatically called
              to retrieve the status of the SEDAR API components.

        Example:
            base_url = "http://127.0.0.1:5000"
            email = "user@example.com"
            password = "password"
            sedar = SedarAPI(base_url)
            try:
                sedar.login(email, password):
            except Exception as e:
                print(e)
        """
        resource_path = "/api/auth/login"
        payload = {
            "email": email,
            "password": password
        }
        
        response = self.connection._post_resource(resource_path, payload)

        if response is None:
            raise Exception("Login failed. Set the logger level to \"Error\" or below to get more detailed information.")
        
        self.connection.user = email
        self.logger.info("Login successful")
        self.get_component_health()

        return User(self.connection, self.connection.user)
    
    #--------------------------------------------------------------
    def logout(self):
        """
        Performs the logout operation for the SEDAR API.

        Args:
            None

        Returns:
            bool: True if the logout was successful.

        Raises:
            Exception: If the logout fails.

        Description:
            This method logs out the user from the SEDAR API by sending a POST request to the '/api/auth/logout' endpoint.

        Example:
            sedar = SedarAPI(base_url)
            try:
                sedar.login(email, pwd)
                # ...
                sedar.logout():
            except Exception as e:
                print(e)
        """
        resource_path = "/api/auth/logout"

        response = self.connection._post_resource(resource_path)

        if response is None:
            raise Exception("Logout failed. Set the logger level to \"Error\" or below to get more detailed information.")
        
        self.logger.info("Logout successful")
        return True

    #--------------------------------------------------------------
    def get_stats(self, pretty_output=True):
        """
        Retrieves the statistics of the Data Lake from the SEDAR API.

        Args:
            None

        Returns:
            If pretty_ouput=False: dict: The statistics of the Data Lake.
            If pretty_output=True: Console output: The statistics of the Data Lake.

        Raises:
            Exception: If fetching the Data Lake stats fails.

        Description:
            This method retrieves the statistics of the Data Lake from the SEDAR API by sending a GET request to the '/api/stats/' endpoint.

        Example:
            sedar = SedarAPI(base_url)
            try:
                stats = sedar.get_stats()
                print(stats)
            except Exception as e:
                print(e)    
        """
        resource_path = "/api/stats/"
        
        response = self.connection._get_resource(resource_path)
        
        if response is None:
            raise Exception("Couldn't fetch Data Lake stats. Set the logger level to \"Error\" or below to get more detailed information.")
        
        if pretty_output:
            self._pretty_print_stats(response)
        else:
            return response
    
    #--------------------------------------------------------------
    def _pretty_print_stats(self, stats):
        # Header
        table =  "+---------------+-------+\n"
        table += "| Item          | Count |\n"
        table += "+---------------+-------+\n"
        
        # Fetch English labels and values
        labels = stats["labels"]["en"]
        values = stats["values"]
        
        # Populate table rows
        for label, value in zip(labels, values):
            table += f"| {label:<13} | {value:<5} |\n"
        
        # Table end
        table += "+---------------+-------+"
        
        print(table)

    #--------------------------------------------------------------
    def get_component_health(self):
        """
        Checks all SEDAR components for their status.

        Args:
            None

        Returns:
            dict: Stats of all sedar components.

        Raises:
            None

        Description:
            This method checks the vitatility of all SEDAR components and puts out warnings if one or multiple
            components seem not to be up by sending a GET request to the '/api/alive/' endpoint.

        Notes:
            - This method is automatically executed when performing the login.
            - Make sure to set the logger-level to 'INFO' or below to see the full output of this method.
            - The return value can be used to further examine the result.

        Example:
            sedar = SedarAPI(base_url)
            health = sedar.get_component_health()
            print(health) 
        """
        resource_path = "/api/alive"
        response = self.connection._get_resource(resource_path)

        if response:
            all_components_alive = all(component["isAlive"] for component in response["components"])

            if all_components_alive:
                self.logger.info("Component Check complete: All main components are alive.")
            else:
                for component in response["components"]:
                    if not component["isAlive"]:
                        self.logger.warning(f"Component {component['name']} is not alive.")
        
        return response
    
    #--------------------------------------------------------------
    def get_hive_health(self):
        """
        Checks the health status of all Hive components.

        Args:
            None

        Returns:
            dict: A dictionary containing the health status of all Hive components. The dictionary consists of a key 'components' which is a list of dictionaries. Each dictionary in the list represents a Hive component and contains:
                - 'isAlive': A boolean indicating if the component is alive.
                - 'name': The name of the Hive component.
                - 'url': The URL associated with the Hive component.

        Raises:
            None

        Description:
            This method checks the vitality of all Hive components and outputs warnings if one or multiple
            components seem not to be up by sending a GET request to the '/api/alive-hive' endpoint.

        Notes:
            - Make sure to set the logger-level to 'INFO' or below to see the full output of this method.
            - The return value can be used to further examine the result.

        Example:
            sedar = SedarAPI(base_url)
            hive_health = sedar.get_hive_health()
            print(hive_health)
        """
        resource_path = "/api/alive-hive"
        response = self.connection._get_resource(resource_path)

        if response:
            all_components_alive = all(component["isAlive"] for component in response["components"])

            if all_components_alive:
                self.logger.info("Component Check complete: All Hive components are alive.")
            else:
                for component in response["components"]:
                    if not component["isAlive"]:
                        self.logger.warning(f"Component {component['name']} is not alive.")
        
        return response
    
    #--------------------------------------------------------------
    def get_access_logs(self, download_path=None):
        """
        Retrieves the access logs from the SEDAR system.

        Args:
            download_path (str, optional): The path where the logs should be downloaded and saved as a JSON file. If not provided, the logs are returned directly.

        Returns:
            dict or bool: 
                - If no download path is provided, returns a dictionary containing the access logs.
                - If a download path is provided and the logs are successfully saved, returns True.
                - If no logs are available, a warning is logged and the method returns None.

        Raises:
            None

        Description:
            This method fetches the access logs by sending a GET request to the '/api/logs/access' endpoint. If a download path is provided, the logs are saved as a JSON file at the specified location. 

        Notes:
            - If no logs are available, a warning is logged, indicating that no accesses have been logged yet.
            - Make sure to set the logger-level to 'INFO' or below to see the full output of this method.

        Example:
            sedar = SedarAPI(base_url)
            logs = sedar.get_access_logs()
            print(logs)

            # To save logs to a file
            sedar.get_access_logs(download_path="path/to/save/logs.json")
        """
        resource_path = "/api/logs/access"

        response = self.connection._get_resource(resource_path)
        if response is None:
            return self.logger.warning("There are currently no access logs available. Most likely no accesses have been logged yet.")

        # If a download path is given, the information is stored in a file
        if download_path is not None:
            os.makedirs(os.path.dirname(download_path), exist_ok=True)
            with open(download_path, "w") as f:
                json.dump(response, f)
            self.logger.info("Access logs downloaded successfully.")
            return True
            
        return response
    
    #--------------------------------------------------------------
    def get_error_logs(self, download_path=None):
        """
        Retrieves the error logs from the SEDAR system.

        Args:
            download_path (str, optional): The path where the logs should be downloaded and saved as a JSON file. If not provided, the logs are returned directly.

        Returns:
            dict or bool: 
                - If no download path is provided, returns a dictionary containing the error logs.
                - If a download path is provided and the logs are successfully saved, returns True.
                - If no logs are available, a warning is logged and the method returns None.

        Raises:
            None

        Description:
            This method fetches the error logs by sending a GET request to the '/api/logs/error' endpoint. If a download path is provided, the logs are saved as a JSON file at the specified location. 

        Notes:
            - If no logs are available, a warning is logged, indicating that no errors have been logged yet.
            - Make sure to set the logger-level to 'INFO' or below to see the full output of this method.

        Example:
            sedar = SedarAPI(base_url)
            logs = sedar.get_error_logs()
            print(logs)

            # To save logs to a file
            sedar.get_error_logs(download_path="path/to/save/logs.json")
        """
        resource_path = "/api/logs/error"

        response = self.connection._get_resource(resource_path)
        if response is None:
            return self.logger.warning("There are currently no access logs available. Most likely no accesses have been logged yet.")

        # If a download path is given, the information is stored in a file
        if download_path is not None:
            os.makedirs(os.path.dirname(download_path), exist_ok=True)
            with open(download_path, "w") as f:
                json.dump(response, f)
            self.logger.info("Access logs downloaded successfully.")
            return True
        
        return response
    

    #--------------------------------------------------------------
    # Workspace Operations
    #--------------------------------------------------------------
    def get_all_workspaces(self) -> List[Workspace]:
        """
        Retrieves a list of all available workspaces from the SEDAR system.

        Args:
            None

        Returns:
            list of Workspace: A list containing instances of the Workspace class for each available workspace.

        Raises:
            Exception: If there's a failure in fetching the workspace details.

        Description:
            This method fetches all available workspaces by sending a GET request to the '/api/v1/workspaces/' endpoint.

        Notes:
            - This method is automatically executed when performing the login.
            - Make sure to set the logger-level to 'ERROR' or below to see detailed error messages, if any.

        Example:
            sedar = SedarAPI(base_url)
            try:
                all_workspaces = sedar.get_all_workspaces()
                for workspace in all_workspaces:
                    print(workspace.content['id'], workspace.content['title'])
            except Exception as e:
                print(e)
        """
        resource_path = "/api/v1/workspaces/"
        response = self.connection._get_resource(resource_path)
        
        if response is None:
            raise Exception("Failed to fetch Workspaces. Set the logger level to \"Error\" or below to get more detailed information.")

        return [Workspace(self.connection, workspace["id"]) for workspace in response]
    
    #--------------------------------------------------------------
    def get_workspace(self, workspace_id: str) -> Workspace:
        """
        Retrieves a specific workspace from the SEDAR system.

        Args:
            workspace_id (str): The unique identifier of the workspace to be retrieved.

        Returns:
            Workspace: An instance of the Workspace class associated with the specified workspace ID.

        Raises:
            Exception: If there's a failure in fetching the workspace details.

        Description:
            This method fetches the details of a specific workspace by sending a GET request to the '/api/v1/workspaces/{workspace_id}' endpoint.

        Notes:
            - Make sure to set the logger-level to 'ERROR' or below to see detailed error messages, if any.

        Example:
            sedar = SedarAPI(base_url)
            workspace_details = sedar.get_workspace(workspace_id)
            print(workspace.content)
            print(workspace_details.title)
        """
        resource_path = f"/api/v1/workspaces/{workspace_id}"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("Failed to fetch Workspace. Set the logger level to \"Error\" or below to get more detailed information.")

        return Workspace(self.connection, workspace_id)
    
    #--------------------------------------------------------------
    def create_workspace(self, title: str, description: str = "") -> Workspace:
        """
        Creates a new workspace in the SEDAR system.

        Args:
            title (str): The title of the new workspace.
            description (str, optional): A description for the new workspace.

        Returns:
            Workspace: An instance of the Workspace class associated with the newly created workspace. 
            The content of the workspace can be accessed using the `.content` attribute.

        Raises:
            Exception: If there's a failure in creating the workspace.

        Description:
            This method creates a new workspace by sending a POST request to the '/api/v1/workspaces/' endpoint.

        Notes:
            - Make sure to provide at least the 'title' parameter when calling this method.
            - Only 'title' and 'description' are accepted as parameters for the API. Any other parameters will be logged as warnings and will not be sent to the API.
            - Make sure to set the logger-level to 'ERROR' or below to see detailed error messages, if any.

        Example:
            sedar = SedarAPI(base_url)
            try:
                new_workspace = sedar.create_workspace(title="New Workspace", description="This is a test workspace.")
                print(new_workspace.content['id'], new_workspace.content['title'])
            except Exception as e:
                print(e)
        """
        resource_path = f"/api/v1/workspaces/"
        payload = {
            "title": title,
            "description": description
        }

        response = self.connection._post_resource(resource_path, payload)
        if response is None:
            raise Exception("The Workspace could not be created. Set the logger level to \"Error\" or below to get more detailed information.")

        self.logger.info("Workspace was created successfully.")
        #return response
        return Workspace(self.connection, response["id"])
    

    #--------------------------------------------------------------
    # User Operations
    #--------------------------------------------------------------
    def get_user(self, user_id: str) -> User:
        """
        Retrieves the details of a specific user from the SEDAR system.

        Args:
            user_id (str): The unique identifier (usually email) of the user to be retrieved.

        Returns:
            User: An instance of the User class associated with the specified user ID. 
            The content of the user details can be accessed using the `.content` attribute.

        Raises:
            Exception: If there's a failure in fetching the user details.

        Description:
            This method fetches the details of a specific user by sending a GET request to the '/api/v1/users/{user_id}' endpoint.

        Notes:
            - Make sure to provide the 'user_id' parameter when calling this method.
            - Make sure to set the logger-level to 'ERROR' or below to see detailed error messages, if any.

        Example:
            sedar = SedarAPI(base_url)
            try:
                user_details = sedar.get_user("admin")
                print(user_details.content['email'], user_details.content['firstname'])
            except Exception as e:
                print(e)
        """
        resource_path = f"/api/v1/users/{user_id}"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("Failed to fetch the User " + user_id + ". Set the logger level to \"Error\" or below to get more detailed information.")

        return User(self.connection, user_id)
    
    #--------------------------------------------------------------
    def get_current_user(self) -> User:
        """
        Retrieves the details of the currently authenticated user from the SEDAR system.

        Args:
            None

        Returns:
            User: An instance of the User class associated with the currently authenticated user. 
            The content of the user details can be accessed using the `.content` attribute.

        Raises:
            Exception: If there's a failure in fetching the user details.

        Description:
            This method fetches the details of the currently authenticated user by sending a GET request to the '/api/v1/users/current/{user_id}' endpoint.

        Notes:
            - The authenticated user's details are based on the user who is currently logged in.
            - Make sure to set the logger-level to 'ERROR' or below to see detailed error messages, if any.

        Example:
            sedar = SedarAPI(base_url)
            try:
                current_user_details = sedar.get_current_user()
                print(current_user_details.content['email'], current_user_details.content['firstname'])
            except Exception as e:
                print(e)
        """
        resource_path = f"/api/v1/users/current/{self.connection.user}"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception(f"Failed to fetch the current user({self.connection.user}). Set the logger level to \"Error\" or below to get more detailed information.")

        return User(self.connection, self.connection.user)
    
    #--------------------------------------------------------------
    def create_user(self, email: str, password: str, firstname: str, lastname: str, username: str, is_admin: bool) -> User:
        """
        Creates a new user in the SEDAR system.

        Args:
            email (str): The email address of the new user.
            password (str): The password for the new user.
            firstname (str): The first name of the new user.
            lastname (str): The last name of the new user.
            username (str): The username for the new user.
            is_admin (bool): A flag to indicate if the new user should have admin privileges.

        Returns:
            User: An instance of the User class associated with the newly created user. The content of the user details can be accessed using the `.content` attribute.

        Raises:
            Exception: If there's a failure in creating the new user.

        Description:
            This method creates a new user by sending a POST request to the '/api/v1/users/' endpoint.

        Notes:
            - Make sure to provide all necessary parameters when calling this method.
            - Make sure to set the logger-level to 'ERROR' or below to see detailed error messages, if any.

        Example:
            sedar = SedarAPI(base_url)
            try:
                new_user = sedar.create_user(email="Postman_User", password="password123", firstname="Mister", lastname="Postman", username="Postman_User", is_admin=True)
                print(new_user.content['email'], new_user.content['firstname'])
            except Exception as e:
                print(e)
        """
        resource_path = f"/api/v1/users/"
        payload = {
            "email":email,
            "password":password,
            "firstname":firstname,
            "lastname":lastname,
            "username":username,
            "is_admin":is_admin
        }

        response = self.connection._post_resource(resource_path, payload)
        if response is None:
            raise Exception("The User could not be created. Set the logger level to \"Error\" or below to get more detailed information.")

        self.logger.info(f"The user {email} was created successfully.")
        return User(self.connection, response["email"])
    
    #--------------------------------------------------------------
    # MLflow Operations
    #--------------------------------------------------------------
    def get_mlflow_parameters(self) -> List[str]:
        """
        Retrieves MLflow parameters from the SEDAR system.

        Args:
            None

        Returns:
            list of str: A list containing distinct names of MLflow parameters. If no parameters are found, an empty list is returned.

        Raises:
            Exception: If there's a failure in fetching the MLflow parameters.

        Description:
            This method fetches MLflow parameters by sending a GET request to the '/api/v1/mlflow/getParameters' endpoint.

        Notes:
            - The exact structure of the returned dictionaries depends on the details provided by the MLflow system.
            - Make sure to set the logger-level to 'ERROR' or below to see detailed error messages, if any.

        Example:
            sedar = SedarAPI(base_url)
            try:
                mlflow_params = sedar.get_mlflow_parameters()
                for param in mlflow_params:
                    print(param)
            except Exception as e:
                print(e)
        """
        resource_path = f"/api/v1/mlflow/getParameters"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("Failed to fetch the MLflow parameters. Set the logger level to \"Error\" or below to get more detailed information.")

        return response
    
    #--------------------------------------------------------------
    def get_mlflow_metrics(self) -> List[str]:
        """
        Retrieves all distinct MLflow metrics used in the SEDAR system.

        Args:
            None

        Returns:
            list of str: A list containing distinct names of MLflow metrics. If no metrics are found, an empty list is returned.

        Raises:
            Exception: If there's a failure in fetching the MLflow metrics.

        Description:
            This method fetches distinct MLflow metrics by sending a GET request to the '/api/v1/mlflow/getMetrics' endpoint.

        Notes:
            - The returned list contains distinct metric names used in the system.
            - Make sure to set the logger-level to 'ERROR' or below to see detailed error messages, if any.

        Example:
            sedar = SedarAPI(base_url)
            try:
                mlflow_metrics = sedar.get_mlflow_metrics()
                for metric in mlflow_metrics:
                    print(metric)
            except Exception as e:
                print(e)
        """
        resource_path = f"/api/v1/mlflow/getMetrics"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("Failed to fetch all Ontologies. Set the logger level to \"Error\" or below to get more detailed information.")

        return response
    
    #--------------------------------------------------------------
    # Wiki Operations
    #--------------------------------------------------------------
    def get_wiki(self, language: str="en") -> Wiki:
        """
            Retrieve the wiki content for a specified language.

            Args:
                language (str, optional): The language for which the wiki content is requested. Defaults to "english".

            Returns:
                Wiki: An instance of the Wiki class containing the retrieved content.

            Raises:
                Exception: An error occurred while fetching the Wiki content.

            Description:
                This method fetches the wiki content from the SEDAR system based on the specified language.

            Notes:
                - The default language is "english" if not specified.
                - The content of the Wiki instance can be accessed using the `.content` attribute.

            Example:
                sedar = SedarAPI(base_url)
                wiki = sedar.get_wiki()
                print(wiki.content)
            """
        return Wiki(self.connection, language) 

    #--------------------------------------------------------------
    # Jupyterhub Operations
    #--------------------------------------------------------------
    def check_jupyterhub_container(self) -> bool:
        """
        Checks if the JupyterHub container for the current user is running.

        Returns:
            bool: True if the container is running, otherwise False.

        Raises:
            Exception: An error occurred while checking the container status.

        Description:
            This method checks the status of the JupyterHub container for the current user in the SEDAR system. 
            It communicates with the Docker environment to determine if the container is actively running.

        Notes:
            - The method will return True only if the container is in the 'running' state.
            - Ensure the current user has a valid session before invoking this method.

        Example:
            sedar = SedarAPI(base_url)
            is_running = sedar.check_jupyterhub_container()
            print(is_running)
        """
        resource_path = f"/api/v1/jupyterhub/checkContainers"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("Failed to fetch Jupyterhub container status. Set the logger level to \"Error\" or below to get more detailed information.")

        return True
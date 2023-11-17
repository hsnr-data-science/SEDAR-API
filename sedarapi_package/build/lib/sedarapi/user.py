# Import needed python modules
from __future__ import annotations
from typing import Type

# Import needed SEDAR modules
from .commons import Commons

class User:
    #--------------------------------------------------------------
    def __init__(self, connection: Type[Commons], user_id):
        self.connection = connection
        self.id = user_id
        self.logger = self.connection.logger
        self.content = self._get_user_json(self.id)

        # Extract some members from the "content" attribute
        self.firstname = self.content["firstname"]
        self.lastname = self.content["lastname"]
        self.isAdmin = self.content["isAdmin"]
        self.username = self.content["username"]

    #--------------------------------------------------------------
    #--------------------- Interface methods ----------------------
    #--------------------------------------------------------------
    def update(self, new_email: str = None, firstname: str = None, lastname: str = None, username: str = None, is_admin: bool = None) -> User:
        """
        Updates the details of the specified user.

        Args:
            new_email (str, optional): The new email address for the user.
            firstname (str, optional): The new first name for the user.
            lastname (str, optional): The new last name for the user.
            username (str, optional): The new username for the user.
            is_admin (bool, optional): If the user should have admin privileges or not.

        Returns:
            User: An instance of the User class representing the updated user. 
                The details of the user can be accessed using the attributes of the returned object.

        Raises:
            Exception: If there's a failure in updating the user details.

        Description:
            This method updates the details of the current user by sending a PUT request to the appropriate API endpoint `/api/v1/users/{user_id}`.

        Notes:
            - The authenticated user needs to have admin permissions to be able to update anothers user details.

        Example:
            ```python
            user = sedar.login(usr, pwd)
            try:
                updated_user = user.update(new_email="new_email@example.com", firstname="New Firstname")
                print(updated_user.firstname)
            except Exception as e:
                print(e)
            ```
        """
        return User(self.connection, self._update_user(self.id, new_email, firstname, lastname, username, is_admin)["email"])
    
    def delete(self):
        """
        Deletes the current user.

        Returns:
            bool: `True` if the user was successfully deleted, otherwise an exception is raised.

        Raises:
            Exception: If there's a failure in deleting the user.

        Description:
            This method deletes the current user by sending a DELETE request to the appropriate API endpoint `/api/v1/users/{user_id}`.

        Note:
            - The authenticated user needs to have admin permissions to be able to delete another user.
            - Deleting a user is irreversible. Ensure that you have proper backups or are sure about the deletion before executing this method.

        Example:
            ```python
            user = sedar.get_user("username")
            try:
                success = user.delete()
                if success:
                    print("User successfully deleted!")
                else:
                    print("Failed to delete user.")
            except Exception as e:
                print(f"Error: {e}")
            ```
        """
        return self._delete_user(self.id)
    

    #--------------------------------------------------------------
    #------------- Private methods (implementations) --------------
    #-------------------------------------------------------------- 
    def _get_current_user_json(self):
        resource_path = f"/api/v1/users/current/{self.connection.user}"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception(f"Failed to fetch User '{self.connection.user}'. Set the logger level to \"Error\" or below to get more detailed information.")

        return response
    
    #--------------------------------------------------------------
    def _get_user_json(self, user_id:str):
        resource_path = f"/api/v1/users/{user_id}"

        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception(f"Failed to fetch User '{user_id}'. Set the logger level to \"Error\" or below to get more detailed information.")

        return response
    
    #--------------------------------------------------------------
    def _update_user(self, user_id, new_email, firstname, lastname, username, is_admin):
        resource_path = f"/api/v1/users/{user_id}"
        # Define the accepted paramters by the API here
        payload = {
            "email": user_id,
            "new_email": None,
            "firstname": None,
            "lastname": None,
            "username": None,
            "is_admin": None
        }
        
        # Get the original User
        user = self._get_user_json(user_id)

        # Reinstate the old values from the original Workspace
        for key in payload:
            payload[key] = user.get(key)

        # If a new value for a parameter is given to this method, assign it
        if new_email is not None:
            payload["new_email"] = new_email
        if firstname is not None:
            payload["firstname"] = firstname
        if lastname is not None:
            payload["lastname"] = lastname
        if username is not None:
            payload["username"] = username
        if is_admin is not None:
            payload["is_admin"] = is_admin

        response = self.connection._put_resource(resource_path, payload)
        if response is None:
            raise Exception(f"The User '{user_id}' could not be updated. Set the logger level to \"Error\" or below to get more detailed information.")

        self.logger.info(f"The User '{user_id}' was updated successfully.")
        return response
    
    #--------------------------------------------------------------
    def _delete_user(self, user_id):
        resource_path = f"/api/v1/users/{user_id}"

        response = self.connection._delete_resource(resource_path)
        if response is None:
            raise Exception(f"Failed to delete User '{user_id}'. Set the logger level to \"Error\" or below to get more detailed information.")

        self.logger.info(f"The User '{user_id}' was updated successfully.")
        return True
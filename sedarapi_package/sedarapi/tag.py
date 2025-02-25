# python imports
from typing import Type

# Import needed SEDAR modules
from .commons import Commons


class Tag:
    #--------------------------------------------------------------
    def __init__(self, connection: Type[Commons], workspace_id: str, dataset_id: str, tag_id: str):
        self.connection = connection
        self.workspace = workspace_id
        self.dataset = dataset_id
        self.id = tag_id
        self.logger = self.connection.logger
        self.content = self._get_tag_json(self.workspace, self.dataset, self.id)

        # Extract some members from the "content" attribute
        #self.title = self.content["title"]
        # ...
    
    #--------------------------------------------------------------
    #--------------------- Interface methods ----------------------
    #--------------------------------------------------------------
    def delete(self):
        """
        Deletes the current tag from the associated dataset.

        Returns:
            bool: `True` if the tag was successfully deleted.

        Raises:
            Exception: If there's a failure in deleting the tag.

        Description:
            This method deletes an existing tag from the associated dataset in the workspace by sending a DELETE request to the appropriate API endpoint `/api/v1/workspaces/{workspace_id}/datasets/{dataset_id}/tags/{tag_id}`.

        Note:
            Deleting a tag is irreversible. Ensure that you have proper backups or are sure about the deletion before executing this method.

        Example:
            ```python
            tag_instance = dataset.get_all_tags()[0]
            try:
                success = tag_instance.delete()
                if success:
                    print("Tag successfully deleted!")
                else:
                    print("Failed to delete tag.")
            except Exception as e:
                print(f"Error: {e}")
            ```
        """
        return self._delete_tag(self.workspace,self.dataset, self.id)
    

    #--------------------------------------------------------------
    #------------- Private methods (implementations) --------------
    #--------------------------------------------------------------
    def _get_tag_json(self, workspace_id, dataset_id, tag_id):
        resource_path = f"/api/v1/workspaces/{workspace_id}/datasets/{dataset_id}/tags/{tag_id}"
        
        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("Tag could not be retrieved. Set the logger level to \"Error\" or below to get more detailed information.")

        return response
    
    #--------------------------------------------------------------
    def _delete_tag(self, workspace_id, dataset_id, tag_id):
        resource_path = f"/api/v1/workspaces/{workspace_id}/datasets/{dataset_id}/tags/{tag_id}"

        response = self.connection._delete_resource(resource_path)
        if response is None:
            raise Exception("The Tag could not be deleted. Set the logger level to \"Error\" or below to get more detailed information.")
        
        self.logger.info("The Tag was deleted successfully.")

        return True

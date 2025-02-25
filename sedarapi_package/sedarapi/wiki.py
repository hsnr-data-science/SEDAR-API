# Import needed python modules
from __future__ import annotations
from typing import Type

# Import needed SEDAR modules
from .commons import Commons

#--------------------------------------------------------------
class Wiki:
    def __init__(self, connection: Type[Commons], language):
        self.connection = connection
        self.language = language
        self.logger = self.connection.logger
        self.content = self._get_wiki_markdown(language)


    #--------------------------------------------------------------
    #--------------------- Interface methods ----------------------
    #--------------------------------------------------------------
    def update(self, markdown: str) -> Wiki:
        """
        Updates the Wiki content.

        Args:
            markdown (str): The updated markdown content for the Wiki.

        Returns:
            Wiki: An instance of the Wiki class with the updated content.

        Raises:
            Exception: If the Wiki update operation fails.

        Description:
            This method allows users to update the Wiki content for a given language using markdown format. 
            After updating, the `content` attribute of the Wiki instance will reflect the new markdown content.

        Note:
            - The previous markdown will be completely overwritten. Be careful to include the old markdown parts you want to keep.
            - Ensure that the provided markdown is valid and properly formatted. Incorrect markdown can cause rendering issues when viewed on the platform.

        Example:
        ```python
        wiki = Wiki(connection, "en")
        updated_wiki = wiki.update("# New Wiki Content\nThis is the updated content for the Wiki.")
        print(updated_wiki.content)
        ```
        """
        self.content = self._update_wiki_markdown(self.language,markdown)
        return self
    
    #--------------------------------------------------------------
    #------------- Private methods (implementations) --------------
    #--------------------------------------------------------------
    def _get_wiki_markdown(self, language):
        resource_path = f"/api/v1/wiki/{language}"
        
        response = self.connection._get_resource(resource_path)
        if response is None:
            raise Exception("Failed to fetch the Wiki. Set the logger level to \"Error\" or below to get more detailed information.")
        
        self.logger.info("The Wiki was retrieved successfully.")
        return response["markdown"]
    
    #--------------------------------------------------------------
    def _update_wiki_markdown(self, language, markdown):
        resource_path = f"/api/v1/wiki/{language}"
        payload =  {
            "markdown": markdown
        }

        response = self.connection._put_resource(resource_path, payload)
        if response is None:
            raise Exception("The Wiki could not be updated. Set the logger level to \"Error\" or below to get more detailed information.")
        
        markdown = self._get_wiki_markdown(language)
        self.logger.info("The Wiki was updated successfully.")
        return markdown
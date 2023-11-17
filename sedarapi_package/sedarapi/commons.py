# Import needed python modules
import requests
import logging
import os
import uuid

#--------------------------------------------------------------
# Common HTTP request methods
#--------------------------------------------------------------
class Commons:
    def __init__(self, base_url):
        self.base_url = base_url
        self.user = None
        self.session = requests.Session()
        self.session_id = str(uuid.uuid4())
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SedarAPI-Logger")
    #--------------------------------------------------------------
    # Common HTTP request methods
    #--------------------------------------------------------------
    def _get_resource(self, resource_path, Data=None):
        url = self.base_url + resource_path
        try:
            response = self.session.get(url, json=Data)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                return response.content
        
        #Handle Connection-Error
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"An Exception occured!\n\tMessage:\n\tFailed to connect to the server: {str(e)}\n\tServer Response:\n\t{response.content}")

        #Handle HTTP-Error
        except requests.exceptions.RequestException as e:
            self.logger.error(f"An Exception occured!\n\tMessage:\n\tFailed to get resource {resource_path}: {str(e)}\n\tServer Response:\n\t{response.content}")

        return None
        
    #----------------------------------------------------------
    def _post_resource(self, resource_path, data=None, files=None):
        url = self.base_url + resource_path

        try:
            if files is not None:
                response = self.session.post(url, data=data, files=files)
            else:
                response = self.session.post(url, json=data)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                return response.content

        #Handle Connection-Error
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"An Exception occured!\n\tMessage:\n\tFailed to connect to the server: {str(e)}\n\tServer Response:\n\t{response.content}")

        #Handle HTTP-Error
        except requests.exceptions.RequestException as e:
            self.logger.error(f"An Exception occured!\n\tMessage:\n\tFailed to post resource {resource_path}: {str(e)}\n\tServer Response:\n\t{response.content}")

        return None

    #----------------------------------------------------------
    def _put_resource(self, resource_path, data=None, files=None):
        url = self.base_url + resource_path

        try:
            if files is not None:
                response = self.session.put(url, data=data, files=files)
            else:
                response = self.session.put(url, json=data)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                return response.content

        #Handle Connection-Error
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"An Exception occured!\n\tMessage:\n\tFailed to connect to the server: {str(e)}\n\tServer Response:\n\t{response.content}")

        #Handle HTTP-Error
        except requests.exceptions.RequestException as e:
            self.logger.error(f"An Exception occured!\n\tMessage:\n\tFailed to post resource {resource_path}: {str(e)}\n\tServer Response:\n\t{response.content}")

        return None

    #----------------------------------------------------------    
    def _patch_resource(self, resource_path, data=None):
        url = self.base_url + resource_path
        try:
            response = self.session.patch(url, json=data)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                return response.content

        #Handle Connection-Error
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"An Exception occured!\n\tMessage:\n\tFailed to connect to the server: {str(e)}\n\tServer Response:\n\t{response.content}")

        #Handle HTTP-Error
        except requests.exceptions.RequestException as e:
            self.logger.error(f"An Exception occured!\n\tMessage:\n\tFailed to patch resource {resource_path}: {str(e)}\n\tServer Response:\n\t{response.content}")

        return None

    #----------------------------------------------------------
    def _delete_resource(self, resource_path, data=None):
        url = self.base_url + resource_path
        try:
            response = self.session.delete(url, json=data)
            response.raise_for_status()
            return response.content

        #Handle Connection-Error
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"An Exception occured!\n\tMessage:\n\tFailed to connect to the server: {str(e)}\n\tServer Response:\n\t{response.content}")

        #Handle HTTP-Error
        except requests.exceptions.RequestException as e:
            self.logger.error(f"An Exception occured!\n\tMessage:\n\tFailed to delete resource {resource_path}: {str(e)}\n\tServer Response:\n\t{response.content}")

        return None
    
    #--------------------------------------------------------------
    # Common helper methods
    #--------------------------------------------------------------
    @staticmethod
    def _check_mimetype(file_path):
        """
        Tries to identify the mime-type for multi-part requests to the API.

        Args:
            file_path (str): The path of a given file, including it's file type.

        Returns:
            str: mime_type of the given file_path or a blank string "" if file type is unknown.

        Raises:
            None
        """
        mime_types = {
            # Text und Dokumente
            ".txt": "text/plain",
            ".csv": "text/csv",
            ".log": "text/plain",
            ".json": "application/json",
            ".xml": "application/xml",
            ".html": "text/html",
            ".htm": "text/html",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".ppt": "application/vnd.ms-powerpoint",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",

            # Ontologie und Semantic Web
            ".rdf": "application/rdf+xml",
            ".ttl": "text/turtle",
            ".nt": "application/n-triples",
            ".n3": "text/n3",
            ".jsonld": "application/ld+json",
            ".owl": "application/owl+xml",

            # Datenbanken und Data Warehouses
            ".sql": "application/sql",
            ".db": "application/x-sqlite3",
            ".mdb": "application/vnd.ms-access",
            ".accdb": "application/vnd.ms-access",

            # Bilder
            ".jpeg": "image/jpeg",
            ".jpg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".tiff": "image/tiff",
            ".ico": "image/vnd.microsoft.icon",
            ".webp": "image/webp",

            # Audio und Video
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".mp4": "video/mp4",
            ".webm": "video/webm",
            ".avi": "video/x-msvideo",
            ".mkv": "video/x-matroska",

            # Archivdateien
            ".zip": "application/zip",
            ".rar": "application/vnd.rar",
            ".7z": "application/x-7z-compressed",
            ".tar": "application/x-tar",
            ".gz": "application/gzip",

            # Andere
            ".parquet": "application/octet-stream",  # Es gibt keinen offiziellen MIME-Typ für Parquet
            ".avro": "avro/binary",
            ".protobuf": "application/x-protobuf"
        }
    
        file_extension = os.path.splitext(file_path)[1]
        return mime_types.get(file_extension, "")
    
    #--------------------------------------------------------------
    @staticmethod
    def _remove_file_extension(file_name):
        return os.path.splitext(file_name)[0]

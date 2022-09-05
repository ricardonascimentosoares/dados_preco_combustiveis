from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class GoogleDriverHelper:

    def __init__(self):
        # Below code does the authentication
        # part of the code
        gauth = GoogleAuth()

        # Creates local webserver and auto
        # handles authentication.
        gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(gauth)

    def save_file(self, filename):
        gfile = self.drive.CreateFile({'parents': [{'id': '1pCk7DzcCkHyzt8R8i3DgHRhljEkBaK5P'}], 'id': '1t-ce8UL2jny8HFAlGf_R3Znwzb9HyNxS'})
        # Read file and set it as the content of this instance.
        gfile.SetContentFile(filename)
        gfile.Upload() # Upload the file.


drive = GoogleDriverHelper()
drive.save_file('dados_preco_combustiveis_final.csv')
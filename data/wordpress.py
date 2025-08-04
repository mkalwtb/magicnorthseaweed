from ftplib import FTP_TLS
from pathlib import Path
from data.plotting import website_folder
import passwords

ftp_host = "surfai.nl"
ftp_user = "PC@surfai.nl"
ftp_pass = passwords.wordpress

local_file = website_folder / "tables" / "table_ZV.html"
remote_folder = "/home3/vcxyzymy/public_html"
remote_filename = "table_ZV.html"

# Maak een beveiligde verbinding via FTPS
ftps = FTP_TLS()
ftps.connect(ftp_host, 21)
ftps.login(user=ftp_user, passwd=ftp_pass)
ftps.prot_p()  # activeer dataverkeer via TLS

# Ga naar juiste map en upload bestand
ftps.cwd(remote_folder)
with open(local_file, "rb") as f:
    ftps.storbinary(f"STOR {remote_filename}", f)

ftps.quit()
print(f"Bestand geüpload via FTPS naar: {remote_folder}/{remote_filename}")
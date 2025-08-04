import ftplib
import passwords
from data.plotting import website_folder

FTP_HOST = "surfai.nl"
FTP_USER = "PC@surfai.nl"
FTP_PASS = passwords.wordpress

LOCAL_FILE = website_folder / "tables" / "table_ZV.html"
REMOTE_FILE = "public_html/mnsw/table_ZV.html"

session = ftplib.FTP_TLS()
session.connect(FTP_HOST, 21, timeout=10)
session.login(FTP_USER, FTP_PASS)
session.prot_p()  # Switch to secure data connection
session.set_pasv(True)

print(session.pwd())

with open(LOCAL_FILE, "rb") as file:
    session.storbinary(f"STOR {REMOTE_FILE}", file)

session.quit()

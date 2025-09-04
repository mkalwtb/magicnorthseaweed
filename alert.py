from dataclasses import dataclass

import pandas as pd

from data import spots
from data.spots import Spot


@dataclass
class AlertFilter:
    spot: Spot
    rating_threshold: int
    email: str
    ID: int

class AlertLog:
    """"
    Representation of a saved email log dataframe, containing to whom and when an email was sent.

    Data is stored in a pandas DataFrame with columns: ['timestamp', 'spot', 'rating', 'email', 'alert_timestamp']

    Automatically saves to a pickle file when modified.
    """

    def __init__(self, file="alert_log.pkl"):
        import pandas as pd
        from pathlib import Path

        self.file = Path(file)
        self.columns = ['timestamp', 'spot', 'rating', 'email', 'alert_timestamp']
        if self.file.exists():
            self.df = pd.read_pickle(self.file)
        else:
            self.df = pd.DataFrame(columns=self.columns)
            self.save()

    def save(self):
        self.df.to_pickle(self.file)

    def log_alert(self, spot: str, rating: int, email: str, alert_timestamp: str):
        import pandas as pd
        from datetime import datetime

        new_entry = pd.DataFrame([{
            'timestamp': datetime.now(),
            'spot': spot,
            'rating': rating,
            'email': email,
            'alert_timestamp': alert_timestamp
        }])
        # print(f"Logging email: {new_entry.to_dict(orient='records')[0]}")
        self.df = pd.concat([self.df, new_entry], ignore_index=True)
        self.save()

email_log = AlertLog()

def content_generator(data: pd.DataFrame) -> str:
    """ Generate the content of the alert email based on the provided data."""
    max_rating = data['rating'].max()
    max_time = data['rating'].idxmax()
    content = f"Alert: Surf rating has reached {max_rating:.1f} at {max_time}.\n\n"
    content += "Recent ratings:\n"
    recent_data = data[data.index >= (max_time - pd.Timedelta(hours=6))]
    content += recent_data[['rating', 'hoogte-v2']].to_string()
    return content

FROM = 'lsaseem93@gmail.com'

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(to: str, subject: str, content: str):
    smtp_server = "mail.surfai.nl"
    port = 465  # SSL/TLS
    sender_email = "alert@surfai.nl"
    password = os.getenv("Surf4Everyone%")  # keep password in env variable

    # Bouw de e-mail
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to

    plain_text = content
    html_text = f"<html><body><p>{content}</p></body></html>"

    message.attach(MIMEText(plain_text, "plain"))
    message.attach(MIMEText(html_text, "html"))

    # Verstuur
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, to, message.as_string())
        print(f"✅ Email sent to {to}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


def check(data: pd.DataFrame, spot: Spot, alert_filters: list[AlertFilter]):
    """ Check if any alerts should be sent based on the provided data and alert filters."""
    from datetime import datetime, timedelta

    now = datetime.now()
    one_day_ago = now - timedelta(days=1)

    for alert_filter in alert_filters:
        if alert_filter.spot.name != spot.name:
            continue

        # Check if the rating exceeds the threshold
        if data['rating'].max() >= alert_filter.rating_threshold:
            alert_time = data[data['rating'] >= alert_filter.rating_threshold].index[0]

            # Check if an email was sent in the last 24 hours for this spot and email
            recent_emails = email_log.df[
                (email_log.df['spot'] == spot.name) &
                (email_log.df['email'] == alert_filter.email)
                # (email_log.df['alert_timestamp'] >= one_day_ago)  # todo enable
            ]

            if not recent_emails.empty:  # todo remove not
                # Send email (placeholder for actual email sending logic)
                print(f"Alert email to {alert_filter.email} for spot {spot.name} with rating {data['rating'].max():.1f} at {alert_time}")

                # Log the sent email
                send_email(
                    to=alert_filter.email,
                    subject=f"Surf Alert for {spot.name}: Rating {data['rating'].max():.1f}",
                    content=content_generator(data)
                )
                email_log.log_alert(spot.name, data['rating'].max(), alert_filter.email, alert_time)
            else:
                print(f"Alert email already sent to {alert_filter.email} for spot {spot.name} in the last 24 hours.")

MEES = AlertFilter(spots.ZV, rating_threshold=6, email="laseem93@gmail.com", ID=0)
FILTERS = [MEES]
import smtplib
from email.message import EmailMessage

from settingsConfig import settingsConfig
from helpers.fileSystem import FileSystem


class _EmailSender:
    def __init__(self):
        self.__settings = settingsConfig.SMTPSettings

    def sendEmail(self, email, subject, message, files=None):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.__settings["email"]
        msg['To'] = email
        msg.set_content(message)

        if isinstance(files, list) and files:
            for path in files:
                with open(path, "rb") as file:
                    msg.add_attachment(
                        file.read(),
                        filename=FileSystem.getFilename(path, True),
                        maintype="application",
                        subtype="zip"
                    )

        smtp = smtplib.SMTP_SSL(self.__settings["host"], self.__settings["port"])
        smtp.login(self.__settings["email"], self.__settings["password"])
        smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        smtp.quit()


emailSender = _EmailSender()

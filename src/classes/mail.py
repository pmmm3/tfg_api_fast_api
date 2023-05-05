import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from src.database import smtp_server, smtp_port, smtp_username, smtp_password


class EmailManager:
    _instance = None

    def __new__(
        cls, smtp_server: str, smtp_port: int, smtp_username: str, smtp_password: str
    ):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.smtp_server = smtp_server
            cls._instance.smtp_port = smtp_port
            cls._instance.smtp_username = smtp_username
            cls._instance.smtp_password = smtp_password
        return cls._instance

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        link: str = None,
        attachment_path: str = None,
    ) -> str:
        # Crear el objeto de mensaje multipart para adjuntar el enlace
        message = MIMEMultipart()
        message["From"] = self.smtp_username
        message["To"] = to
        message["Subject"] = subject

        # Crear el cuerpo del correo electrónico como texto y adjuntar el enlace (si se proporciona)
        message.attach(MIMEText(body, "plain"))
        if link:
            message.attach(MIMEText(f'<a href="{link}">{link}</a>', "html"))

        # Adjuntar el archivo (si se proporciona)
        if attachment_path:
            with open(attachment_path, "r") as file:
                attachment = MIMEApplication(file.read(), _subtype="text")
                attachment.add_header(
                    "Content-Disposition", "attachment", filename=attachment_path
                )
                message.attach(attachment)

        # Enviar el correo electrónico usando el servidor SMTP
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.smtp_username, to, message.as_string())

        return "Correo electrónico enviado"


email_manager = EmailManager(smtp_server, smtp_port, smtp_username, smtp_password)

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from jinja2 import Template

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
        content: str,
        attachment_path: str = None,
    ) -> str:
        # Crear el objeto de mensaje multipart para adjuntar el enlace
        message = MIMEMultipart()
        message["From"] = self.smtp_username
        message["To"] = to
        message["Subject"] = subject

        # Añadir el contenido del mensaje
        message.attach(MIMEText(content, "html"))

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

    async def send_activate_account(self, to: str, token: str = None):
        # Cargar la plantilla desde el archivo
        with open("src/templates/activate_account.html", "r") as f:
            template = Template(f.read())

        # Renderizar la plantilla con los valores personalizados
        subject = "Activación de cuenta en PsicoSalud"
        content = template.render()

        # Enviar el correo electrónico
        await self.send_email(to, subject, content)


email_manager = EmailManager(smtp_server, smtp_port, smtp_username, smtp_password)

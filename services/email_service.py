"""
Email service for sending verification and notification emails
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
import logging
from jinja2 import Template
import ssl

logger = logging.getLogger(__name__)


class EmailService:
    """Service class for sending emails."""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "richardtekere02@gmail.com")
        self.app_name = os.getenv("APP_NAME", "AI Data Assistant")
        self.app_url = os.getenv("APP_URL", "http://localhost:8501")

        # Email templates
        self.templates = self._load_email_templates()

    def _load_email_templates(self) -> dict:
        """Load email templates."""
        return {
            "verification": self._get_verification_template(),
            "password_reset": self._get_password_reset_template(),
            "welcome": self._get_welcome_template(),
        }

    def _get_verification_template(self) -> Template:
        """Get email verification template."""
        return Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Email - {{ app_name }}</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #2563EB, #0D9488); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                .button { display: inline-block; background: #2563EB; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
                .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ app_name }}</h1>
                    <p>Email Verification Required</p>
                </div>
                <div class="content">
                    <h2>Hello {{ username }}!</h2>
                    <p>Thank you for registering with {{ app_name }}. To complete your registration, please verify your email address by clicking the button below:</p>
                    
                    <div class="text-center">
                        <a href="{{ verification_url }}" class="button">Verify Email Address</a>
                    </div>
                    
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p class="word-break-break-all background-f0f0f0 padding-10px border-radius-5px">{{ verification_url }}</p>
                    
                    <div class="warning">
                        <strong>Important:</strong> This verification link will expire in 24 hours. If you don't verify your email within this time, you'll need to request a new verification email.
                    </div>
                    
                    <p>If you didn't create an account with {{ app_name }}, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 {{ app_name }}. All rights reserved.</p>
                    <p>This is an automated email, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """)

    def _get_password_reset_template(self) -> Template:
        """Get password reset template."""
        return Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password - {{ app_name }}</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #DC2626, #EA580C); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                .button { display: inline-block; background: #DC2626; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
                .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ app_name }}</h1>
                    <p>Password Reset Request</p>
                </div>
                <div class="content">
                    <h2>Hello {{ username }}!</h2>
                    <p>We received a request to reset your password for your {{ app_name }} account. Click the button below to reset your password:</p>
                    
                    <div class="text-center">
                        <a href="{{ reset_url }}" class="button">Reset Password</a>
                    </div>
                    
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p class="word-break-break-all background-f0f0f0 padding-10px border-radius-5px">{{ reset_url }}</p>
                    
                    <div class="warning">
                        <strong>Important:</strong> This password reset link will expire in 1 hour. If you don't reset your password within this time, you'll need to request a new reset link.
                    </div>
                    
                    <p>If you didn't request a password reset, please ignore this email. Your password will remain unchanged.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 {{ app_name }}. All rights reserved.</p>
                    <p>This is an automated email, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """)

    def _get_welcome_template(self) -> Template:
        """Get welcome email template."""
        return Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to {{ app_name }}!</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #16A34A, #0D9488); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                .button { display: inline-block; background: #16A34A; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
                .feature { background: white; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #16A34A; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ app_name }}</h1>
                    <p>Welcome aboard! 🎉</p>
                </div>
                <div class="content">
                    <h2>Hello {{ username }}!</h2>
                    <p>Welcome to {{ app_name }}! Your account has been successfully verified and you're now ready to start exploring the power of AI-driven data analysis.</p>
                    
                    <div class="text-center">
                        <a href="{{ app_url }}" class="button">Get Started</a>
                    </div>
                    
                    <h3>What you can do with {{ app_name }}:</h3>
                    
                    <div class="feature">
                        <strong>📊 Advanced Data Analysis</strong><br>
                        Upload your datasets and get comprehensive statistical insights, correlation analysis, and automated pattern recognition.
                    </div>
                    
                    <div class="feature">
                        <strong>📈 Interactive Visualizations</strong><br>
                        Create beautiful charts, graphs, and dashboards with just a few clicks or natural language commands.
                    </div>
                    
                    <div class="feature">
                        <strong>🤖 AI-Powered Insights</strong><br>
                        Ask questions about your data in plain English and get intelligent, automated analysis and recommendations.
                    </div>
                    
                    <div class="feature">
                        <strong>📋 Professional Reports</strong><br>
                        Generate comprehensive EDA reports and export your findings in multiple formats.
                    </div>
                    
                    <p>If you have any questions or need assistance, feel free to reach out to our support team.</p>
                    
                    <p>Happy analyzing!</p>
                    <p><strong>The {{ app_name }} Team</strong></p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 {{ app_name }}. All rights reserved.</p>
                    <p>This is an automated email, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """)

    def send_email(
        self, to_email: str, subject: str, html_content: str, text_content: str = None
    ) -> bool:
        """Send an email."""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning(
                    "SMTP credentials not configured. Email sending disabled."
                )
                return False

            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject

            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain")
                msg.attach(text_part)

            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False

    def send_verification_email(
        self, to_email: str, username: str, verification_token: str
    ) -> bool:
        """Send email verification email."""
        verification_url = f"{self.app_url}/verify_email?token={verification_token}"

        html_content = self.templates["verification"].render(
            username=username, verification_url=verification_url, app_name=self.app_name
        )

        text_content = f"""
        Hello {username}!
        
        Thank you for registering with {self.app_name}. To complete your registration, please verify your email address by visiting:
        
        {verification_url}
        
        This verification link will expire in 24 hours.
        
        If you didn't create an account with {self.app_name}, please ignore this email.
        
        Best regards,
        The {self.app_name} Team
        """

        return self.send_email(
            to_email=to_email,
            subject=f"Verify Your Email - {self.app_name}",
            html_content=html_content,
            text_content=text_content,
        )

    def send_password_reset_email(
        self, to_email: str, username: str, reset_token: str
    ) -> bool:
        """Send password reset email."""
        reset_url = f"{self.app_url}/reset_password?token={reset_token}"

        html_content = self.templates["password_reset"].render(
            username=username, reset_url=reset_url, app_name=self.app_name
        )

        text_content = f"""
        Hello {username}!
        
        We received a request to reset your password for your {self.app_name} account. Click the link below to reset your password:
        
        {reset_url}
        
        This password reset link will expire in 1 hour.
        
        If you didn't request a password reset, please ignore this email.
        
        Best regards,
        The {self.app_name} Team
        """

        return self.send_email(
            to_email=to_email,
            subject=f"Reset Your Password - {self.app_name}",
            html_content=html_content,
            text_content=text_content,
        )

    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """Send welcome email after email verification."""
        html_content = self.templates["welcome"].render(
            username=username, app_url=self.app_url, app_name=self.app_name
        )

        text_content = f"""
        Hello {username}!
        
        Welcome to {self.app_name}! Your account has been successfully verified and you're now ready to start exploring the power of AI-driven data analysis.
        
        Get started by visiting: {self.app_url}
        
        What you can do with {self.app_name}:
        - Advanced Data Analysis
        - Interactive Visualizations
        - AI-Powered Insights
        - Professional Reports
        
        Happy analyzing!
        The {self.app_name} Team
        """

        return self.send_email(
            to_email=to_email,
            subject=f"Welcome to {self.app_name}! 🎉",
            html_content=html_content,
            text_content=text_content,
        )

    def test_email_configuration(self) -> bool:
        """Test email configuration by sending a test email."""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP credentials not configured")
                return False

            # Test connection
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(self.smtp_username, self.smtp_password)
                logger.info("SMTP connection test successful")
                return True

        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False

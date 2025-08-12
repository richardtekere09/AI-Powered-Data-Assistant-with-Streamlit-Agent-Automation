# services/email_service.py
"""
Email service for sending verification and notification emails
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.app_name = "AI Data Assistant"
        self.base_url = os.getenv("BASE_URL", "http://localhost:8501")

    def _send_email(
        self, to_email: str, subject: str, html_content: str, text_content: str = None
    ) -> bool:
        """
        Send email using SMTP.

        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (optional)

        Returns:
            bool: True if email sent successfully
        """
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured. Skipping email send.")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, "plain")
                msg.attach(text_part)

            # Add HTML content
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Connect and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_verification_email(
        self, to_email: str, username: str, verification_token: str
    ) -> bool:
        """
        Send email verification email.

        Args:
            to_email: User email
            username: Username
            verification_token: Verification token

        Returns:
            bool: True if email sent successfully
        """
        subject = f"Welcome to {self.app_name} - Verify Your Email"
        verification_url = (
            f"{self.base_url}/auth/email_verification?token={verification_token}"
        )

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Email Verification</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2563EB, #0D9488); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #2563EB; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .footer {{ margin-top: 30px; text-align: center; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Welcome to {self.app_name}!</h1>
                </div>
                <div class="content">
                    <h2>Hi {username},</h2>
                    <p>Thank you for registering with {self.app_name}! We're excited to help you unlock the power of your data with AI-driven insights.</p>
                    
                    <p>To complete your registration and start analyzing your data, please verify your email address by clicking the button below:</p>
                    
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" class="button">✅ Verify Email Address</a>
                    </p>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="background: #e9ecef; padding: 10px; border-radius: 5px; word-break: break-all;">
                        {verification_url}
                    </p>
                    
                    <p><strong>This verification link will expire in 24 hours.</strong></p>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                    
                    <h3>🎯 What you can do with {self.app_name}:</h3>
                    <ul>
                        <li><strong>📊 Advanced Analytics:</strong> Statistical analysis, correlations, and hypothesis testing</li>
                        <li><strong>📈 Smart Visualizations:</strong> Interactive charts and dashboards</li>
                        <li><strong>🤖 AI Insights:</strong> Natural language queries and pattern recognition</li>
                        <li><strong>📋 Automated Reports:</strong> Comprehensive EDA reports with one click</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>If you didn't create this account, please ignore this email.</p>
                    <p>© 2024 {self.app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to {self.app_name}!
        
        Hi {username},
        
        Thank you for registering! Please verify your email address by visiting:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create this account, please ignore this email.
        """

        return self._send_email(to_email, subject, html_content, text_content)

    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """
        Send welcome email after successful verification.

        Args:
            to_email: User email
            username: Username

        Returns:
            bool: True if email sent successfully
        """
        subject = f"🎉 Welcome to {self.app_name} - Let's Get Started!"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #16A34A, #0D9488); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #16A34A; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .feature {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #2563EB; }}
                .footer {{ margin-top: 30px; text-align: center; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Email Verified Successfully!</h1>
                </div>
                <div class="content">
                    <h2>Welcome aboard, {username}!</h2>
                    <p>Your email has been verified and your account is now active. You're ready to start exploring your data with the power of AI!</p>
                    
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{self.base_url}" class="button">🚀 Start Analyzing Data</a>
                    </p>
                    
                    <h3>🔥 Quick Start Guide:</h3>
                    
                    <div class="feature">
                        <strong>1. 📁 Upload Your Data</strong><br>
                        Upload CSV or Excel files and get instant insights
                    </div>
                    
                    <div class="feature">
                        <strong>2. 🤖 Ask AI Questions</strong><br>
                        Use natural language to explore patterns and correlations
                    </div>
                    
                    <div class="feature">
                        <strong>3. 📊 Generate Reports</strong><br>
                        Create comprehensive EDA reports with one click
                    </div>
                    
                    <div class="feature">
                        <strong>4. 📈 Create Visualizations</strong><br>
                        Build interactive charts and dashboards
                    </div>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                    
                    <p><strong>Need help?</strong> Our AI assistant is ready to guide you through any analysis. Just ask questions in plain English!</p>
                </div>
                <div class="footer">
                    <p>Happy analyzing! 🎯</p>
                    <p>© 2024 {self.app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to {self.app_name}!
        
        Hi {username},
        
        Your email has been verified successfully! You're now ready to start analyzing your data.
        
        Get started: {self.base_url}
        
        Quick Start:
        1. Upload your CSV or Excel files
        2. Ask AI questions about your data
        3. Generate comprehensive reports
        4. Create beautiful visualizations
        
        Happy analyzing!
        """

        return self._send_email(to_email, subject, html_content, text_content)

    def send_password_reset_email(
        self, to_email: str, username: str, reset_token: str
    ) -> bool:
        """
        Send password reset email.

        Args:
            to_email: User email
            username: Username
            reset_token: Password reset token

        Returns:
            bool: True if email sent successfully
        """
        subject = f"{self.app_name} - Password Reset Request"
        reset_url = f"{self.base_url}/auth/reset_password?token={reset_token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #F59E0B, #DC2626); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #DC2626; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .warning {{ background: #FEF2F2; border: 1px solid #FCA5A5; color: #DC2626; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ margin-top: 30px; text-align: center; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Hi {username},</h2>
                    <p>We received a request to reset your password for your {self.app_name} account.</p>
                    
                    <p>If you requested this password reset, click the button below to create a new password:</p>
                    
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" class="button">🔑 Reset Password</a>
                    </p>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="background: #e9ecef; padding: 10px; border-radius: 5px; word-break: break-all;">
                        {reset_url}
                    </p>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong>
                        <ul style="margin: 10px 0 0 20px;">
                            <li>This reset link will expire in 1 hour</li>
                            <li>For security, you can only use this link once</li>
                            <li>If you didn't request this reset, please ignore this email</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>If you didn't request this password reset, your account is still secure.</p>
                    <p>© 2024 {self.app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Password Reset Request - {self.app_name}
        
        Hi {username},
        
        We received a request to reset your password.
        
        Reset your password: {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this reset, please ignore this email.
        """

        return self._send_email(to_email, subject, html_content, text_content)

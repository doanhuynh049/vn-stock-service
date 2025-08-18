import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import jinja2
from pathlib import Path
from utils.api_logger import APILogger

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, smtp_host: str, smtp_port: int, smtp_user: str, smtp_pass: str, 
                 mail_from: Optional[str] = None, smtp_tls: bool = True):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        self.mail_from = mail_from or smtp_user
        self.smtp_tls = smtp_tls
        
        # Initialize API logger
        self.api_logger = APILogger()
        
        # Setup Jinja2 template environment
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Add custom filters
        self.jinja_env.filters['strftime'] = self._strftime_filter

    def send_stock_advisory_email(self, stock_advisory: Dict[str, Any], recipient: str) -> bool:
        """Send individual stock advisory email"""
        try:
            template = self.jinja_env.get_template("stock_detail.html")
            
            # Prepare template data
            template_data = {
                "ticker": stock_advisory["position"]["ticker"],
                "exchange": stock_advisory["position"]["exchange"],
                "price": stock_advisory["market_data"]["price"],
                "change": stock_advisory["market_data"].get("change", 0),
                "change_pct": stock_advisory["market_data"].get("change_pct", 0),
                "shares": stock_advisory["position"]["shares"],
                "avg_price": stock_advisory["position"]["avg_price"],
                "target_price": stock_advisory["position"]["target_price"],
                "pct_to_target": ((stock_advisory["position"]["target_price"] / stock_advisory["market_data"]["price"]) - 1) * 100,
                "performance": stock_advisory["performance"],
                "technical": stock_advisory.get("technical", {}),
                "fundamentals": stock_advisory["market_data"].get("fundamentals", {}),
                "advisory": stock_advisory["advisory"],
                "generated_at": stock_advisory["generated_at"]
            }
            
            html_content = template.render(**template_data)
            
            subject = f"📈 {stock_advisory['position']['ticker']} Stock Advisory - {datetime.now().strftime('%B %d, %Y')}"
            
            return self.send_email(recipient, subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending stock advisory email: {e}")
            return False

    def send_portfolio_overview_email(self, portfolio_advisory: Dict[str, Any], 
                                    holdings_data: Dict[str, Any], recipient: str) -> bool:
        """Send portfolio overview email"""
        try:
            template = self.jinja_env.get_template("portfolio_overview.html")
            
            # Prepare template data
            template_data = {
                "owner": holdings_data.get("owner", "Portfolio"),
                "portfolio_metrics": portfolio_advisory["portfolio_metrics"],
                "advisory": portfolio_advisory["advisory"],
                "generated_at": portfolio_advisory["generated_at"]
            }
            
            html_content = template.render(**template_data)
            
            subject = f"📊 Portfolio Overview - {datetime.now().strftime('%B %d, %Y')}"
            
            return self.send_email(recipient, subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending portfolio overview email: {e}")
            return False

    def send_all_stocks_advisory_email(self, stock_advisories: List[Dict[str, Any]], 
                                     portfolio_data: Dict[str, Any], 
                                     portfolio_metrics: Dict[str, Any],
                                     recipient: str) -> bool:
        logger.info(f"Sending consolidated all-stocks advisory email to {recipient} with {len(stock_advisories)} advisories")
        """Send consolidated email with all stock advisories"""
        try:
            template = self.jinja_env.get_template("all_stocks_advisory.html")
            
            # Prepare template data
            template_data = {
                "date": datetime.now().strftime('%B %d, %Y'),
                "portfolio": portfolio_data,
                "portfolio_metrics": portfolio_metrics,
                "stock_advisories": stock_advisories,
                "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            html_content = template.render(**template_data)
            
            subject = f"📈 Daily Stock Advisory - {len(stock_advisories)} Positions - {datetime.now().strftime('%B %d, %Y')}"
            
            return self.send_email(recipient, subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending all-stocks advisory email: {e}")
            return False

    def send_email(self, recipient: str, subject: str, html_content: str, 
                   attachments: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Send email with HTML content and optional attachments"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.mail_from
            msg['To'] = recipient
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Log the SMTP request
            start_time = time.time()
            request_id = self.api_logger.log_request(
                api_name="SMTP_Email",
                method="SEND",
                url=f"smtp://{self.smtp_host}:{self.smtp_port}",
                params={
                    "recipient": recipient,
                    "subject": subject,
                    "content_size": len(html_content),
                    "attachments_count": len(attachments) if attachments else 0,
                    "tls_enabled": self.smtp_tls
                }
            )
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_tls:
                    server.starttls()
                
                if self.smtp_user and self.smtp_pass:
                    server.login(self.smtp_user, self.smtp_pass)
                
                server.send_message(msg)
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Log successful email response
            self.api_logger.log_response(
                request_id=request_id,
                api_name="SMTP_Email",
                status_code=250,  # SMTP success code
                response_data={
                    "message": "Email sent successfully",
                    "recipient": recipient,
                    "subject": subject
                },
                duration_ms=duration_ms
            )
            
            logger.info(f"Email sent successfully to {recipient}: {subject}")
            return True
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
            
            # Log error response
            if 'request_id' in locals():
                self.api_logger.log_response(
                    request_id=request_id,
                    api_name="SMTP_Email",
                    status_code=0,
                    duration_ms=duration_ms,
                    error=str(e)
                )
            
            logger.error(f"Failed to send email to {recipient}: {e}")
            return False

    def send_batch_emails(self, email_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send multiple emails in batch"""
        results = {
            "sent": 0,
            "failed": 0,
            "errors": []
        }
        
        for email_data in email_batch:
            try:
                success = self.send_email(**email_data)
                if success:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Failed to send to {email_data.get('recipient', 'unknown')}")
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error sending to {email_data.get('recipient', 'unknown')}: {str(e)}")
        
        logger.info(f"Batch email results: {results['sent']} sent, {results['failed']} failed")
        return results

    def test_connection(self) -> bool:
        """Test SMTP connection"""
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_tls:
                    server.starttls()
                
                if self.smtp_user and self.smtp_pass:
                    server.login(self.smtp_user, self.smtp_pass)
            
            logger.info("SMTP connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False

    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message"""
        try:
            with open(attachment['filepath'], 'rb') as file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
                
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment.get("filename", os.path.basename(attachment["filepath"]))}'
            )
            msg.attach(part)
            
        except Exception as e:
            logger.error(f"Failed to add attachment {attachment.get('filepath')}: {e}")

    def _strftime_filter(self, date_str: str, format_str: str = '%B %d, %Y at %I:%M %p') -> str:
        """Jinja2 filter for date formatting"""
        try:
            if isinstance(date_str, str):
                # Parse ISO format datetime string
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime(format_str)
            return str(date_str)
        except:
            return str(date_str)


class DryRunEmailSender(EmailSender):
    """Email sender for testing that doesn't actually send emails"""
    
    def __init__(self, output_dir: str = "output/emails"):
        # Initialize with dummy SMTP settings
        super().__init__("localhost", 587, "test@test.com", "password")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def send_email(self, recipient: str, subject: str, html_content: str, 
                   attachments: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Save email to file instead of sending"""
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{timestamp}_{safe_subject[:50]}.html"
            
            # Save to file
            output_file = self.output_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"<!-- Email would be sent to: {recipient} -->\n")
                f.write(f"<!-- Subject: {subject} -->\n")
                f.write(html_content)
            
            logger.info(f"DRY RUN: Email saved to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save dry run email: {e}")
            return False

    def send_all_stocks_advisory_email(self, stock_advisories: List[Dict[str, Any]], 
                                     portfolio_data: Dict[str, Any], 
                                     portfolio_metrics: Dict[str, Any],
                                     recipient: str) -> bool:
        logger.info(
            "DRY RUN: Sending all-stocks advisory email (not actually sent, saved to file)"
        )
        """Save consolidated all-stocks advisory email to file instead of sending"""
        try:
            template = self.jinja_env.get_template("all_stocks_advisory.html")
            
            # Prepare template data
            template_data = {
                "date": datetime.now().strftime('%B %d, %Y'),
                "portfolio": portfolio_data,
                "portfolio_metrics": portfolio_metrics,
                "stock_advisories": stock_advisories,
                "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            html_content = template.render(**template_data)
            
            subject = f"📈 Daily Stock Advisory - {len(stock_advisories)} Positions - {datetime.now().strftime('%B %d, %Y')}"
            
            return self.send_email(recipient, subject, html_content)
            
        except Exception as e:
            logger.error(f"Error generating all-stocks advisory email: {e}")
            return False

    def test_connection(self) -> bool:
        """Always return True for dry run"""
        logger.info("DRY RUN: SMTP connection test (simulated)")
        return True
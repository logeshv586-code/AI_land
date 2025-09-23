"""
Notification Service for Real Estate Application

Handles email notifications, in-app notifications, and push notifications
for the agent-mediated communication system.
"""

import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
import logging

from sqlalchemy.orm import Session
from app.models import User, Message, PropertyListing
from app.core.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling various types of notifications"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@realestate.com')
    
    async def notify_new_message(
        self, 
        message: Message, 
        sender: User, 
        recipient: User, 
        property_listing: PropertyListing,
        db: Session
    ):
        """Send notification for new message"""
        
        try:
            # Send email notification
            await self._send_email_notification(
                recipient=recipient,
                subject=f"New message about {property_listing.title}",
                template="new_message",
                context={
                    "sender_name": f"{sender.first_name} {sender.last_name}" if sender.first_name else sender.username,
                    "sender_role": sender.user_role.value.replace('_', ' ').title(),
                    "property_title": property_listing.title,
                    "property_address": property_listing.location.address if property_listing.location else "Unknown",
                    "message_subject": message.subject,
                    "message_preview": message.content[:100] + "..." if len(message.content) > 100 else message.content,
                    "message_url": f"/messages/{message.id}"
                }
            )
            
            # Create in-app notification (could be stored in database)
            await self._create_in_app_notification(
                user_id=recipient.id,
                title="New Message",
                content=f"You have a new message from {sender.username} about {property_listing.title}",
                notification_type="message",
                related_id=message.id,
                db=db
            )
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
    
    async def notify_property_inquiry(
        self,
        property_listing: PropertyListing,
        inquirer: User,
        agent: User,
        message: str,
        db: Session
    ):
        """Send notification for property inquiry"""
        
        try:
            await self._send_email_notification(
                recipient=agent,
                subject=f"New inquiry for {property_listing.title}",
                template="property_inquiry",
                context={
                    "inquirer_name": f"{inquirer.first_name} {inquirer.last_name}" if inquirer.first_name else inquirer.username,
                    "inquirer_role": inquirer.user_role.value.replace('_', ' ').title(),
                    "property_title": property_listing.title,
                    "property_address": property_listing.location.address if property_listing.location else "Unknown",
                    "property_price": f"${property_listing.price:,.2f}",
                    "inquiry_message": message,
                    "property_url": f"/properties/{property_listing.id}"
                }
            )
            
        except Exception as e:
            logger.error(f"Error sending property inquiry notification: {str(e)}")
    
    async def notify_subscription_expiring(
        self,
        user: User,
        days_until_expiry: int,
        db: Session
    ):
        """Send notification for expiring subscription"""
        
        try:
            await self._send_email_notification(
                recipient=user,
                subject=f"Your subscription expires in {days_until_expiry} days",
                template="subscription_expiring",
                context={
                    "user_name": f"{user.first_name} {user.last_name}" if user.first_name else user.username,
                    "days_until_expiry": days_until_expiry,
                    "subscription_plan": user.subscription_plan.value.title(),
                    "renewal_url": "/subscription/renew"
                }
            )
            
        except Exception as e:
            logger.error(f"Error sending subscription expiry notification: {str(e)}")
    
    async def notify_featured_listing_expiring(
        self,
        property_listing: PropertyListing,
        owner: User,
        hours_until_expiry: int,
        db: Session
    ):
        """Send notification for expiring featured listing"""
        
        try:
            await self._send_email_notification(
                recipient=owner,
                subject=f"Featured listing expires in {hours_until_expiry} hours",
                template="featured_listing_expiring",
                context={
                    "user_name": f"{owner.first_name} {owner.last_name}" if owner.first_name else owner.username,
                    "property_title": property_listing.title,
                    "hours_until_expiry": hours_until_expiry,
                    "extend_url": f"/properties/{property_listing.id}/extend-featured"
                }
            )
            
        except Exception as e:
            logger.error(f"Error sending featured listing expiry notification: {str(e)}")
    
    async def _send_email_notification(
        self,
        recipient: User,
        subject: str,
        template: str,
        context: dict
    ):
        """Send email notification using SMTP"""
        
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email notification")
            return
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = recipient.email
            
            # Generate email content based on template
            html_content = self._generate_email_html(template, context)
            text_content = self._generate_email_text(template, context)
            
            # Attach parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent to {recipient.email}")
            
        except Exception as e:
            logger.error(f"Error sending email to {recipient.email}: {str(e)}")
    
    def _generate_email_html(self, template: str, context: dict) -> str:
        """Generate HTML email content"""
        
        if template == "new_message":
            return f"""
            <html>
            <body>
                <h2>New Message Received</h2>
                <p>Hello,</p>
                <p>You have received a new message from <strong>{context['sender_name']}</strong> 
                ({context['sender_role']}) regarding the property:</p>
                
                <div style="border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 5px;">
                    <h3>{context['property_title']}</h3>
                    <p><strong>Address:</strong> {context['property_address']}</p>
                    <p><strong>Subject:</strong> {context['message_subject']}</p>
                    <p><strong>Message Preview:</strong> {context['message_preview']}</p>
                </div>
                
                <p><a href="{context['message_url']}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Full Message</a></p>
                
                <p>Best regards,<br>Real Estate Platform Team</p>
            </body>
            </html>
            """
        
        elif template == "property_inquiry":
            return f"""
            <html>
            <body>
                <h2>New Property Inquiry</h2>
                <p>Hello,</p>
                <p>You have received a new inquiry from <strong>{context['inquirer_name']}</strong> 
                ({context['inquirer_role']}) for your property:</p>
                
                <div style="border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 5px;">
                    <h3>{context['property_title']}</h3>
                    <p><strong>Address:</strong> {context['property_address']}</p>
                    <p><strong>Price:</strong> {context['property_price']}</p>
                    <p><strong>Inquiry:</strong> {context['inquiry_message']}</p>
                </div>
                
                <p><a href="{context['property_url']}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Property</a></p>
                
                <p>Best regards,<br>Real Estate Platform Team</p>
            </body>
            </html>
            """
        
        # Add more templates as needed
        return f"<html><body><p>Notification: {template}</p></body></html>"
    
    def _generate_email_text(self, template: str, context: dict) -> str:
        """Generate plain text email content"""
        
        if template == "new_message":
            return f"""
            New Message Received
            
            Hello,
            
            You have received a new message from {context['sender_name']} ({context['sender_role']}) 
            regarding the property: {context['property_title']} at {context['property_address']}.
            
            Subject: {context['message_subject']}
            Message Preview: {context['message_preview']}
            
            Please log in to view the full message.
            
            Best regards,
            Real Estate Platform Team
            """
        
        elif template == "property_inquiry":
            return f"""
            New Property Inquiry
            
            Hello,
            
            You have received a new inquiry from {context['inquirer_name']} ({context['inquirer_role']}) 
            for your property: {context['property_title']} at {context['property_address']}.
            
            Price: {context['property_price']}
            Inquiry: {context['inquiry_message']}
            
            Please log in to respond to this inquiry.
            
            Best regards,
            Real Estate Platform Team
            """
        
        return f"Notification: {template}"
    
    async def _create_in_app_notification(
        self,
        user_id: int,
        title: str,
        content: str,
        notification_type: str,
        related_id: Optional[int],
        db: Session
    ):
        """Create in-app notification (could be stored in database)"""
        
        # For now, just log the notification
        # In a full implementation, you would store this in a notifications table
        logger.info(f"In-app notification for user {user_id}: {title} - {content}")
        
        # TODO: Implement database storage for in-app notifications
        # notification = InAppNotification(
        #     user_id=user_id,
        #     title=title,
        #     content=content,
        #     notification_type=notification_type,
        #     related_id=related_id,
        #     is_read=False,
        #     created_at=datetime.utcnow()
        # )
        # db.add(notification)
        # db.commit()
    
    async def send_bulk_notifications(
        self,
        users: List[User],
        subject: str,
        template: str,
        context: dict
    ):
        """Send bulk notifications to multiple users"""
        
        tasks = []
        for user in users:
            task = self._send_email_notification(user, subject, template, context)
            tasks.append(task)
        
        # Send all notifications concurrently
        await asyncio.gather(*tasks, return_exceptions=True)

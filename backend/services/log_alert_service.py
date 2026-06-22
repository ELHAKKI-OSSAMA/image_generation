from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import aiohttp
from pydantic import BaseModel

from ..models.log import Log, LogLevel, LogCategory
from ..config import settings

class AlertCondition(BaseModel):
    name: str
    description: str
    level: Optional[LogLevel]
    category: Optional[LogCategory]
    threshold: int
    time_window: int  # in minutes
    cooldown: int  # in minutes
    channels: List[str]  # email, slack, etc.

class AlertState:
    def __init__(self):
        self.last_triggered: Dict[str, datetime] = {}

class LogAlertService:
    def __init__(self, db: Session):
        self.db = db
        self.alert_state = AlertState()
        
        # Configure email
        self.email_conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=settings.USE_CREDENTIALS
        )
        
        # Default alert conditions
        self.alert_conditions = [
            AlertCondition(
                name="High Error Rate",
                description="Error rate exceeds normal threshold",
                level=LogLevel.ERROR,
                threshold=10,
                time_window=5,
                cooldown=15,
                channels=["email", "slack"]
            ),
            AlertCondition(
                name="Critical System Error",
                description="Critical system error detected",
                level=LogLevel.CRITICAL,
                threshold=1,
                time_window=5,
                cooldown=15,
                channels=["email", "slack"]
            ),
            AlertCondition(
                name="Security Alert",
                description="Suspicious security activity detected",
                category=LogCategory.SECURITY,
                threshold=5,
                time_window=5,
                cooldown=15,
                channels=["email", "slack"]
            ),
            AlertCondition(
                name="API Performance",
                description="API response time degradation",
                category=LogCategory.API,
                threshold=1000,  # ms
                time_window=5,
                cooldown=15,
                channels=["slack"]
            )
        ]

    async def check_alert_conditions(self, log: Log) -> List[AlertCondition]:
        """Check if a log entry triggers any alert conditions"""
        triggered_alerts = []
        current_time = datetime.utcnow()

        for condition in self.alert_conditions:
            # Skip if in cooldown period
            if condition.name in self.alert_state.last_triggered:
                cooldown_end = self.alert_state.last_triggered[condition.name] + \
                             timedelta(minutes=condition.cooldown)
                if current_time < cooldown_end:
                    continue

            # Check level and category conditions
            if condition.level and log.level != condition.level:
                continue
            if condition.category and log.category != condition.category:
                continue

            # Check threshold conditions
            time_window_start = current_time - timedelta(minutes=condition.time_window)
            
            count = await self.db.query(Log).filter(
                Log.timestamp >= time_window_start,
                Log.level == log.level if condition.level else True,
                Log.category == log.category if condition.category else True
            ).count()

            if count >= condition.threshold:
                triggered_alerts.append(condition)
                self.alert_state.last_triggered[condition.name] = current_time

        return triggered_alerts

    async def send_email_alert(self, condition: AlertCondition, data: Dict[str, Any]):
        """Send alert via email"""
        message = MessageSchema(
            subject=f"Alert: {condition.name}",
            recipients=[settings.ALERT_EMAIL_RECIPIENT],
            body=f"""
            Alert: {condition.name}
            Description: {condition.description}
            Time: {datetime.utcnow()}
            
            Details:
            {data}
            """,
            subtype="html"
        )

        fm = FastMail(self.email_conf)
        await fm.send_message(message)

    async def send_slack_alert(self, condition: AlertCondition, data: Dict[str, Any]):
        """Send alert via Slack webhook"""
        webhook_url = settings.SLACK_WEBHOOK_URL
        
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 Alert: {condition.name}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Description:* {condition.description}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Time:* {datetime.utcnow()}\n\n*Details:*\n```{data}```"
                    }
                }
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=message) as response:
                if response.status != 200:
                    raise ValueError(f"Failed to send Slack alert: {await response.text()}")

    async def send_alert(self, condition: AlertCondition, data: Dict[str, Any]):
        """Send alert through configured channels"""
        for channel in condition.channels:
            try:
                if channel == "email":
                    await self.send_email_alert(condition, data)
                elif channel == "slack":
                    await self.send_slack_alert(condition, data)
            except Exception as e:
                print(f"Failed to send {channel} alert: {str(e)}")

    async def process_log(self, log: Log):
        """Process a log entry and send alerts if needed"""
        triggered_alerts = await self.check_alert_conditions(log)
        
        for alert in triggered_alerts:
            alert_data = {
                "log_level": log.level,
                "category": log.category,
                "action": log.action,
                "details": log.details,
                "error_stack": log.error_stack if log.error_stack else "N/A"
            }
            
            await self.send_alert(alert, alert_data)

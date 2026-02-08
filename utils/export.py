"""
Export conversations to PDF/JSON
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import json
from datetime import datetime


class ConversationExporter:
    """Export conversations to various formats"""
    
    def export_to_json(self, conversation: dict, messages: list) -> str:
        """Export conversation to JSON"""
        export_data = {
            'conversation': conversation,
            'messages': messages,
            'exported_at': datetime.now().isoformat()
        }
        return json.dumps(export_data, indent=2)
    
    def export_to_pdf(self, conversation: dict, messages: list) -> BytesIO:
        """Export conversation to PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph(f"<b>{conversation['title']}</b>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Metadata
        created = datetime.fromtimestamp(conversation['created_at']).strftime('%Y-%m-%d %H:%M')
        meta = Paragraph(f"Created: {created}", styles['Normal'])
        story.append(meta)
        story.append(Spacer(1, 24))
        
        # Messages
        for msg in messages:
            role = msg['role'].upper()
            content = msg['content']
            timestamp = datetime.fromtimestamp(msg['timestamp']).strftime('%H:%M')
            
            # Role and timestamp
            header = Paragraph(f"<b>{role}</b> ({timestamp})", styles['Heading2'])
            story.append(header)
            
            # Content
            text = Paragraph(content, styles['Normal'])
            story.append(text)
            story.append(Spacer(1, 12))
        
        doc.build(story)
        buffer.seek(0)
        return buffer


exporter = ConversationExporter()

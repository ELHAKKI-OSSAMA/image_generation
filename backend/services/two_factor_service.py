import pyotp
import qrcode
from io import BytesIO
import base64
from uuid import UUID
from typing import List, Dict, Any
import secrets
from sqlalchemy.ext.asyncio import AsyncSession

class TwoFactorService:
    def __init__(self):
        self.issuer = "Admin Panel"
        self._temp_secrets = {}  # Temporary storage for setup phase

    async def generate_setup(self, user_id: UUID, email: str) -> Dict[str, Any]:
        """Generate 2FA setup data including QR code and backup codes"""
        # Generate secret
        secret = pyotp.random_base32()
        
        # Generate TOTP URI
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(email, issuer_name=self.issuer)
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Convert QR code to base64 image
        img_buffer = BytesIO()
        qr.make_image(fill_color="black", back_color="white").save(img_buffer, format='PNG')
        qr_code = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4).upper() for _ in range(8)]
        
        # Store secret temporarily
        self._temp_secrets[str(user_id)] = {
            'secret': secret,
            'backup_codes': backup_codes
        }
        
        return {
            'qr_code': f"data:image/png;base64,{qr_code}",
            'backup_codes': backup_codes
        }

    async def verify_setup(self, user_id: UUID, code: str) -> bool:
        """Verify the 2FA setup code"""
        user_id_str = str(user_id)
        if user_id_str not in self._temp_secrets:
            return False
            
        secret = self._temp_secrets[user_id_str]['secret']
        totp = pyotp.TOTP(secret)
        
        # Verify code
        if not totp.verify(code):
            return False
            
        # Setup successful - can persist the secret and backup codes here
        # For now we'll just remove from temporary storage
        del self._temp_secrets[user_id_str]
        
        return True

    async def verify_code(self, secret: str, code: str) -> bool:
        """Verify a 2FA code"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code)
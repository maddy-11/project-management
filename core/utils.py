from .models import Notification, CustomUser
from typing import List, Optional
import requests
from decouple import config
from decimal import Decimal
from django.core.cache import cache

USD_TO_PKR_STATIC = Decimal('277')

# Optionally set this in your environment for live rates
def get_usd_to_pkr_rate():
    cached_rate = cache.get('usd_to_pkr_rate')
    if cached_rate is not None:
        return Decimal(str(cached_rate))
    api_key = config('EXCHANGE_RATE_API_KEY')
    if api_key:
        try:
            url = f'https://v6.exchangerate-api.com/v6/{api_key}/pair/USD/PKR'
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get('result') == 'success':
                    rate = Decimal(str(data['conversion_rate']))
                    cache.set('usd_to_pkr_rate', str(rate), 60 * 60)  # cache for 1 hour
                    return rate
        except Exception:
            pass
    return USD_TO_PKR_STATIC

def convert_to_pkr(amount, currency, rate=None):
    if currency == 'USD':
        if rate is None:
            rate = get_usd_to_pkr_rate()
        return (Decimal(amount) * rate, True, rate)
    return (Decimal(amount), False, Decimal('1'))

def create_notifications(
    recipients: List[CustomUser],
    message: str,
    notif_type: str = 'info',
    actor: Optional[CustomUser] = None,
    **extra_fields
):
    notifications = [
        Notification(
            recipient=recipient,
            message=message,
            type=notif_type,
            actor=actor,
            **extra_fields
        )
        for recipient in recipients
    ]
    Notification.objects.bulk_create(notifications) 
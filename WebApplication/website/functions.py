from django.conf import settings
import requests


def sendWhatsAppMessage(phoneNumber, message):
  headers = {"Authorization": settings.WHATSAPP_TOKEN}
  payload = {"messaging_product": "whatsapp",
		   "recipient_type": "individual",
		   "to": phoneNumber,
		   "type": "text",
		   "text": {"body": message}
		   }
  reponse =  requests.post(settings.WHATSAPP_URL, headers=headers, json=payload)
  ans = response.json()
  return ans

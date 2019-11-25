from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = 'ACd9655ed09cbdb45c5ac2181ceaca308d'
auth_token = 'b1cab5063ede8ebd41a12a29da06809c'
client = Client(account_sid, auth_token)

message = client.messages \
    .create(
         #body='This is Your Qr Code For Entry And Exit',
         body='Welcome to our Company This is the code for entry and exit',
         media_url=['http://www.simsview.com/img/simslogo.jpg'],
         #media_url=["qrdata/smsimage.png"],
        from_='+12052939343',
        to='+918680854271'
     )

print(message.sid)
print ("Sms Sent Sucessfully")
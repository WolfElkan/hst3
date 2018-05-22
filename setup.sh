echo "Enter PayPal recipient account business email:"
read email
echo "Enter ngrok or other host address as"
echo "00000000.ngrok.io"
read ngrok
echo "Enter or paste MySQL database password:"
read mysql

alpha64=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
secret_key=
for (( i = 0; i < 50; i++ )); do
	while :; do ran=$RANDOM; ((ran < 32760)) && char_num=$(((ran%64)+0)) && break; done 
	# echo $char_num
	char="${alpha64:$char_num:1}"
	secret_key=$secret_key$char
# echo $char
done

touch HST/HST/ignored.py 

echo "SECRET_KEY = '${secret_key}'" >> HST/HST/ignored.py
echo >> HST/HST/ignored.py
echo "PAYPAL_BUSINESS_EMAIL = '${email}'" >> HST/HST/ignored.py
echo >> HST/HST/ignored.py
echo "NGROK_URL = u'${ngrok}'" >> HST/HST/ignored.py
echo >> HST/HST/ignored.py
echo "DB_PASSWORD = '${mysql}'" >> HST/HST/ignored.py
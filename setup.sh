touch .gitignore
echo "*/*.pem" >> .gitignore
echo "*.pyc" >> .gitignore
echo "apps/payment/migrations/*" >> .gitignore
echo "!apps/payment/migrations/__init__.py" >> .gitignore
echo "apps/people/migrations/*"  >> .gitignore
echo "!apps/people/migrations/__init__.py"  >> .gitignore
echo "apps/program/migrations/*" >> .gitignore
echo "!apps/program/migrations/__init__.py" >> .gitignore
echo "apps/radmin/migrations/*"  >> .gitignore
echo "!apps/radmin/migrations/__init__.py"  >> .gitignore
echo "*/*/password.py" >> .gitignore
echo "ignored.py" >> .gitignore

touch HST/ignored.py
alpha64=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/

echo "Enter PayPal recipient account business email:"
read email
echo "Enter host address: (e.g. www.families.hstonline.org)"
read ngrok
echo "Enter MySQL database password: (or leave blank to have one generated)"
read mysql

if [[ $mysql == "" ]]; then 
	for (( i = 0; i < 60; i++ )); do
		while :; do ran=$RANDOM; ((ran < 32760)) && char_num=$(((ran%64)+0)) && break; done 
		char="${alpha64:$char_num:1}"
		mysql=$mysql$char
	done
fi

secret_key=
for (( i = 0; i < 50; i++ )); do
	while :; do ran=$RANDOM; ((ran < 32760)) && char_num=$(((ran%64)+0)) && break; done 
	# echo $char_num
	char="${alpha64:$char_num:1}"
	secret_key=$secret_key$char
# echo $char
done

echo "SECRET_KEY = '${secret_key}'" >> HST/ignored.py
echo >> HST/ignored.py
echo "PAYPAL_BUSINESS_EMAIL = '${email}'" >> HST/ignored.py
echo >> HST/ignored.py
echo "NGROK_URL = u'${ngrok}'" >> HST/ignored.py
echo >> HST/ignored.py
echo "DB_PASSWORD = '${mysql}'" >> HST/ignored.py
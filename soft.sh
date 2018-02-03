# echo "You are about to drop the entire database and recreate it from existing migration files.  \nAre you sure you want to do this?"
# echo "Press Y to continue, or any other key to abort"
# read choice
# if [[ $choice = "Y" ]]; then
	# rm -rf apps/main/migrations
	# mkdir apps/main/migrations
	# touch apps/main/migrations/__init__.py
	# rm -rf apps/program/migrations
	# mkdir apps/program/migrations
	# touch apps/program/migrations/__init__.py
	mysql -u terminal -pterminal -e "DROP DATABASE HST; CREATE DATABASE HST; USE HST;"
	echo 'mysql> DROP DATABASE HST; CREATE DATABASE HST; USE HST;'
	# python manage.py makemigrations
	python manage.py migrate
# else
# 	echo "False Alarm. Sorry, Hawaii."
# fi

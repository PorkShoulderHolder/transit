mkdir $(pwd)/transit/processed_data
mkdir $(pwd)/mta/mta_data
echo "0 5 */2 * * python "$(pwd)"/mta_api/run.py > /dev/null" > crontab.txt
crontab $(pwd)/crontab.txt
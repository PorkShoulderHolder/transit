echo "0 5 */2 * * python "$(pwd)"/mta_api/run.py > /dev/null" > crontab.txt
echo "0 5 */2 * * python "$(pwd)"/
crontab $(pwd)/crontab.txt

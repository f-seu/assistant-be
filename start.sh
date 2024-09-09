unset http_proxy
unset https_proxy
unset socks_proxy
unset ALL_PROXY
unset all_proxy
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897
python manage.py runserver
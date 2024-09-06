git pull --rebase --autostash

cd frontend
npm run build

cd ../backend
python3 main.py
sudo apt-get install git g++
echo "Hello"
cd /app/Stockfish-master/src
make help
make build ARCH=x86-64

sudo apt-get install git g++
echo "Hello"
git clone https://github.com/official-stockfish/Stockfish.git
cd lib/app/Stockfish/src
make build ARCH=x86-64

sudo apt update

echo "creating python virtual environment..."
python3 -m venv vir
echo "activating python environment..."
source vir/bin/activate

echo "installing libraris..."
pip3 install -r requirement.txt

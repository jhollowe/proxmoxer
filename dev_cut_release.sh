
rm -rf build/ dist/ proxmoxer.egg-info/ README.txt

python setup.py sdist bdist_wheel

twine check dist/*

twine upload dist/*

crf_learn -f 4 -p 40 -c 3 template train.data model > train.rst  
crf_test -m model test.data > test.rst


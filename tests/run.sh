# run all tests

for dataset in risawoz ; do
  for test_script in tests/${dataset}/*.py ; do
    echo "running ${test_script}"
    python3 ${test_script} || exit 1
  done
done

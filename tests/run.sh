# run all tests
for dataset in risawoz ; do
  for test_script in tests/${dataset}/*.py ; do
    for setting in ko ; do
      echo "running ${test_script} with setting ${setting}"
      python3 ${test_script} --setting ${setting} || exit 1
    done
  done
done

for dataset in bitod ; do
  for test_script in tests/${dataset}/*.py ; do
    echo "running ${test_script}"
    python3 ${test_script} || exit 1
  done
done

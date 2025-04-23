if [ $# -eq 0 ]; then
  echo "usage: ./generate_problem.sh flag"
fi

python3 generate_system.py $1 && emcc check.c -o check.js -s NO_EXIT_RUNTIME=1 -s EXPORTED_RUNTIME_METHODS=[ccall]

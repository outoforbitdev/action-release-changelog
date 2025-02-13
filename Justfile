app_name := "library-galaxy-map"
port := "1798"
api_port := "1799"

install:
    npm install
    npx husky install
    npx husky init
    echo "npx commitlint --edit \$1 --config ./.linters/config/commitlint.config.js" > .husky/commit-msg
    echo "just lint\njust test" > .husky/pre-commit

build:
    npm run build

test:
    python3 -m unittest discover -v -s ./src

test-coverage:
    python -m coverage run -m unittest discover -s ./src
    python -m coverage report
    rm .coverage

test-coverage-report:
    python -m coverage run -m unittest discover -s ./src
    python -m coverage html
    rm .coverage
    open ./htmlcov/index.html

lint:
    docker run -v $(pwd):/app -v $(pwd)/.linters:/polylint/.linters outoforbitdev/polylint:0.1.0

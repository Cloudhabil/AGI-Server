.RECIPEPREFIX := >
.PHONY: run ideas docs ui-mindmap lint typecheck test check

run:
>python3 loop_agent.py

# Auto-approve first mission (demo)
ideas:
>echo "y" | python3 loop_agent.py

# Quick doc demo (approve, title, body)
docs:
>echo -e "y\ncloudhabil_cli_overview\nThis is an auto-doc.\n" | python3 loop_agent.py

ui-mindmap:
>cd ui/cli-ia-mindmap && npm install && npm run dev

lint:
>flake8 .

typecheck:
>mypy bus_server.py kb.py agent_server.py server tests

test:
>python -m pytest -q

check: lint typecheck test

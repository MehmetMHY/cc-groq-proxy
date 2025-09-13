#!/bin/bash

IMAGE_NAME="claude-code-kimi-groq"
CONTAINER_NAME="kimi-proxy"
PORT="7187"

check_groq_key() {
	if [ -z "$GROQ_API_KEY" ]; then
		echo "❌ GROQ_API_KEY environment variable is not set!"
		echo "Setup and get your Groq API key here: https://console.groq.com/"
		exit 1
	fi
}

build_image() {
	echo "Building Docker image..."
	docker build -t $IMAGE_NAME .
}

get_groq_models() {
	if [ -z "$GROQ_API_KEY" ]; then
		echo "GROQ_API_KEY not set"
		return 1
	fi

	curl -s -H "Authorization: Bearer $GROQ_API_KEY" \
		-H "Content-Type: application/json" \
		"https://api.groq.com/openai/v1/models" |
		jq -r '.data[].id' 2>/dev/null || echo ""
}

select_model_interactive() {
	if [ -n "$MODEL_ARG" ]; then
		return
	fi

	# Check if fzf is available
	if ! command -v fzf &>/dev/null; then
		echo "fzf not found. Please install fzf for interactive model selection."
		echo "Using default model."
		MODEL_ARG="--model moonshotai/kimi-k2-instruct-0905"
		return
	fi

	echo "Fetching available models..."
	local models=$(get_groq_models)

	if [ -z "$models" ]; then
		echo "No models available, using default"
		MODEL_ARG="--model moonshotai/kimi-k2-instruct-0905"
		return
	fi

	# Create model list with DEFAULT at the top
	local model_list=$(printf "DEFAULT (moonshotai/kimi-k2-instruct-0905)\n%s" "$models")

	local selected_model=$(echo "$model_list" | fzf --prompt="Select model: " --reverse)

	if [ $? -ne 0 ] || [ -z "$selected_model" ]; then
		echo "Selection cancelled or no model selected. Exiting."
		exit 1
	elif [ "$selected_model" = "DEFAULT (moonshotai/kimi-k2-instruct-0905)" ]; then
		echo "Selected: DEFAULT"
		MODEL_ARG="--model moonshotai/kimi-k2-instruct-0905"
	else
		echo "Selected: $selected_model"
		MODEL_ARG="--model $selected_model"
	fi
}

select_tokens_interactive() {
	if [ -n "$TOKEN_ARG" ]; then
		return
	fi

	# Check if fzf is available
	if ! command -v fzf &>/dev/null; then
		echo "fzf not found. Using default max tokens."
		TOKEN_ARG="--max-tokens 16384"
		return
	fi

	# Common token limits with DEFAULT at the top - intervals of 1024 from 4096 to 1048576
	local token_options="DEFAULT (16384)"
	for ((i = 4096; i <= 1048576; i += 1024)); do
		token_options="${token_options}
${i}"
	done

	local selected_tokens=$(echo "$token_options" | fzf --prompt="Select max tokens: " --height=10 --reverse)

	if [ $? -ne 0 ] || [ -z "$selected_tokens" ]; then
		echo "Selection cancelled or no tokens selected. Exiting."
		exit 1
	elif [ "$selected_tokens" = "DEFAULT (16384)" ]; then
		echo "Selected: DEFAULT (16384)"
		TOKEN_ARG="--max-tokens 16384"
	else
		echo "Selected: $selected_tokens tokens"
		TOKEN_ARG="--max-tokens $selected_tokens"
	fi
}

run_container() {
	check_groq_key

	if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
		echo "Container $CONTAINER_NAME is already running"
		docker ps -f name=$CONTAINER_NAME
		return
	fi

	select_model_interactive
	select_tokens_interactive

	echo "Starting container..."
	docker run -d \
		--name $CONTAINER_NAME \
		-p $PORT:7187 \
		-e GROQ_API_KEY="$GROQ_API_KEY" \
		$IMAGE_NAME \
		python proxy.py $MODEL_ARG $TOKEN_ARG

	echo "Proxy started on http://localhost:$PORT"
	docker ps -f name=$CONTAINER_NAME
}

stop_container() {
	if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
		echo "Stopping container $CONTAINER_NAME..."
		docker stop $CONTAINER_NAME
		docker rm $CONTAINER_NAME
		echo "Container stopped and removed"
	else
		echo "Container $CONTAINER_NAME is not running"
	fi
}

show_logs() {
	if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
		docker logs $CONTAINER_NAME
	else
		echo "Container $CONTAINER_NAME does not exist"
	fi
}

follow_logs() {
	if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
		echo "Following logs for $CONTAINER_NAME (Ctrl+C to exit)..."
		docker logs -f $CONTAINER_NAME
	else
		echo "Container $CONTAINER_NAME is not running"
	fi
}

show_status() {
	if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
		echo "✅ Container is running:"
		docker ps -f name=$CONTAINER_NAME
		echo ""
		echo "📊 Resource usage:"
		docker stats $CONTAINER_NAME --no-stream
	elif [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
		echo "⏸️ Container exists but is not running"
		docker ps -a -f name=$CONTAINER_NAME
	else
		echo "❌ Container does not exist"
	fi
}

show_help() {
	echo "Usage: $0 [OPTIONS] COMMAND"
	echo ""
	echo "Commands:"
	echo "  build              Build the Docker image"
	echo "  run                Start the proxy container"
	echo "  stop               Stop and remove the container"
	echo "  status             Show container status"
	echo "  logs               Show container logs"
	echo "  follow             Follow container logs (live)"
	echo ""
	echo "Options:"
	echo "  -m, --model MODEL      Specify model to use (for run command)"
	echo "  -t, --max-tokens N     Specify max tokens (for run command)"
	echo "  -h, --help             Show this help"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
	case $1 in
	-m | --model)
		if [ -n "$2" ]; then
			MODEL_ARG="--model $2"
			shift 2
		else
			echo "Error: --model requires a value"
			exit 1
		fi
		;;
	-t | --max-tokens)
		if [ -n "$2" ] && [[ "$2" =~ ^[0-9]+$ ]]; then
			TOKEN_ARG="--max-tokens $2"
			shift 2
		else
			echo "Error: --max-tokens requires a numeric value"
			exit 1
		fi
		;;
	-h | --help)
		show_help
		exit 0
		;;
	build | run | stop | status | logs | follow)
		COMMAND="$1"
		shift
		;;
	--)
		shift
		break
		;;
	-*)
		echo "Unknown option: $1"
		show_help
		exit 1
		;;
	*)
		if [ -z "$COMMAND" ]; then
			COMMAND="$1"
		else
			echo "Unknown argument: $1"
			show_help
			exit 1
		fi
		shift
		;;
	esac
done

# If no command specified, show help
if [ -z "$COMMAND" ]; then
	show_help
	exit 1
fi

# Execute command
case $COMMAND in
build)
	build_image
	;;
run)
	run_container
	;;
stop)
	stop_container
	;;
status)
	show_status
	;;
logs)
	show_logs
	;;
follow)
	follow_logs
	;;
help)
	show_help
	;;
*)
	echo "Unknown command: $COMMAND"
	show_help
	exit 1
	;;
esac

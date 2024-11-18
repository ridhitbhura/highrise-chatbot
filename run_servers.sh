#!/bin/bash

# Wait a moment for processes to clean up
sleep 2

# Start FastAPI server
uvicorn src.api.server:app --reload --port 8000 &
FASTAPI_PID=$!

# Wait for FastAPI to start
sleep 5

# Start Next.js frontend
cd frontend && npm run dev &
NEXTJS_PID=$!

# Handle script termination
trap "kill $FASTAPI_PID $NEXTJS_PID" SIGINT SIGTERM EXIT

# Wait for both processes
wait 
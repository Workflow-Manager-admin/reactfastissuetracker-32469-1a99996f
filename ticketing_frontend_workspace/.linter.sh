#!/bin/bash
cd /home/kavia/workspace/code-generation/reactfastissuetracker-32469-1a99996f/ticketing_frontend_workspace/ticketing_frontend
npm run build
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
   exit 1
fi


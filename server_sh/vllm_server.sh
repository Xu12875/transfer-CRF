#!/bin/bash
eval "$(conda shell.bash hook)"
env_name="LLM-inference"
conda activate $env_name

# export CUDA_VISIBLE_DEVICES=4,5,6,7

vllm serve /data/hf_cache/models/Qwen/Qwen2.5-32B-Instruct --host=127.0.0.1 --port=8030 --api-key="token-abc123"  --tensor-parallel-size 8 --max-model-len 8196 --dtype auto --gpu-memory-utilization 0.8


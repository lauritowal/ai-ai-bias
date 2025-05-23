#!/bin/bash

rm -rf "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results"
echo "Removed leave_one_out_results directory"

cd /home/wombat_share/laurito/ai-ai-bias/merged_run_outputs

# Product products
mkdir -p "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results/products/gpt3_5"
poetry run python process_human_results.py --leave_one_out --output "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results/products/gpt3_5/results" \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Autochthon/gpt3_5/product/experiment_20240516202629.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/janpro/gpt3_5/product/experiment_20240515142440.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Verča/gpt3_5/product/experiment_20240525223901.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/aknah/gpt3_5/product/experiment_20250515212524.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/marta_st/gpt3_5/product/experiment_20250518170033.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Ola_Hadrian/gpt3_5/product/experiment_20250518152455.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Mateusz/gpt3_5/product/experiment_20250520204012.json

mkdir -p "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results/products/gpt4" 
poetry run python process_human_results.py --leave_one_out --output "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results/products/gpt4/results" \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/janpro/gpt4/product/experiment_20240515200804.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Verča/gpt4/product/experiment_20240515112325.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/aknah/gpt4/product/experiment_20250515214801.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/marta_st/gpt4/product/experiment_20250518113604.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Ola_Hadrian/gpt4/product/experiment_20250518161835.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Mateusz/gpt4/product/experiment_20250520205532.json

# Papers
mkdir -p "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results/papers/gpt3_5" 
poetry run python process_human_results.py --leave_one_out --output "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results/papers/gpt3_5/results" \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Autochthon/gpt3_5/paper/experiment_20240516114412.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Verča/gpt3_5/paper/experiment_20240524124933.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/janpro/gpt3_5/paper/experiment_20240516103841.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/jh/gpt3_5/paper/experiment_20250513132659.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/marta_st/gpt3_5/paper/experiment_20250518170626.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/msvana/gpt3_5/paper/experiment_20250514103412.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Mateusz/gpt3_5/paper/experiment_20250520203552.json

mkdir -p "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results/papers/gpt4" 
poetry run python process_human_results.py --leave_one_out --output "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results/papers/gpt4/results" \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Autochthon/gpt4/paper/experiment_20240516144908.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/janpro/gpt4/paper/experiment_20240515225002.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Verča/gpt4/paper/experiment_20240527114201.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/jh/gpt4/paper/experiment_20250513134614.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/marta_st/gpt4/paper/experiment_20250518112905.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/msvana/gpt4/paper/experiment_20250514105220.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Mateusz/gpt4/paper/experiment_20250520205025.json

# Movies
mkdir -p "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results/movies/gpt3_5"
poetry run python process_human_results.py --leave_one_out --output "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results/movies/gpt3_5/results" \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Fran/gpt3_5/movie/experiment_20250209094913.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/hammad/gpt3_5/movie/experiment_20250207170538.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Musa/gpt3_5/movie/experiment_20250208111240.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/fnj/gpt3_5/movie/experiment_20250516175236.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/marta_st/gpt3_5/movie/experiment_20250518170931.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Muaaz/gpt3_5/movie/experiment_20250207190349.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Mateusz/gpt3_5/movie/experiment_20250520200206.json

mkdir -p "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results/movies/gpt4"
poetry run python process_human_results.py --leave_one_out --output "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results/movies/gpt4/results" \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Fran/gpt4/movie/experiment_20250209095054.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/hammad/gpt4/movie/experiment_20250207185657.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Musa/gpt4/movie/experiment_20250208123259.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/fnj/gpt4/movie/experiment_20250516184124.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/marta_st/gpt4/movie/experiment_20250518112015.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Muaaz/gpt4/movie/experiment_20250209145048.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Mateusz/gpt4/movie/experiment_20250520202026.json

# original movie results #
########################################################################################
########################################################################################
########################################################################################

rm -rf "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results"
echo "Removed original_results directory"

# Product products
mkdir -p "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results/products/gpt3_5"
poetry run python process_human_results.py --output "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results/products/gpt3_5/results" \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Autochthon/gpt3_5/product/experiment_20240516202629.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/janpro/gpt3_5/product/experiment_20240515142440.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Verča/gpt3_5/product/experiment_20240525223901.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/aknah/gpt3_5/product/experiment_20250515212524.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/marta_st/gpt3_5/product/experiment_20250518170033.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Ola_Hadrian/gpt3_5/product/experiment_20250518152455.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Mateusz/gpt3_5/product/experiment_20250520204012.json

mkdir -p "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results/products/gpt4" 
poetry run python process_human_results.py --output "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results/products/gpt4/results" \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/janpro/gpt4/product/experiment_20240515200804.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Verča/gpt4/product/experiment_20240515112325.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/aknah/gpt4/product/experiment_20250515214801.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/marta_st/gpt4/product/experiment_20250518113604.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Ola_Hadrian/gpt4/product/experiment_20250518161835.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Mateusz/gpt4/product/experiment_20250520205532.json

# Papers
mkdir -p "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results/papers/gpt3_5" 
poetry run python process_human_results.py --output "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results/papers/gpt3_5/results" \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Autochthon/gpt3_5/paper/experiment_20240516114412.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Verča/gpt3_5/paper/experiment_20240524124933.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/janpro/gpt3_5/paper/experiment_20240516103841.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/jh/gpt3_5/paper/experiment_20250513132659.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/marta_st/gpt3_5/paper/experiment_20250518170626.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/msvana/gpt3_5/paper/experiment_20250514103412.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Mateusz/gpt3_5/paper/experiment_20250520203552.json

mkdir -p "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results/papers/gpt4" 
poetry run python process_human_results.py  --output "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results/papers/gpt4/results" \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Autochthon/gpt4/paper/experiment_20240516144908.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/janpro/gpt4/paper/experiment_20240515225002.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Verča/gpt4/paper/experiment_20240527114201.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/jh/gpt4/paper/experiment_20250513134614.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/marta_st/gpt4/paper/experiment_20250518112905.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/msvana/gpt4/paper/experiment_20250514105220.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Mateusz/gpt4/paper/experiment_20250520205025.json

# Movies
mkdir -p "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results/movies/gpt3_5"
poetry run python process_human_results.py --output "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results/movies/gpt3_5/results" \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Fran/gpt3_5/movie/experiment_20250209094913.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/hammad/gpt3_5/movie/experiment_20250207170538.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Musa/gpt3_5/movie/experiment_20250208111240.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/fnj/gpt3_5/movie/experiment_20250516175236.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/marta_st/gpt3_5/movie/experiment_20250518170931.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Muaaz/gpt3_5/movie/experiment_20250207190349.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Mateusz/gpt3_5/movie/experiment_20250520200206.json

mkdir -p "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results/movies/gpt4"
poetry run python process_human_results.py --output "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results/movies/gpt4/results" \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Fran/gpt4/movie/experiment_20250209095054.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/hammad/gpt4/movie/experiment_20250207185657.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Musa/gpt4/movie/experiment_20250208123259.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/fnj/gpt4/movie/experiment_20250516184124.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/marta_st/gpt4/movie/experiment_20250518112015.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Muaaz/gpt4/movie/experiment_20250209145048.json \
    /home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results/Mateusz/gpt4/movie/experiment_20250520202026.json







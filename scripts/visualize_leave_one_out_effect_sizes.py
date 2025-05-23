import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats

def load_json_file(file_path):
    """Load a JSON file and return its contents."""
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_model_info(data, category_filter=None):
    """Extract model information and win ratios from the data."""
    model_results = {}
    
    for key, value in data.items():
        # Split the key to get the components
        if '---' not in key:
            continue
            
        category, rest = key.split('---', 1)
        
        # Only process items matching the category filter if provided
        if category_filter and category != category_filter:
            continue
            
        # Extract model name from the key
        if '|' in rest:
            parts = rest.split('|')
            for part in parts:
                if 'gpt' in part.lower():
                    model_part = part.strip()
                    model_name = model_part.split('-')[0].strip()  # Extract model name (e.g., gpt3_5, gpt4)
                    
                    # Get the total counts and win ratio
                    total_tallies = value.get('total_tallies', {})
                    total = sum(v for k, v in total_tallies.items() if k != 'Invalid')
                    llm_wins = total_tallies.get('LLM', 0)
                    win_ratio = value.get('llm_win_ratio', 0)  # Changed from avg_llm_win_ratio to llm_win_ratio
                    
                    if model_name not in model_results:
                        model_results[model_name] = {'ratios': [], 'totals': [], 'wins': []}
                    model_results[model_name]['ratios'].append(win_ratio)
                    model_results[model_name]['totals'].append(total)
                    model_results[model_name]['wins'].append(llm_wins)
                    break
    
    # Calculate averages for each model
    results = {}
    for model, data in model_results.items():
        results[model] = {
            'value': np.mean(data['ratios']),
            'size': np.mean(data['totals']),
            'llm_count': np.mean(data['wins'])
        }
    return results

def process_directory(directory_path, category=None):
    """Process all JSON files in a directory and return a dictionary of results."""
    results = {}
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"Directory not found: {directory_path}")
        return results
    
    # Process each model subdirectory
    for model_dir in directory.iterdir():
        if not model_dir.is_dir():
            continue
            
        for file_path in model_dir.glob('*.json'):
            # Extract the name of the person left out from the filename
            person_name = file_path.stem.replace('results_without_', '').strip()
            data = load_json_file(file_path)
            model_results = extract_model_info(data, category)
            
            if model_results:  # Only add if we got results
                if person_name not in results:
                    results[person_name] = {}
                # Update results with data from this model directory
                results[person_name].update(model_results)
    
    return results

def create_results_table(results):
    """Create a pandas DataFrame from the results."""
    if not results:
        return pd.DataFrame()
        
    # Convert results to DataFrame with additional columns for size and llm_count
    data = {
        name: {
            'gpt3_5': results[name].get('gpt3_5', {}).get('value', np.nan),
            'gpt4': results[name].get('gpt4', {}).get('value', np.nan),
            'size_gpt3_5': results[name].get('gpt3_5', {}).get('size', np.nan),
            'size_gpt4': results[name].get('gpt4', {}).get('size', np.nan),
            'llm_count_gpt3_5': results[name].get('gpt3_5', {}).get('llm_count', np.nan),
            'llm_count_gpt4': results[name].get('gpt4', {}).get('llm_count', np.nan),
        }
        for name in results
    }
    df = pd.DataFrame(data).T
    
    # Add average column for values
    df['average'] = df[['gpt3_5', 'gpt4']].mean(axis=1)
    df['size'] = df[['size_gpt3_5', 'size_gpt4']].mean(axis=1)
    df['llm_count'] = df[['llm_count_gpt3_5', 'llm_count_gpt4']].mean(axis=1)
    
    # Calculate mean for each column
    means = df.mean()
    
    # Add mean row to the DataFrame if not already present
    if 'AVERAGE' not in df.index:
        df.loc['AVERAGE'] = means
    
    return df

def compute_ci(p, n):
    """
    Compute confidence interval for a proportion p with sample size n.
    Uses Wilson score interval which works well for small samples and extreme proportions.
    """
    # Wilson score interval
    z = 1.96  # 95% confidence
    denominator = 1 + z**2/n
    center = (p + z**2/(2*n))/denominator
    error = z * np.sqrt(p*(1-p)/n + z**2/(4*n**2))/denominator
    return center - error, center + error

def get_original_results():
    """Load and process original results."""
    # Define paths to original results
    base_dir = "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results"
    
    # Initialize results structure
    results = {
        'movies': {'avg_llm_win_ratio': 0},
        'papers': {'avg_llm_win_ratio': 0},
        'products': {'avg_llm_win_ratio': 0}
    }
    
    # Process movies
    movies_gpt35_path = os.path.join(base_dir, "movies/gpt3_5/results.json")
    movies_gpt4_path = os.path.join(base_dir, "movies/gpt4/results.json")
    movies_gpt35_data = load_json_file(movies_gpt35_path)
    movies_gpt4_data = load_json_file(movies_gpt4_path)
    
    # Get the average win ratio for movies
    movies_gpt35_ratio = movies_gpt35_data["movie---DESCRIPTION-from_title_and_year|gpt3_5---COMPARISON-pick_one|humans"].get("llm_win_ratio", 0)
    movies_gpt4_ratio = movies_gpt4_data["movie---DESCRIPTION-from_title_and_year|gpt4---COMPARISON-pick_one|humans"].get("llm_win_ratio", 0)
    results['movies']['avg_llm_win_ratio'] = np.mean([movies_gpt35_ratio, movies_gpt4_ratio])
    
    # Process papers
    papers_gpt35_path = os.path.join(base_dir, "papers/gpt3_5/results.json")
    papers_gpt4_path = os.path.join(base_dir, "papers/gpt4/results.json")
    papers_gpt35_data = load_json_file(papers_gpt35_path)
    papers_gpt4_data = load_json_file(papers_gpt4_path)
    
    # Get the average win ratio for papers
    papers_gpt35_ratio = papers_gpt35_data["paper---DESCRIPTION-write_xml_paper_abstract_combined|gpt3_5---COMPARISON-pick_one|humans"].get("llm_win_ratio", 0)
    papers_gpt4_ratio = papers_gpt4_data["paper---DESCRIPTION-write_xml_paper_abstract_combined|gpt4---COMPARISON-pick_one|humans"].get("llm_win_ratio", 0)
    results['papers']['avg_llm_win_ratio'] = np.mean([papers_gpt35_ratio, papers_gpt4_ratio])
    
    # Process products
    products_gpt35_path = os.path.join(base_dir, "products/gpt3_5/results.json")
    products_gpt4_path = os.path.join(base_dir, "products/gpt4/results.json")
    products_gpt35_data = load_json_file(products_gpt35_path)
    products_gpt4_data = load_json_file(products_gpt4_path)
    
    # Get the average win ratio for products
    products_gpt35_ratio = products_gpt35_data["product---DESCRIPTION-from_json_details|gpt3_5---COMPARISON-pick_one|humans"].get("llm_win_ratio", 0)
    products_gpt4_ratio = products_gpt4_data["product---DESCRIPTION-from_json_details|gpt4---COMPARISON-pick_one|humans"].get("llm_win_ratio", 0)
    results['products']['avg_llm_win_ratio'] = np.mean([products_gpt35_ratio, products_gpt4_ratio])
    
    return results

def create_category_effect_size_plot(category_df, original_results, category, category_name):
    """Create effect size plot for a specific category."""
    if category_df.empty:
        print(f"No data available for {category_name}")
        return
        
    # Calculate effect sizes
    all_data = []
    # Use the original results directly
    baseline_win_rate = original_results[category]['avg_llm_win_ratio']
    
    for idx in category_df.index:
        if idx == 'AVERAGE':
            continue
            
        # Get the win rate when this participant is left out (averaged across GPT-3.5 and GPT-4)
        leave_one_out_win_rate = category_df.loc[idx, 'average']
        # Calculate how much the win rate changes when this participant is left out
        win_rate_change = leave_one_out_win_rate - baseline_win_rate

        # Get sample size for confidence intervals
        sample_size = category_df.loc[idx, 'size']
        
        # Calculate confidence intervals
        p = leave_one_out_win_rate  # proportion
        n = sample_size  # sample size
        ci_low, ci_high = compute_ci(p, n)
        
        # Adjust confidence intervals to be relative to win rate change
        ci_low_effect = win_rate_change - (leave_one_out_win_rate - ci_low)
        ci_high_effect = ci_high - leave_one_out_win_rate + win_rate_change
        
        all_data.append({
            'Participant': idx,
            'Effect Size': win_rate_change,
            'CI Low': win_rate_change - abs(ci_low_effect),
            'CI High': win_rate_change + abs(ci_high_effect),
            'Original Value': leave_one_out_win_rate  # Store original value for reference
        })
    
    # Convert to dataframe
    effect_df = pd.DataFrame(all_data)
    
    # Sort by effect size
    effect_df = effect_df.sort_values(by='Effect Size')
    
    # Create a unique mapping for participants in this category only
    participants = sorted(effect_df['Participant'].unique())
    participant_map = {name: f"Omitting {i+1}" for i, name in enumerate(participants)}
    
    # Add the unique identifiers to the dataframe
    effect_df['Omitting ID'] = effect_df['Participant'].map(participant_map)
    
    # Save the participant mapping for this category
    with open(f'participant_mapping_{category}.txt', 'w') as f:
        f.write(f"Participant ID mapping for {category_name}:\n")
        for i, name in enumerate(participants):
            f.write(f"Omitting {i+1}: {name}\n")
    
    print(f"Participant mapping for {category_name} saved to participant_mapping_{category}.txt")
    
    # Create figure with more bottom space for annotation
    plt.figure(figsize=(10, max(8, len(effect_df) * 0.5 + 1)))
    
    # Plot each data point
    for i, (_, row) in enumerate(effect_df.iterrows()):
        plt.plot([row['CI Low'], row['CI High']], [i, i], 'k-', alpha=0.7)
        plt.plot([row['Effect Size']], [i], 'ko', markersize=8)
    
    # Add vertical line at zero (no effect)
    plt.axvline(x=0, color='k', linestyle=':', alpha=0.7)
    
    # Add shaded region for small effect sizes (-0.1 to 0.1)
    plt.axvspan(-0.1, 0.1, color='lightgreen', alpha=0.2)
    plt.axvspan(0.1, 0.4, color='lightgreen', alpha=0.1)
    plt.axvspan(-0.4, -0.1, color='lightgreen', alpha=0.1)
    
    # Create y-tick labels with only the Omitting ID
    y_labels = [row['Omitting ID'] for _, row in effect_df.iterrows()]
    
    # Customize plot
    plt.yticks(range(len(effect_df)), y_labels)
    plt.xlabel('Effect size (change in LLM win rate)', fontsize=14)
    plt.grid(axis='x', linestyle='--', alpha=0.3)
    plt.title(f'Effect of Omitting Each Participant on {category_name} LLM Win Rate', fontsize=14)
    
    # Adjust layout with more bottom margin
    plt.tight_layout(rect=[0, 0.1, 1, 0.98])
    
    # Add a note about interpretation with more space below the plot
    plt.figtext(0.5, 0.02, 
                "Positive values indicate higher LLM preference when this participant is excluded.\n"
                "Negative values indicate lower LLM preference when this participant is excluded.", 
                ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.1, "pad":5})
    
    # Save the figure
    plt.savefig(f'leave_one_out_effect_sizes_{category}.png', dpi=300, bbox_inches='tight')
    print(f"Created forest plot for {category_name}: leave_one_out_effect_sizes_{category}.png")

def plot_effect_sizes(movies_df, papers_df, products_df, original_results):
    """Create independent forest plots for each category."""
    
    # Process each category separately
    create_category_effect_size_plot(movies_df, original_results, 'movies', 'Movies')
    create_category_effect_size_plot(papers_df, original_results, 'papers', 'Papers')
    create_category_effect_size_plot(products_df, original_results, 'products', 'Products')

def main():
    # Define base directory
    base_dir = "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results"
    
    # Process movies directory
    movies_dir = os.path.join(base_dir, "movies")
    movies_results = process_directory(movies_dir, "movie")
    movies_df = create_results_table(movies_results)
    
    # Process papers and products from their separate directories
    papers_dir = os.path.join(base_dir, "papers")
    products_dir = os.path.join(base_dir, "products")
    
    papers_results = process_directory(papers_dir, "paper")
    products_results = process_directory(products_dir, "product")
    
    papers_df = create_results_table(papers_results)
    products_df = create_results_table(products_results)
    
    # Get original results
    original_results = get_original_results()
    
    # Create effect size visualization
    plot_effect_sizes(movies_df, papers_df, products_df, original_results,)

if __name__ == "__main__":
    main() 
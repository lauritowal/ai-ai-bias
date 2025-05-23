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

def extract_model_info(data, category_filter=None, target_model=None):
    """Extract model information and win ratios from the data."""
    results = {}
    
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
                    
                    # Skip if not the target model
                    if target_model and model_name != target_model:
                        continue
                    
                    # Get the pre-computed values directly
                    total_tallies = value.get('total_tallies', {})
                    total = total_tallies.get('Human', 0) + total_tallies.get('LLM', 0)  # Valid responses only
                    llm_wins = total_tallies.get('LLM', 0)
                    win_ratio = value.get('llm_win_ratio', 0)
                    
                    # Store the result directly (no need for averaging)
                    results[model_name] = {
                        'value': win_ratio,
                        'size': total,
                        'llm_count': llm_wins
                    }
                    break
    
    return results

def process_directory(directory_path, category=None, target_model=None):
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
            model_results = extract_model_info(data, category, target_model)
            
            if model_results:  # Only add if we got results
                if person_name not in results:
                    results[person_name] = {}
                # Update results with data from this model directory
                results[person_name].update(model_results)
    
    return results

def create_results_table(results, target_model):
    """Create a pandas DataFrame from the results for a specific model."""
    if not results:
        return pd.DataFrame()
        
    # Convert results to DataFrame - each result is already the final value for that participant
    data = {
        name: results[name].get(target_model, {})
        for name in results
        if target_model in results[name]
    }
    
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data).T
    
    # Calculate mean for each column (this is now the mean across leave-one-out scenarios)
    means = df.mean()
    
    # Add mean row to the DataFrame
    if 'AVERAGE' not in df.index:
        df.loc['AVERAGE'] = means
    
    return df

def compute_ci(value, size):
    """
    Compute confidence interval for a proportion using beta distribution.
    Returns the half-widths for the 95% confidence interval.
    """
    alpha = value * size
    beta_ = (1 - value) * size
    a, b = scipy.stats.beta.interval(0.95, alpha, beta_)
    return value - a, b - value


def get_original_results(target_model):
    """Load and process original results for a specific model."""
    # Define paths to original results
    base_dir = "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/original_results"
    
    # Initialize results structure
    results = {
        'movies': {'llm_win_ratio': 0},
        'papers': {'llm_win_ratio': 0},
        'products': {'llm_win_ratio': 0}
    }
    
    # Process each category
    categories = ['movies', 'papers', 'products']
    for category in categories:
        results_path = os.path.join(base_dir, f"{category}/{target_model}/results.json")
        if os.path.exists(results_path):
            data = load_json_file(results_path)
            for key, value in data.items():
                if target_model in key:
                    results[category]['llm_win_ratio'] = value.get('llm_win_ratio', 0)
                    break
    
    return results

def create_category_effect_size_plot(category_df, original_results, category, category_name, model):
    """Create win rate plot showing baseline vs leave-one-out results for a specific category and model."""
    if category_df.empty:
        print(f"No data available for {category_name}")
        return
        
    # Calculate effect sizes
    all_data = []
    # Use the original results directly
    baseline_win_rate = original_results[category]['llm_win_ratio']
    
    for idx in category_df.index:
        if idx == 'AVERAGE':
            continue
            
        # Get the win rate when this participant is left out
        leave_one_out_win_rate = category_df.loc[idx, 'value']
        
        # Get sample size for confidence intervals
        sample_size = category_df.loc[idx, 'size']
        
        # Calculate confidence intervals for the leave-one-out win rate
        p = leave_one_out_win_rate  # proportion
        n = sample_size  # sample size
        ci_low_width, ci_high_width = compute_ci(p, n)
        ci_low = p - ci_low_width
        ci_high = p + ci_high_width
        
        all_data.append({
            'Participant': idx,
            'Baseline Win Rate': baseline_win_rate,
            'Leave One Out Win Rate': leave_one_out_win_rate,
            'CI Low': ci_low,
            'CI High': ci_high,
            'Effect Size': leave_one_out_win_rate - baseline_win_rate  # Keep for reference
        })
    
    # Convert to dataframe
    effect_df = pd.DataFrame(all_data)
    
    # Sort by leave-one-out win rate
    effect_df = effect_df.sort_values(by='Leave One Out Win Rate')
    
    # Create a unique mapping for participants in this category only
    participants = sorted(effect_df['Participant'].unique())
    participant_map = {name: f"Omitting {i+1}" for i, name in enumerate(participants)}
    
    # Add the unique identifiers to the dataframe
    effect_df['Omitting ID'] = effect_df['Participant'].map(participant_map)
    
    # Save the participant mapping for this category
    with open(f'participant_mapping_{category}_{model}.txt', 'w') as f:
        f.write(f"Participant ID mapping for {category_name} ({model.upper()}):\n")
        for i, name in enumerate(participants):
            f.write(f"Omitting {i+1}: {name}\n")
    
    print(f"Participant mapping for {category_name} ({model.upper()}) saved to participant_mapping_{category}_{model}.txt")
    
    # Create figure with more bottom space for annotation
    plt.figure(figsize=(12, max(8, len(effect_df) * 0.5 + 1)))
    
    # Add background shading for different percentage zones from baseline
    # Define the zones (±10%, ±20%, ±30%, etc.) with decreasing opacity
    zone_colors = ['lightblue', 'lightcyan', 'lightgray', 'whitesmoke']
    zone_alphas = [0.3, 0.2, 0.15, 0.1]
    
    for i, (color, alpha) in enumerate(zip(zone_colors, zone_alphas)):
        zone_size = (i + 1) * 0.1  # 0.1, 0.2, 0.3, 0.4
        
        # Add shaded regions for each zone
        plt.axvspan(baseline_win_rate - zone_size, baseline_win_rate + zone_size, 
                   color=color, alpha=alpha, zorder=0)
    
    # Plot each data point
    for i, (_, row) in enumerate(effect_df.iterrows()):
        # Plot confidence interval for leave-one-out rate (using lighter blue)
        plt.plot([row['CI Low'], row['CI High']], [i, i], color='#6699CC', alpha=0.7, linewidth=2)
        
        # Plot baseline as a vertical line segment (using lighter red)
        plt.plot([row['Baseline Win Rate']], [i], color='#CC6666', marker='o', markersize=8, label='Baseline' if i == 0 else '')
        
        # Plot leave-one-out rate (using lighter blue)
        plt.plot([row['Leave One Out Win Rate']], [i], color='#6699CC', marker='o', markersize=8, label='Leave-one-out' if i == 0 else '')
        
        # Connect baseline to leave-one-out with an arrow or line
        plt.plot([row['Baseline Win Rate'], row['Leave One Out Win Rate']], [i, i], 'k-', alpha=0.3, linewidth=1)
    
    # Add vertical reference lines
    plt.axvline(x=0.5, color='gray', linestyle=':', alpha=0.5, label='Equal preference (0.5)')
    plt.axvline(x=baseline_win_rate, color='#CC6666', linestyle='-', alpha=0.8, linewidth=2, label=f'Baseline ({baseline_win_rate:.3f})')
    
    # Add ±10% reference lines from baseline (only show lines that are within reasonable bounds)
    if baseline_win_rate + 0.1 <= 1.0:
        plt.axvline(x=baseline_win_rate + 0.1, color='orange', linestyle='--', alpha=0.7, label=f'+10% ({baseline_win_rate + 0.1:.3f})')
    if baseline_win_rate - 0.1 >= 0.0:
        plt.axvline(x=baseline_win_rate - 0.1, color='orange', linestyle='--', alpha=0.7, label=f'-10% ({baseline_win_rate - 0.1:.3f})')
    
    # Add ±20% reference lines if within bounds
    if baseline_win_rate + 0.2 <= 1.0:
        plt.axvline(x=baseline_win_rate + 0.2, color='purple', linestyle=':', alpha=0.6)
    if baseline_win_rate - 0.2 >= 0.0:
        plt.axvline(x=baseline_win_rate - 0.2, color='purple', linestyle=':', alpha=0.6)
    
    # Create y-tick labels with only the Omitting ID
    y_labels = [row['Omitting ID'] for _, row in effect_df.iterrows()]
    
    # Customize plot
    plt.yticks(range(len(effect_df)), y_labels)
    # plt.xlabel('LLM Win Rate', fontsize=14)  # Removed x-axis label
    plt.xlim(-0.05, 1.05)  # Set reasonable x-axis limits
    
    # Set x-axis ticks at 0.1 intervals and add baseline as a special tick
    regular_ticks = np.arange(0, 1.1, 0.1)
    all_ticks = np.sort(np.append(regular_ticks, baseline_win_rate))
    plt.xticks(all_ticks)
    
    # Color the baseline tick red and bold
    ax = plt.gca()
    tick_labels = []
    for tick in all_ticks:
        if abs(tick - baseline_win_rate) < 0.001:  # This is the baseline tick
            tick_labels.append(f'{baseline_win_rate:.2f}')
        elif abs(tick - baseline_win_rate) < 0.05:  # Too close to baseline, hide it
            tick_labels.append('')
        else:  # Regular tick
            tick_labels.append(f'{tick:.1f}')
    
    ax.set_xticklabels(tick_labels)
    
    # Now color the baseline tick red and bold
    tick_label_objects = ax.get_xticklabels()
    for i, tick in enumerate(all_ticks):
        if abs(tick - baseline_win_rate) < 0.001:  # Found the baseline tick
            tick_label_objects[i].set_color('#CC6666')
            tick_label_objects[i].set_weight('bold')
            break
    
    plt.grid(axis='x', linestyle='--', alpha=0.3)
    plt.title(f'LLM Win Rates When Omitting Each Participant - {category_name} ({model.upper()})', fontsize=14)
    plt.legend(loc='upper right')
    
    # Adjust layout with more bottom margin
    plt.tight_layout(rect=[0, 0.1, 1, 0.98])
    
    # Add a note about interpretation with more space below the plot
    plt.figtext(0.5, 0.02, 
                "Red markers show baseline win rate (all participants). Blue markers show win rate when participant is omitted.\n"
                "Lines connect baseline to leave-one-out values. Blue error bars show 95% confidence intervals.", 
                ha="center", fontsize=10, bbox={"facecolor":"lightblue", "alpha":0.1, "pad":5})
    
    # Save the figure
    plt.savefig(f'leave_one_out_win_rates_{category}_{model}.png', dpi=300, bbox_inches='tight')
    print(f"Created win rate plot for {category_name} ({model.upper()}): leave_one_out_win_rates_{category}_{model}.png")
    plt.close()

def plot_effect_sizes_for_model(movies_df, papers_df, products_df, original_results, model):
    """Create independent win rate plots for each category for a specific model."""
    
    # Process each category separately
    create_category_effect_size_plot(movies_df, original_results, 'movies', 'Movies', model)
    create_category_effect_size_plot(papers_df, original_results, 'papers', 'Papers', model)
    create_category_effect_size_plot(products_df, original_results, 'products', 'Products', model)

def main():
    # Define base directory
    base_dir = "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/leave_one_out_results"
    
    # Process each model separately
    for model in ['gpt3_5', 'gpt4']:
        # Process directories for this model
        movies_results = process_directory(os.path.join(base_dir, "movies"), "movie", model)
        papers_results = process_directory(os.path.join(base_dir, "papers"), "paper", model)
        products_results = process_directory(os.path.join(base_dir, "products"), "product", model)
        
        # Create results tables for this model
        movies_df = create_results_table(movies_results, model)
        papers_df = create_results_table(papers_results, model)
        products_df = create_results_table(products_results, model)
        
        # Get original results for this model
        original_results = get_original_results(model)
        
        # Create effect size visualization for this model
        plot_effect_sizes_for_model(movies_df, papers_df, products_df, original_results, model)

if __name__ == "__main__":
    main() 
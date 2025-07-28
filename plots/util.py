from collections import Counter
import requests
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


def download_relationship_metrics_csv(
    simulation_id,
    data_dir="../data",
    redownload=False,
):
    data_dir = os.path.join(data_dir, simulation_id)
    csv_path = os.path.join(data_dir, f"{simulation_id}.csv")
    if os.path.exists(csv_path) and not redownload:
        print(f"CSV already exists at {csv_path}. Skipping download.")
        return
    url = f"http://localhost:8000/simulation/{simulation_id}/relationship-metrics"
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, f"{simulation_id}-graph-metrics.csv")

    response = requests.get(url)
    if response.status_code == 200:
        with open(csv_path, "wb") as f:
            f.write(response.content)
        print(f"CSV downloaded and saved to {csv_path}")
    else:
        print(f"Failed to download CSV. Status code: {response.status_code}")


def read_relationship_metrics_csv(simulation_id, data_dir="../data"):
    csv_path = os.path.join(
        data_dir, f"{simulation_id}", f"{simulation_id}-graph-metrics.csv"
    )
    if not os.path.exists(csv_path):
        print(f"CSV file {csv_path} does not exist.")
        return None

    df = pd.read_csv(csv_path)
    return df


def get_world_data(simulation_id):
    url = f"http://localhost:8000/simulation/{simulation_id}/world"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"Failed to fetch simulation settings. Status code: {response.status_code}"
        )
        return None


def get_agent_data(simulation_id):
    url = f"http://localhost:8000/simulation/{simulation_id}/agent"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch agent data. Status code: {response.status_code}")
        return None


def generate_plot_title(data, num_agents=12, personality="Neutral Personality"):
    world = data["world_data"]
    width, height = world["size_x"], world["size_y"]

    resources = data["resources_data"]
    total_resources = len(resources)
    required_agents = [r["required_agents"] for r in resources]

    # Count the proportion of required agents: 1-agent, 2-agent, 3-agent
    count = Counter(required_agents)
    agent_dist = [count.get(1, 0), count.get(2, 0), count.get(3, 0)]
    agent_pct = [round(n / total_resources * 100) for n in agent_dist]

    # Create title string
    title = (
        f"{num_agents} Agents, {width} x {height} Grid, {total_resources} Resources "
    )
    title += f"({agent_pct[0]}%, {agent_pct[1]}%, {agent_pct[2]}%), {personality}"

    return title


def download_map(simulation_id):

    download_dir = os.path.abspath(os.path.join("..", "data", simulation_id))
    map_path = f"{download_dir}/{simulation_id}-map.png"
    if os.path.exists(map_path):
        print(f"Map already exists at {map_path}. Skipping download.")
        return

    # Setup Chrome options for headless and automatic downloads
    chrome_options = Options()  # run headless if you want
    chrome_options.add_argument("--headless")
    prefs = {"download.default_directory": download_dir}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(
            f"http://localhost:3000/simulation/{simulation_id}"
        )  # Your React app URL

        # Wait for page load
        time.sleep(2)

        # Find the button by its text or class - adjust selector as needed
        button = driver.find_element(
            By.XPATH, "//button[contains(text(), 'Download Map')]"
        )

        # Click the button
        button.click()

        # Wait for download or rendering to complete
        time.sleep(2)
        print(f"Map downloaded to {map_path}")

    finally:
        driver.quit()

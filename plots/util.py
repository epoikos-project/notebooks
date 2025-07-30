from collections import Counter
import requests
import os
import pandas as pd
import zipfile


def download_relationship_metrics_csv(
    simulation_id,
    data_dir="../data",
    redownload=False,
):
    data_dir = os.path.join(data_dir, simulation_id)
    csv_path = os.path.join(data_dir, f"{simulation_id}-graph-metrics.csv")

    if os.path.exists(csv_path) and not redownload:
        print(f"CSV already exists at {csv_path}. Skipping download.")
        return
    url = f"http://localhost:8000/simulation/{simulation_id}/relationship-metrics"
    os.makedirs(data_dir, exist_ok=True)

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
    title += f"({agent_dist[0]}, {agent_dist[1]}, {agent_dist[2]}), {personality}"

    return title


def download_map_image(simulation_id, tick, data_dir="../data", redownload=False):
    data_dir = os.path.join(data_dir, simulation_id)
    os.makedirs(data_dir, exist_ok=True)
    img_filename = f"{simulation_id}-map-tick-{tick}.png"
    img_path = os.path.join(data_dir, img_filename)
    if os.path.exists(img_path) and not redownload:
        print(f"Image already exists at {img_path}. Skipping download.")
        return
    url = f"http://localhost:3000/maps/{simulation_id}/{img_filename}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(img_path, "wb") as f:
            f.write(response.content)
        print(f"Image downloaded and saved to {img_path}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")


def download_all_maps(simulation_id, data_dir="../data", redownload=False):

    data_dir = os.path.join(data_dir, simulation_id, "maps")
    os.makedirs(data_dir, exist_ok=True)
    zip_filename = f"simulation_{simulation_id}_maps.zip"
    zip_path = os.path.join(data_dir, zip_filename)

    if os.path.exists(zip_path) and not redownload:
        print(f"Zip file already exists at {zip_path}. Skipping download.")
        return

    url = f"http://localhost:3000/api/download-maps?simulationId={simulation_id}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(zip_path, "wb") as f:
            f.write(response.content)
        print(f"All maps downloaded and saved to {zip_path}")

        # Extract the zip
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(data_dir)
        print(f"Maps extracted to {data_dir}")
    else:
        print(f"Failed to download all maps. Status code: {response.status_code}")


def get_action_logs(simulation_id):
    url = f"http://localhost:8000/simulation/{simulation_id}/action-logs"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch action logs. Status code: {response.status_code}")
        return None

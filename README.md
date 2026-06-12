## 📖 Overview

This model simulates how opinions evolve in a population of agents with two attitude dimensions (A and B). Agents interact through a social network, updating their opinions based on:

- **Social Judgment Theory**: Assimilation vs. contrast effects based on opinion distance
- **Dual Dimensions**: Attitudes A and B with configurable importance weights
- **Network Effects**: Connection strength evolves with interactions
- **Confirmation Bias**: Selective exposure to like-minded opinions

## 🚀 Features

- **Real-time Web Interface**: Flask-based dashboard with interactive visualization
- **Dual Attitude Dimensions**: Agents have separate opinions on two correlated issues
- **Dynamic Social Network**: Connections form based on spatial proximity, strengths evolve
- **Interactive Parameters**: Adjust model parameters in real-time
- **Live Statistics**: Real-time charts showing opinion distribution and dynamics
- **Agent Visualization**: Color-coded agents with split semicircles for dual attitudes

## 📊 Model Mechanics

### Opinion Dimensions
- Each agent has `opinion_A` and `opinion_B` (range: -1 to 1)
- Overall opinion: `opinion = opinion_A * importance_A + opinion_B * importance_B`
- Tolerance thresholds control assimilation/contrast behavior

### Interaction Rules
| Parameter | Options | Description |
|-----------|---------|-------------|
| `interaction-order` | importance-based / high agreement / low agreement | Which dimension to discuss |
| `interaction-rule` | central only / with peripheral | Whether second dimension updates |

### Social Judgment Theory
- If |opinion_diff| < tolerance → Assimilation (move closer)
- If |opinion_diff| ≥ tolerance → Contrast (move away)
- Otherwise → No change

### Network Evolution
- Connections form between spatially close agents
- `link-strength` changes with each interaction (+1 for assimilation, -1 for contrast)
- Stronger connections = darker lines in visualization

## 🖥️ Installation
### Prerequisites
- Python 3.10 or higher
- pip package manager

### Clone Repository
git clone https://github.com/yourusername/gaming-polarisation-abm.git

cd gaming-polarisation-abm

## Run Application
python3 app.py

Or  open your browser and navigate to: http://localhost:5000

## 🎮 Explore the model

Click SETUP to initialize the model with 100 agents randomly distributed in the world. You'll see each agent represented as a circle split into two halves: the left half shows Attitude A, the right half shows Attitude B. The overall agent color indicates their combined opinion (pink for support, blue for oppose, grey for neutral). Gray lines between agents represent social connections—darker lines indicate stronger relationships formed through repeated agreement.

Click GO ONCE to run a single time step and observe how agents interact. Each interaction follows social judgment theory: if two agents have similar opinions (difference < tolerance threshold), they move closer together (assimilation). If their opinions are very different (difference ≥ rejectance threshold), they move apart (contrast). The "interaction-order" dropdown lets you choose which attitude dimension agents discuss first: "importance-based" prioritizes the more important dimension, "high agreement" chooses the dimension with smaller opinion gaps, and "low agreement" chooses the dimension with larger gaps. The "interaction-rule" determines whether agents update only the discussed dimension ("central only") or both dimensions ("with peripheral").
## 🙏 Acknowledgments
Social Judgment Theory: Sherif & Hovland (1961)

Jager, Wander, and Frédéric Amblard. “A dynamical perspective on attitude change.” NAACSOS (North American Association for Computational Social and Organizational Science) Conference, Pittsburgh. 2004.


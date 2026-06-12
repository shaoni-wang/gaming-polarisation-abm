from flask import Flask, render_template, jsonify, request
from model.config import Config
from model.simulation import Simulation
import threading
import time
import webbrowser
import socket

app = Flask(__name__)

# Global simulation instance
sim = Simulation(Config())
simulation_thread = None
running = False


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/api/state')
def get_state():
    """Get current simulation state"""
    return jsonify(sim.get_state())


@app.route('/api/step', methods=['POST'])
def step():
    """Execute one simulation step"""
    sim.step()
    return jsonify(sim.get_state())


@app.route('/api/run', methods=['POST'])
def run():
    """Run simulation continuously"""
    global running, simulation_thread
    
    if running:
        return jsonify({'status': 'already running'})
    
    running = True
    
    def run_sim():
        while running and sim.tick < sim.config.max_ticks:
            sim.step()
            time.sleep(0.05)
    
    simulation_thread = threading.Thread(target=run_sim)
    simulation_thread.start()
    
    return jsonify({'status': 'started'})


@app.route('/api/stop', methods=['POST'])
def stop():
    """Stop continuous simulation"""
    global running
    running = False
    return jsonify({'status': 'stopped'})


@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset simulation"""
    global sim, running
    running = False
    if simulation_thread and simulation_thread.is_alive():
        simulation_thread.join(timeout=1.0)
    sim = Simulation(Config())
    return jsonify({'status': 'reset'})


@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """Get or update configuration"""
    if request.method == 'GET':
        return jsonify({
            'num_agents': Config.num_agents,
            'avg_connections': Config.avg_connections,
            'importance_attitude_A': Config.importance_attitude_A,
            'level_of_involvement': Config.level_of_involvement,
            'reinforcement': Config.reinforcement,
            'confirmation_bias': Config.confirmation_bias,
            'influencer_present': Config.influencer_present,
            'interaction_order': Config.interaction_order,
            'interaction_rule': Config.interaction_rule,
            'max_ticks': Config.max_ticks,
            'tolerance_attitude_A': Config.tolerance_attitude_A,
            'tolerance_attitude_B': Config.tolerance_attitude_B
        })
    else:
        data = request.json
        for key, value in data.items():
            if hasattr(Config, key):
                setattr(Config, key, value)
        Config.validate()
        global sim
        sim = Simulation(Config())
        return jsonify({'status': 'config updated'})


def find_available_port(start_port=5000):
    """Find a single available port"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', start_port))
    sock.close()
    if result != 0:
        return start_port
    return start_port + 1


def open_browser(url, delay=1.0):
    """Open browser with delay"""
    def _open():
        time.sleep(delay)
        webbrowser.open(url)
    threading.Thread(target=_open, daemon=True).start()


if __name__ == '__main__':
    port = find_available_port(5000)
    url = f"http://localhost:{port}"
    
    print("=" * 50)
    print("🎮 Gaming Polarisation ABM Simulation")
    print("=" * 50)
    print(f"Configuration:")
    print(f"  - Agents: {Config.num_agents}")
    print(f"  - Avg Connections: {Config.avg_connections}")
    print(f"  - Importance A: {Config.importance_attitude_A}")
    print(f"  - Tolerance A: {Config.tolerance_attitude_A}")
    print(f"  - Tolerance B: {Config.tolerance_attitude_B}")
    print(f"  - Max Ticks: {Config.max_ticks}")
    print(f"  - Interaction Order: {Config.interaction_order}")
    print(f"  - Interaction Rule: {Config.interaction_rule}")
    print("=" * 50)
    print(f"🌐 Server starting at: {url}")
    print("📱 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    open_browser(url)
    app.run(debug=False, host='0.0.0.0', port=port)
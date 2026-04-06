# 🚚 MDVRP Heuristic Optimization

## 📌 Overview

This project implements solutions for the **Multi-Depot Vehicle Routing Problem (MDVRP)** using heuristic search techniques.

### Algorithms Implemented:

* ✅ Greedy Nearest Neighbor (Baseline)
* ✅ A* Search with MST Heuristic (Optimization)

The goal is to minimize total route distance while ensuring all customers are visited.

---

## 📂 Project Structure

```
MDVRP-Heuristic-Optimization/
│
├── src/
│   ├── greedy.py        # Baseline algorithm
│   ├── astar.py         # A* search implementation
│   ├── mst.py           # MST heuristic
│   ├── utils.py         # Utility functions
│
├── tests/
│   ├── test_algorithms.py   # Test runner
│
├── data/
│   ├── sample_data.json     # Sample dataset
│
├── README.md
├── requirements.txt
```

---

## ⚙️ Requirements

* Python 3.8 or higher

Install dependencies:

```
pip install -r requirements.txt
```

---

## ▶️ How to Run the Project

### Step 1: Clone the Repository

```
git clone https://github.com/Parth04Dalvi/MDVRP-Heuristic-Optimization.git
cd MDVRP-Heuristic-Optimization
```

---

### Step 2: Install Dependencies

```
pip install -r requirements.txt
```

---

### Step 3: Run the Test Script

```
python tests/test_algorithms.py
```

---

## 📊 Expected Output

You will see output like:

```
Running Greedy...
Greedy Route: [0, 1, 3, 2, 4, 0]
Greedy Cost: 1250

Running A*...
A* Route: [0, 3, 1, 2, 4, 0]
A* Cost: 980
```

---

## 🧠 How It Works

### 🔹 Greedy Algorithm

* Starts from depot
* Always chooses nearest unvisited customer
* Fast but not optimal

### 🔹 A* Search

* Uses cost function:
  f(n) = g(n) + h(n)
* g(n): distance traveled so far
* h(n): MST cost of remaining customers
* Produces better routes than Greedy

---

## 🧪 Running Custom Data (Optional)

You can modify the dataset in:

```
data/sample_data.json
```

Or edit the `nodes` array in:

```
tests/test_algorithms.py
```

---

## 📈 Future Improvements

* 🚧 Tabu Search (planned)
* 🚧 Multi-depot extension
* 🚧 Performance optimization for large datasets

---


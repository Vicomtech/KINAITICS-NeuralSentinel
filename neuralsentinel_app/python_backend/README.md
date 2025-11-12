# NeuralSentinel

NeuralSentinel Desktop application for managing and evaluating datasets and models.

---

## 🚀 Development Setup

This guide explains how to set up and run the application in development mode. It uses the **Conda** package manager to create a reproducible Python environment.

### Prerequisites

* [Node.js](https://nodejs.org/) (v18 or higher recommended)
* [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
* A `requirements.txt` file containing the necessary Python packages.

---

### 1. Install Node.js Dependencies

First, clone the repository and install all the required `npm` packages.

```bash
git clone [your-repo-url]
cd neuralsentinel
npm install


# 1. Create the new environment
conda create -n neuralsentinel_dev python=3.11

# 2. Activate the environment
conda activate neuralsentinel_dev

# 3. Install all Python dependencies
# (This step may take a while)
pip install -r requirements.txt

# 1. Activate the environment
conda activate neuralsentinel_dev

# 2. Run the application
# (Your prompt should show "(neuralsentinel_dev)")
npm start

# 1. Activate the environment
conda activate neuralsentinel_dev

# 2. Run the application
# (Your prompt should show "(neuralsentinel_dev)")
npm start
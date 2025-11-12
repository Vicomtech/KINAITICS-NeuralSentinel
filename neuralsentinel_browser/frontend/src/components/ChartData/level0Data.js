export const datalvl0 = {
  labels: ['Step 0', 'Step 20', 'Step 40'],
  datasets: [
    {
      label: '226',
      data: [25, 19, 17],
      borderColor: '#440066',
      backgroundColor: '#440066'
    },
    {
      label: '486',
      data: [9, 7, 6],
      borderColor: '#0000ff',
      backgroundColor: '#0000ff'
    },
    {
      label: '28',
      data: [5, 3, 2],
      borderColor: '#004444',
      backgroundColor: '#004444'
    },
    {
      label: '435',
      data: [0, 0, 0],
      borderColor: '#ff0000',
      backgroundColor: '#ff0000'
    }

  ]
}

export const optionslvl0 = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    title: {
      display: true,
      text: 'Neurons associated to class 0',
      font: {
        size: 40,
        family: "'Garamond', 'serif'",
        weight: 800,
      },
      color: 'rgb(3, 37, 100)'
    },
    legend: {
      labels: {
        // This more specific font property overrides the global property
        color: 'rgb(3, 37, 100)',
        font: {
          size: 30
        }
      }
    }
  },
  scales: {
    x: {
      color: 'rgb(3, 37, 100)',
      title: {
        display: true,
        text: 'Steps',
        font: {
          size: 32,
          family: "'Garamond', 'serif'",
          weight: 'bolder',
        },
        color: 'rgb(3, 37, 100)'
      },
      ticks: {
        display: true,
        font: {
          size: 30,
          family: "'Garamond', 'serif'",
          weight: 400,
        },
        color: 'rgb(3, 37, 100)'
      }
    },
    y: {
      suggestedMin: 0,
      suggestedMax: 30,
      color: 'rgb(3, 37, 100)',
      title: {
        display: true,
        text: 'Impact value',
        font: {
          size: 32,
          family: "'Garamond', 'serif'",
          weight: 'bolder',
        },
        color: 'rgb(3, 37, 100)'
      },
      ticks: {
        display: true,
        font: {
          size: 30,
          family: "'Garamond', 'serif'",
          weight: 400,
        },
        color: 'rgb(3, 37, 100)'
      }
    }
  }
}

export const datalvl1 = {
  labels: ['Step 0', 'Step 20', 'Step 40'],
  datasets: [
    {
      label: '254',
      data: [4, 7, 12],
      borderColor: '#0000ff',
      backgroundColor: '#0000ff'
    },
    {
      label: '76',
      data: [0, 0, 1],
      borderColor: '#004444',
      backgroundColor: '#004444'
    },
    {
      label: '347',
      data: [0, 0, 0],
      borderColor: '#ff0000',
      backgroundColor: '#ff0000'
    }

  ]
}

export const optionslvl1 = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    title: {
      display: true,
      text: 'Neurons associated to class 1',
      font: {
        size: 40,
        family: "'Garamond', 'serif'",
        weight: 800,
      },
      color: 'rgb(3, 37, 100)'
    },
    legend: {
      labels: {
        color: 'rgb(3, 37, 100)',
        // This more specific font property overrides the global property
        font: {
          size: 30
        }
      }
    }
  },

  scales: {
    x: {
      color: 'rgb(3, 37, 100)',
      title: {
        display: true,
        text: 'Steps',
        font: {
          size: 32,
          family: "'Garamond', 'serif'",
          weight: 'bolder',
        },
        color: 'rgb(3, 37, 100)'
      },
      ticks: {
        display: true,
        font: {
          size: 30,
          family: "'Garamond', 'serif'",
          weight: 400,
        },
        color: 'rgb(3, 37, 100)'
      }
    },
    y: {
      suggestedMin: 0,
      suggestedMax: 15,
      color: 'rgb(3, 37, 100)',
      title: {
        display: true,
        text: 'Impact value',
        font: {
          size: 32,
          family: "'Garamond', 'serif'",
          weight: 'bolder',
        },
        color: 'rgb(3, 37, 100)'
      },
      ticks: {
        display: true,
        font: {
          size: 30,
          family: "'Garamond', 'serif'",
          weight: 400,
        },
        color: 'rgb(3, 37, 100)'
      }
    }
  }
}
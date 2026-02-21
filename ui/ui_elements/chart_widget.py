import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

def create_pie_chart_widget(data, labels, title='Pie Chart'):
    widget = QWidget()
    layout = QVBoxLayout()
    figure = plt.figure()
    canvas = FigureCanvas(figure)
    layout.addWidget(canvas)
    ax = figure.add_subplot(111)
    ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    ax.set_title(title)
    # ax.legend(labels, loc="best")
    canvas.draw()
    widget.setLayout(layout)
    return widget

def create_bar_graph_widget(data, x_label='X Label', y_label='Y Label', title='Bar Graph'):
    widget = QWidget()
    layout = QVBoxLayout()
    figure = plt.figure()
    canvas = FigureCanvas(figure)
    layout.addWidget(canvas)
    x_labels = data.index.values
    y = data.values
    x = np.arange(len(x_labels))
    ax = figure.add_subplot(111)
    ax.bar(x, y)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=90)  # Rotate x-labels by 90 degrees
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    canvas.draw()
    widget.setLayout(layout)
    return widget
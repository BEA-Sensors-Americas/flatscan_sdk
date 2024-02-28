import sys

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from frontend.gui import Ui_FLATSCAN
import frontend.renderer as renderer
import frontend.signal_handlers as signal_handlers
import frontend.sensor_params as sensor_params
import frontend.api_calls as api_calls
from PyQt6 import QtCore, QtGui, QtWidgets
from pyqtgraph.widgets.RawImageWidget import RawImageWidget


class MainWindow(QMainWindow):
    resized = pyqtSignal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        # self.resized.connect(self.resize_handler)

    def resizeEvent(self, event):
        self.resized.emit()
        return super(MainWindow, self).resizeEvent(event)


def create_qt_app():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_ui = Ui_FLATSCAN()
    main_ui.setupUi(main_window)
    main_window.show()
    return app, main_ui, main_window


def init_model_and_handlers(main_ui, main_window, r):
    api_calls.set_renderer(r)
    main_ui.plot_graph.setRenderer(r)
    params = sensor_params.SensorParams()
    signal_handlers.set_window_and_sensor_params(main_ui, params, main_window, r)
    signal_handlers.initialize_all_push_buttons()
    signal_handlers.initialize_default_text()
    signal_handlers.initialize_connection_settings()
    signal_handlers.register_handlers()
    signal_handlers.start_emergency_message_checker()


def set_up_front_end():
    # Initialize QT application and window
    app, main_ui, main_window = create_qt_app()

    # Initialize renderer for processing MDI data

    r = renderer.Renderer(app, main_ui, main_window, 200, main_ui.plot_graph.size().width(),
                          main_ui.plot_graph.size().height() - main_ui.textBrowser.size().height() - 50, 0, 108)
    # Initialize models for storing GUI state and handling user events
    init_model_and_handlers(main_ui, main_window, r)


    # Starting event loop
    sys.exit(app.exec())
